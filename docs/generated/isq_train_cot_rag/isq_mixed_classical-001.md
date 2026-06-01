# ISQ training COT RAG corpus: isq_mixed_classical shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4603

- task_id: `isqTrain/4603`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `global_phase`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2943`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    Z(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations applied**:
   - `X(q[0])`: Pauli-X gate on q[0]
   - `Z(q[0])`: Pauli-Z gate on q[0]
   - `X(q[0])`: Pauli-X gate on q[0]
   - Measurements on q[0] and q[1]
2. **State evolution**:
   - Initial state: |00>
   - After `X(q[0])`: |10>
   - After `Z(q[0])`: -|10> (Z applies a phase of -1 to |1>)
   - After second `X(q[0])`: -|00>
3. **Final state before measurement**: -|00>. The global phase of -1 does not affect measurement probabilities.
4. **Predicted probability distribution**: {|00>: 1.0}. Since q[1] was never modified, it remains |0>, and the two X gates on q[0] cancel each other out (up to a global phase), returning it to |0>.

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 1.0000.'}

## isqTrain/429

- task_id: `isqTrain/429`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2732`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;

qbit q[2];

procedure main() {
    // Generate random 0-3
    H(q);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits in the state |00>.
2. The `H(q)` operation applies a Hadamard gate to both qubits

### Reference answer

{'predicted_probs': {'0': 0.25, '1': 0.25, '2': 0.25, '3': 0.25}, 'explanation': 'Parametric variant of isqHumanEval/126. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1956

- task_id: `isqTrain/1956`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `intermediate`
- concept_tags: `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `377`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit c[1], q[1];
procedure main() {
    H(c[0]);
    int x = M(c[0]);
    if (x == 1) {
        X(q[0]);
    }
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ code**:
    *   `qbit c[1], q[1];`: Two qubits are declared, `c[0]` and `q[0]`. Initial state is $|00\rangle$ (assuming `c` is higher-order bit or just naming them c=0, q=1 for now, wait, the order depends on measurement).
    *   `H(c[0]);`: Apply Hadamard to `c[0]`. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   `int x = M(c[0]);`: Measure `c[0]`.
        *   If outcome is 0 (prob 0.5), state collapses to $|00\rangle$. `x = 0`.
        *   If outcome is 1 (prob 0.5), state collapses to $|10\rangle$. `x = 1`.
    *   `if (x == 1) { X(q[0]); }`: Conditionally apply X to `q[0]`.
        *   If `x=0`, state remains $|00\rangle$.
        *   If `x=1`, state becomes $|11\rangle$ (since X flips $|0\rangle$ to $|1\rangle$).
    *   `M(q[0]);`: Measure `q[0]`.
        *   If previous outcome was 0, `q[0]` is in $|0\rangle$, measures as 0. Total bitstring: `00`.
        *   If previous outcome was 1, `q[0]` is in $|1\rangle$, measures as 1. Total bitstring: `11`.

2.  **Bitstring ordering in isQ**:
    *   The `--probs` output format says "array indexed by measurement bitstring (earlier measured qubit = higher bit)".
    *   Measurements in order: `M(c[0])` then `M(q[0])`.
    *   So `c[0]` is the higher bit (leftmost in string), `q[0]` is the lower bit (rightmost).
    *   Case 1: `c[0]` measures 0 (bit 1 = 0), `q[0]` measures 0 (bit 0 = 0). Bitstring = `00`.
    *   Case 2: `c[0]` measures 1 (bit 1 = 1), `q[0]` measures 1 (bit 0 = 1). Bitstring = `11`.
    *   Wait, Let me re-analyze the probabilities in the prompt: `Expected measurement probabilities: {'01': 0.5, '11': 0.5}`.
    *   Wait! Why is it `01` and `11`?
    *   Ah! Is `x` measured but not part of the *final* measurement string? Or is it just `q[0]` is higher bit?
    *   Wait, the prompt literally says `Expected measurement probabilities: {'01': 0.5, '11': 0.5}`.
    *   Let me re-evaluate.
    *   If `M(c[0])` is the *first* measurement, and `M(q[0])` is the *second* measurement, they are both measurements.
    *   Wait! Is `x` a classical control, but `c[0]` is a qubit. The program explicitly has `M(c[0])` and `M(q[0])`.
    *   Maybe `c[0]` is the *second* bit in the string? No, "earlier measured qubit = higher bit". So `c[0]` is the higher bit.
    *   Let's check the `if (x == 1)` condition. If `c[0]` is measured, it becomes classical.
    *   Is `c[0]` actually measured at the end? Wait, the `Expected measurement probabilities` has `01` and `11`. This means the higher bit is 0 or 1, and the lower bit is ALWAYS 1!
    *   Wait. Let's trace again.
    *   `H(c[0])` -> $|+\rangle$.
    *   `int x = M(c[0]);` -> measures $c[0]$.
    *   If $x=0$, $c[0]$ is $|0\rangle$.
    *   If $x=1$, $c[0]$ is $|1\rangle$.
    *   If $x==1$, `X(q[0])` is applied.

### Reference answer

{'predicted_probs': {'01': 0.5, '11': 0.5}, 'explanation': 'Coin flip conditional'}

## isqTrain/1957

- task_id: `isqTrain/1957`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `2136`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[1];
qbit a[1];
qbit b[1];
procedure main() {
    H(a[0]); CNOT(a[0], b[0]);
    X(q[0]);
    CNOT(q[0], a[0]);
    H(q[0]);
    int mq = M(q[0]);
    int ma = M(a[0]);
    if (ma == 1) { X(b[0]); }
    if (mq == 1) { Z(b[0]); }
    M(b[0]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step quantum circuit analysis for an isQ program, concluding with the predicted probability distribution of measurement outcomes.

2.  **Analyze the isQ program**:
    *   `qbit q[1]; qbit a[1]; qbit b[1];` (3 qubits total: q, a, b. Initial state $|000\rangle$)
    *   `H(a[0]); CNOT(a[0], b[0]);` -> Entangle `a` and `b` into a Bell state: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)_{a,b}$. `q` is $|0\rangle$. State: $|0\rangle_q \otimes \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)_{a,b} = \frac{1}{\sqrt{2}}(|000\rangle + |011\rangle)$. (Ordering: q, a, b).
    *   `X(q[0]);` -> Flip `q` to $|1\rangle$. State: $\frac{1}{\sqrt{2}}(|100\rangle + |111\rangle)$.
    *   `CNOT(q[0], a[0]);` -> Control `q` (which is $|1\rangle$), target `a`. Flips `a`. State: $\frac{1}{\sqrt{2}}(|110\rangle + |101\rangle)$.
    *   `H(q[0]);` -> Apply H to `q`.
        *   $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   State: $\frac{1}{\sqrt{2}} [ \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_q \otimes (|10\rangle - |01\rangle)_{a,b} ]$ Wait, let's trace carefully.
        *   Current state before H: $|1\rangle_q \otimes \frac{1}{\sqrt{2}}(|10\rangle + |01\rangle)_{a,b}$.
        *   Apply H on `q`: $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_q \otimes \frac{1}{\sqrt{2}}(|10\rangle + |01\rangle)_{a,b}$.
        *   $= \frac{1}{2} (|010\rangle + |001\rangle - |110\rangle - |101\rangle)$.
    *   `int mq = M(q[0]);` -> Measure `q`. Collapses to either $|0\rangle$ or $|1\rangle$ with 50% probability.
        *   If $mq=0$: state is $|010\rangle + |001\rangle$ -> normalized: $\frac{1}{\sqrt{2}}(|010\rangle + |001\rangle)$.
        *   If $mq=1$: state is $|110\rangle + |101\rangle$ -> normalized: $\frac{1}{\sqrt{2}}(|110\rangle + |101\rangle)$.
    *   `int ma = M(a[0]);` -> Measure `a`.
        *   If $mq=0$: `a` is entangled with `b`. Measure `a`:
            *   If $ma=0$, state is $|001\rangle$ (prob 1/4 total). `b` is $|1\rangle$.
            *   If $ma=1$, state is $|010\rangle$ (prob 1/4 total). `b` is $|0\rangle$.
        *   If $mq=1$: Measure `a`:
            *   If $ma=0$, state is $|101\rangle$ (prob 1/4 total). `b` is $|1\rangle$.
            *   If $ma=1$, state is $|110\rangle$ (prob 1/4 total). `b` is $|0\rangle$.
    *   Wait, let's review the classical corrections on `b`.
    *   `if (ma == 1) { X(b[0]); }`
        *   If $mq=0, ma=0$: `b` is $|1\rangle$, apply nothing. `b` stays $|1\rangle$.
        *   If $mq=0, ma=1$: `b` is $|0\rangle$, apply X. `b` becomes $|1\r

### Reference answer

{'predicted_probs': {'000': 0.25, '011': 0.25, '100': 0.25, '111': 0.25}, 'explanation': "Quantum Teleportation with classical feedback. Note: --probs mode reports pre-correction joint distribution over all 3 qubits, not the post-correction state of Bob's qubit alone."}

## isqTrain/2592

- task_id: `isqTrain/2592`
- task_type: `code_equivalence`
- category: `isq_mixed_classical`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5156`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;

qbit q[1]; 

procedure main() {
    // Using a while loop to perform classical setup before quantum operations.
    // e.g., Finding gcd of 15 and 10 to prepare Rz(pi/gcd) state.
    int a = 15;
    int b = 10;
    while (b != 0) {
        int temp = b;
        a = a % b;
        b = temp;
        
        // Swap a and b if needed (mod assigns remainder to a directly)
        // Actually a % b makes a the remainder. So next iter b=a_old%b_old, a=temp
        temp = a;
        a = b;
        b = temp;
    }
    // a is GCD = 5
    // Apply Rz(pi/a)
    X(q[0]);
    H(q[0]);
    // Apply phase
    Rz(pi / a, q[0]);
    H(q[0]);
    M(q[0]);
}

```

Version B:
```isq
import std;

qbit q[1]; 

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Using a while loop to perform classical setup before quantum operations.
    // e.g., Finding gcd of 15 and 10 to prepare Rz(pi/gcd) state.
    int a = 15;
    int b = 10;
    while (b != 0) {
        int temp = b;
        a = a % b;
        b = temp;
        
        // Swap a and b if needed (mod assigns remainder to a directly)
        // Actually a % b makes a the remainder. So next iter b=a_old%b_old, a=temp
        temp = a;
        a = b;
        b = temp;
    }
    // a is GCD = 5
    // Apply Rz(pi/a)
    X(q[0]);
    H(q[0]);
    // Apply phase
    Rz(pi / a, q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Computes the GCD of 15 and 10 (yielding 5) via a classical loop. It then applies the gate sequence `X`, `H`, `Rz(pi/5)`, and `H` to `q[0]` before measuring.
2. **Program B**: Executes the exact same classical logic and quantum gate sequence on `q[0]`.
3. **Key difference**: Program B contains an additional `GPhase(0.0)` gate at the beginning of its main procedure.
4. **Probability equivalence**: The `GPhase(0.0)` gate multiplies the quantum state by a phase factor of $e^{i \cdot 0} = 1$. This acts strictly as an identity operation

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/2590

- task_id: `isqTrain/2590`
- task_type: `code_equivalence`
- category: `isq_mixed_classical`
- difficulty: `difficult`
- concept_tags: `entanglement`, `global_phase`, `isq_syntax_arrays`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `4196`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;

qbit q[1]; // Alice's state
qbit a[1]; // Alice's half of EPR
qbit b[1]; // Bob's half of EPR

procedure main() {
    // Shared EPR
    H(a[0]); CNOT(a[0], b[0]);
    
    // Alice's state to teleport: |1>
    X(q[0]);
    
    // Alice's operations
    CNOT(q[0], a[0]);
    H(q[0]);
    
    // Measurements
    int mq = M(q[0]);
    int ma = M(a[0]);
    
    // Bob's operations conditional
    if (ma == 1) { X(b[0]); }
    if (mq == 1) { Z(b[0]); }
    
    // Bob's measurement
    M(b[0]); // M(b) should evaluate to 1
}

```

vs.

```isq
import std;

qbit q[1]; // Alice's state
qbit a[1]; // Alice's half of EPR
qbit b[1]; // Bob's half of EPR

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Shared EPR
    H(a[0]); CNOT(a[0], b[0]);
    
    // Alice's state to teleport: |1>
    X(q[0]);
    
    // Alice's operations
    CNOT(q[0], a[0]);
    H(q[0]);
    
    // Measurements
    int mq = M(q[0]);
    int ma = M(a[0]);
    
    // Bob's operations conditional
    if (ma == 1) { X(b[0]); }
    if (mq == 1) { Z(b[0]); }
    
    // Bob's measurement
    M(b[0]); // M(b) should evaluate to 1
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** performs the standard quantum teleportation protocol to transfer the state |1> to Bob's qubit. It creates an EPR pair, performs a Bell measurement, and applies conditional X and Z gates to Bob's qubit.
2. **Program B** implements the exact same teleportation circuit but adds the instruction `GPhase(0.0)` before starting the protocol.
3. **The key difference** between the two programs is the presence of `GPhase(0.0)` in Program B.
4. **Measurement probabilities** are exactly the same. `GPhase(0.0)` applies a global phase of $e^{i\cdot 0} = 1$, which mathematically corresponds to an identity operation. Global phase gates do not affect quantum states or measurement probabilities.
5. **Verdict:** Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/446

- task_id: `isqTrain/446`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `796`

### Prompt

用isQ实现implements a variant of the phase_kickback pattern using anc1[1] -> anc1[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program that implements a variant of the phase_kickback pattern.

Analyzing the circuit requirements:
- It implements IPE (Iterative Phase Estimation) for Phase=1/4 of S gate with eigenstate |1>
- Uses qubits: u[1], anc1[3], anc0[1] - total of 5 qubits
- anc1[0] is measured as m1 (Round 1), anc0[0] is measured as m0 (Round 2)
- anc1[1] and anc1[2] are measured but not used in computation

Let me trace through the circuit:

1. Initial state: |00000>
2. X(u[0]): |00010> (u[0] is in position that makes it |1>)
3. H(anc1[0]): (|0> + |1>)/√2 ⊗ |0010>
4. ctrl Z(anc1[0], u[0]): This applies Z to u[0] when anc1[0] is |1>. Since u[0] is |1>, this applies a phase of -1. So: (|0> ⊗ |0010> - |1> ⊗ |0010>)/√2 = (|0> - |1>)/√2 ⊗ |0010>
5. H(anc1[0]): |1> ⊗ |0010>
6. M(anc1[0]) = 1, m1 = 1
7. H(anc0[0]): (|0> + |1>)/√2 ⊗ anc1 state ⊗ |1>_u ⊗ |0>_anc0[0]

Wait, let me reconsider the qubit ordering. The qubits are:
- u[0] - eigenstate
- anc1[0], anc1[1], anc1[2] - ancilla register 1
- anc0[0] - ancilla register 0

Measurements are done in order:
- m1 = M(anc1[0])
- M(anc1[1])
- M(anc1[2])
- m0 = M(anc0[0])

For --probs output, earlier measured qubit = higher bit. So the measurement order is:
- anc1[0] (bit 3, highest)
- anc1[1] (bit 2)
- anc1[2] (bit 1)
- anc0[0] (bit 0, lowest)

predicted output: |1000> with probability 1.0

This means:
- anc1[0] = 1 (bit 3)
- anc1[1] = 0 (bit 2)
- anc1[2] = 0 (bit 1)
- anc0[0] = 0 (bit 0)

Let me trace through again:

Initial: all |0>
After X(u[0]): u[0] = |1>, rest still |0>

Round 1: U^(2^1) = S^2 = Z
- H(anc1[0]): anc1[0] = |+>
- ctrl Z(anc1[0], u[0]): Phase kickback - since u[0] is |1>, eigenvalue of Z is -1, so anc1[0] picks up phase: |+> → |->
- H(anc1[0]): |-> → |1>
- M(anc1[0]) = 1, so m1 = 1

anc1[1] and anc1[2] are never touched, so they stay |0>, measured as 0.

Round 2: U^(2^0) = S
- H(anc0[0]): anc0[0] = |+>
- ctrl S(anc0[0], u[0]): Phase kickback - eigenvalue of S on |1> is i, so phase e^(iπ/2) = e^(iπ/2)
  The anc0[0] picks up this phase when controlling on |1>: (|0> + i|1>)/√2
- Phase correction: since m1=1, apply Rz(-π/2, anc0[0])
  This rotates by -π/2 around Z: (|0> + i*e^(-iπ/2)|1>)/√2 = (|0> + i*(-i)|1>)/√2 = (|0> + |1>)/√2
- H(anc0[0]): (|0> + |1>)/√2 → |0>
- M(anc0[0]) = 0, so m0 = 0

Final

## isqTrain/442

- task_id: `isqTrain/442`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2763`

### Prompt

Implement the following in isQ: implements a variant of the phase_kickback pattern using u[1] -> u[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants me to analyze the phase kickback circuit and provide reasoning.

The circuit implements Iterative Phase Estimation (IPE) to find the phase of the S gate, which is 1/4 (or π/2).

Let me trace through the state evolution:

1. Initial state: |00⟩ for ancilla qubits, |0⟩ for u[0]
2. After X(u[0]): |00⟩⊗|1⟩
3. Round 1: Prepare anc1 in superposition with H, apply controlled-Z (S²=Z)
   - H(anc1): (|0⟩+|1⟩)/√2 ⊗ |0⟩ ⊗ |1⟩
   - ctrl Z(anc1[0], u[0]): This applies Z to u[0] when anc1[0]=|1⟩
   - Since u[0] is |1⟩, Z|1⟩ = -|1⟩
   - Result: (|0⟩⊗|0⟩⊗|1⟩ - |1⟩⊗|0⟩⊗|1⟩)/√2
   - H(anc1[0]): This applies H to anc1[0]
   - The state becomes: |1⟩⊗|0⟩⊗|1⟩ (measuring anc1 gives 1)

Wait, let me be more careful. We have 3 qubits: anc1[0], anc0[0], u[0].

Initial: |000⟩

After X(u[0]): |001⟩

Round 1:
- H(anc1[0]): (|0⟩+|1⟩)/√2 ⊗ |0⟩ ⊗ |1⟩ = (|001⟩ + |101⟩)/√2

- ctrl Z(anc1[0], u[0]): This is CZ between anc1[0] and u[0]
  - When anc1[0]=|1⟩ and u[0]=|1⟩, we apply phase of -1
  - Result: (|001⟩ - |101⟩)/√2

- H(anc1[0]): Apply H to first qubit
  - |0⟩ → (|0⟩+|1⟩)/√2
  - |1⟩ → (|0⟩-|1⟩)/√2
  - So (|001⟩ - |101⟩)/√2 → [(|0⟩+|1⟩)⊗|0⟩⊗|1⟩ - (|0⟩-|1⟩)⊗|0⟩⊗|1⟩]/2
  - = [|001⟩ + |101⟩ - |001⟩ + |101⟩]/2
  - = |101⟩
  
Wait that's wrong. Let me redo:
- State before H(anc1): (|001⟩ - |101⟩)/√2
- Apply H to anc1[0] (first qubit):
  - H|0⟩ = (|0⟩+|1⟩)/√2
  - H|1⟩ = (|0⟩-|1⟩)/√2
  - So the state becomes: [(|0⟩+|1⟩)⊗|01⟩ - (|0⟩-|1⟩)⊗|01⟩]/2
  - = [|001⟩ + |101⟩ - |001⟩ + |101⟩]/2
  - = 2|101⟩/2 = |101⟩

Hmm, that gives anc1[0] = 1.

Actually wait, I need to think about this more carefully. The CZ gate applies a Z to the target when control is |1⟩. But Z|1⟩ = -|1⟩, so we get a phase of -1.

So m1 = M(anc1[0]) = 1 with probability 1.

Round 2:
State after Round 1: |101⟩ (but anc1 is measured, so effectively we have |01⟩ for anc0 and u[0])

- H(anc0[0]): (|0⟩+|1⟩)/√2 ⊗ |1⟩ = (|01⟩ + |11⟩)/√2

- ctrl S(anc0[0], u[0]): When anc0[0]=|1⟩ and u[0]=|1⟩, apply S to u[0]
  - S|1⟩ = i|1⟩
  - Result: (|01⟩ + i|11⟩)/√2

- Phase correction: m1 = 1, so apply Rz(-π/2) to anc0[0]
  - Rz(-π/2)|0⟩ = |0⟩ (no phase change)
  - Rz(-π/2)|1⟩ = e^{-i(-π/2)/2}|1⟩ = e^{iπ/4}|1⟩...

## isqTrain/443

- task_id: `isqTrain/443`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3`

### Prompt

用isQ实现implements a variant of the phase_kickback pattern using anc1[1] -> anc1[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this circuit carefully.

The circuit implements Iterative Phase Estimation (IPE) for the S gate with eigenstate |1>. The S gate has eigenvalue $e^{i\pi/2} = i$, so the phase is $\phi = 1/4$.

**Goal**: Implement phase kickback using IPE to estimate phase 1/4 of the S gate.

**Qubits**: 
- `u[1]`: eigenstate qubit (initialized to |1>)
- `anc1[2]`: ancilla register (only anc1[0] is used for measurement)
- `anc0[1]`: ancilla qubit

3 qubits measured: anc1[0], anc1[1], anc0[0]

**Step-by-step evolution**:

Initial state: |000> (anc1[0], anc1[1], anc0[0]) ⊗ |0> (u[0])

1. X(u[0]): State becomes |000>|1>

2. **Round 1**: 
   - H(anc1[0]): (|0>+|1>)|00>|1> / √2
   - ctrl Z(anc1[0], u[0]): Since u[0]=|1>, this applies Z to u[0] controlled by anc1[0]. When anc1[0]=|1>, Z|1>=-|1>. So state becomes (|0>|1> - |1>|1>)/√2 ⊗ |00>... wait, let me be more careful.

Actually, let me track all qubits. The order is anc1[0], anc1[1], anc0[0], u[0].

Initial: |0,0,0,0>

X(u[0]): |0,0,0,1>

H(anc1[0]): (|0,0,0,1> + |1,0,0,1>)/√2

ctrl Z(anc1[0], u[0]): When anc1[0]=1 and u[0]=1, apply Z. Z|1> = -|1>.
State: (|0,0,0,1> - |1,0,0,1>)/√2

H(anc1[0]): This is H on the first qubit. The first qubit is in state (|0>-|1>)/√2 = |->. H|-> = |1>.
So anc1[0] becomes |1>.
State: |1,0,0,1>

M(anc1[0]) = 1 (m1 = 1)
M(anc1[1]) = 0

State after measurement: |1,0,0,1>

3. **Round 2**:
   - H(anc0[0]): State becomes (|1,0,0,1> + |1,0,1,1>)/√2 ... wait, anc0[0] is the third qubit (index 2 in the 4-qubit system).
   
   Actually, H on anc0[0]: |1,0,0,1> → |1,0>(|0>+|1>)/√2 ⊗ |1> = (|1001> + |1011>)/√2
   
   - ctrl S(anc0[0], u[0]): When anc0[0]=1 and u[0]=1, apply S. S|1> = i|1>.
   State: (|1001> + i|1011>)/√2 = (|1,0,0,1> + i|1,0,1,1>)/√2

   - Since m1=1, apply Rz(-π/2, anc0[0]): Rz(-π/2) on anc0[0] adds phase -π/2 when anc0[0]=|1>.
   State: (|1,0,0,1> + i·e^{-iπ/2}|1,0,1,1>)/√2 = (|1,0,0,1> + i·(-i)|1,0,1,1>)/√2 = (|1,0,0,1> + |1,0,1,1>)/√2

   Wait, let me recalculate. Rz(-π/2)|0> = |0> and Rz(-π/2)|1> = e^{-iπ/2}|1> = -i|1>.

   So state becomes: (|1001> + i·(-i)|1011>)/√2 = (|1001> + (i·(-i))|1011>)/√2 = (|100

## isqTrain/427

- task_id: `isqTrain/427`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1074`

### Prompt

Implement a quantum circuit in isQ: implements a compact variant of the gate_decomposition pattern using q[2] -> q[1]. The circuit should use a reduced qubit register.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Generate a random bit (0 or 1) with equal probability using a minimal single-qubit circuit.
2. Uses 1 qubit (q[0]) in a 1-element register, which is measured at the end.
3. State evolution: |0> → H → (|0> + |1>)/√2 = |+>
4. Measurement yields |0> or |1> each with probability 0.5, as the |+> state has equal amplitude squared for both basis states.

# ISQ training COT RAG corpus: quantum_algorithms shard 120

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/939

- task_id: `isqTrain/939`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `528`

### Prompt

Help me write isQ code that implements the reversible_logic pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The circuit implements a controlled-swap operation (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) using an alternative decomposition where CNOT is replaced by H-CZ-H.

**Goal**: Implement a controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) gate on qubits q[1] and q[2], controlled by q[0], using the H-CZ-H decomposition for CNOT gates.

**Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.

**Initial state**: |000⟩

**Step-by-step evolution**:

1. X(q[0]); X(q[1]); → |110⟩ (q[0]=1, q[1]=1, q[2]=0)

2. The swap operation (three-CNOT decomposition) is applied with q[0] as control. Let me trace through the swap_gate procedure:

The swap_gate uses CNOT → H CZ H decomposition:
- CNOT(a, b) = H(b) → CZ(a, b) → H(b)

Standard swap (three-CNOT decomposition) decomposition:
- CNOT(a, b)
- CNOT(b, a)
- CNOT(a, b)

With H-CZ-H substitution:
- H(b) CZ(a, b) H(b)  [first CNOT]
- H(a) CZ(b, a) H(a)  [second CNOT]
- H(b) CZ(a, b) H(b)  [third CNOT]

Starting state: |110⟩ (when controlled, we consider the case where control q[0]=1)

Wait, this is a controlled-swap (three-CNOT decomposition), so q[0] controls whether the swap happens. Since q[0]=|1⟩, the swap (three-CNOT decomposition) will be applied to q[1] and q[2].

Initial state: |110⟩

First CNOT(q[1], q[2]) = H(q[2]) CZ(q[1], q[2]) H(q[2]):
- |110⟩ → H(q[2]) on |110⟩ = |110⟩ (q[2] is |0⟩, H|0⟩=|+⟩ but we need to track... actually let me be more careful)

Wait, the initial state is |110⟩ meaning q[0]=1, q[1]=1, q[2]=0.

H(q[2]): |0⟩ → |+⟩, so state becomes |11+⟩ = |11⟩⊗(|0⟩+|1⟩)/√2 = (|110⟩+|111⟩)/√2

CZ(q[1], q[2]): applies Z to q[2] when q[1]=1. Since q[1]=1, Z is applied to q[2]:
- |110⟩ → |110⟩ (Z|0⟩=|0⟩)
- |111⟩ → -|111⟩ (Z|1⟩=-|1⟩)
State: (|110⟩-|111⟩)/√2 = |11⟩⊗(|0⟩-|1⟩)/√2 = |11-⟩

H(q[2]): |11-⟩ → |110⟩... wait let me recalculate.

|0⟩-|1⟩)/√2 = H|1⟩, so H(|0⟩-|1⟩)/√2 = |1⟩
State becomes |111⟩

So first CNOT(q[1], q[2]) maps |110⟩ → |111⟩. That's correct since CNOT(1,2) with q[1]=1 flips q[2]: |0⟩→|1⟩.

Second CNOT(q[2], q[1]) = H(q[1]) CZ(q[2], q[1]) H(q[1]):
- |111⟩ → H(q[1]): q[1] is |1⟩, H|1⟩=|−⟩
  State: |1⟩⊗(|1⟩-|0⟩)... wait, let me be careful with ordering.

State is |q[0]q[1]q[2]⟩ = |111⟩

H(q[1]): q[1]=|1⟩ → (|0⟩-|1⟩)/√2
State: (|101⟩-|111⟩)/√2

CZ(q[2], q[1]): Z on q[1] when q[2]=1
- |101⟩ → -|101⟩ (q[2]=1, Z on q[1] which is |0⟩... wait, Z|0⟩=|0⟩)
Actually CZ applies Z to target when control is |1⟩. Here control is q[2] and target is q[1].

For |101⟩: q[2]=1, so Z applied to q[1]. q[1]=|0⟩, Z|0⟩=|0⟩, so |101

## isqTrain/2567

- task_id: `isqTrain/2567`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `global_phase`, `isq_syntax_arrays`, `isq_syntax_procedures`, `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2892`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;

qbit q[2];

procedure my_oracle() {
    X(q[1]);
    CZ(q[0], q[1]);
    X(q[1]);
}

procedure diffuser() {
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
}

procedure main() {
    H(q[0]); H(q[1]);
    my_oracle();
    diffuser();
    M(q[0]); M(q[1]);
}

```

vs.

```isq
import std;

qbit q[2];

procedure my_oracle() {
    X(q[1]);
    CZ(q[0], q[1]);
    X(q[1]);
}

procedure diffuser() {
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
}

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]); H(q[1]);
    my_oracle();
    diffuser();
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes two qubits to |00>, applies Hadamard gates to create an equal superposition, and then applies an oracle and a Grover diffuser. The oracle flips the phase of the |10> state, and the diffuser amplifies its amplitude, resulting in a final state of |10> (100% measurement probability for |10>).
2. **Program B** performs the exact same initialization, superposition, oracle, and diffuser operations on the qubits.
3. The key difference is the addition of the `GPhase(0.0)` operation at the beginning of Program B's main procedure.
4. The measurement probability distributions are identical. `GPhase(0.0)` applies a global phase factor of $e^{i0} = 1$, which is mathematically equivalent to the identity matrix and has no effect on the quantum state or measurement outcomes.
5. Verdict: Yes, the programs are equivalent.

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/978

- task_id: `isqTrain/978`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4062`

### Prompt

用isQ实现implements the lie_trotter pattern with modified rotation parameters (num_pi2s_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a "Reasoning" section explaining an isQ program.
    *   Goal: Implement `lie_trotter` with modified rotation parameters (num_pi2s_to_pi3, i.e., $\pi/3$ instead of $\pi/2$ for Rx in the YY term).
    *   Circuit: Start with |10>, apply ZZ, XX, YY Trotter steps, measure.
    *   Constraints: Start with "## Reasoning", no code blocks, 3-8 lines (up to 15 for complex), concise Dirac notation.

2.  **Analyze the Circuit (circuit implementation):**
    *   **Qubits:** 2 ($q_0, q_1$)
    *   **Initial State:** $|10\rangle$
    *   **Step 1 (ZZ):** CNOT, Rz(0.3926...), CNOT. The angle $0.3926... \approx \pi/8$. This applies a $ZZ$ rotation of $t = \pi/16$.
    *   **Step 2 (XX):** H, H, CNOT, Rz(0.3926...), CNOT, H, H. This applies an $XX$ rotation of $t = \pi/16$.
    *   **Step 3 (YY):** The problem mentions "modified rotation parameters (num_pi2s_to_pi3)". In the implementation, the Rx gates use `1.04719755119660490`, which is exactly $\pi/3$.
        *   Normally, to map $Y \to Z$ for a $ZZ$-type simulation of $YY$, one uses $Rx(\pi/2)$ (or $Rx(-\pi/2)$).
        *   Here, $Rx(\pi/3)$ is used instead of $\pi/2$. This is the "modified" part.
    *   **Final State & Probabilities:**
        *   Let's trace the evolution conceptually. The state rotates in the XX, YY, ZZ subspaces.
        *   Initial: $|10\rangle$.
        *   The rotations mix the states.
        *   The resulting probabilities should be given: $P(00) \approx 0.0071$, $P(01) \approx 0.1122$, $P(10) \approx 0.8735$, $P(11) \approx 0.0071$.
        *   The state is mostly $|10\rangle$ but leaks into $|01\rangle$.

3.  **Draft the Reasoning:**
    *   *Goal:* Implement a Lie-Trotter step for the Heisenberg model (XX+YY+ZZ) with modified basis rotations ($Rx(\pi/3)$ instead of $\pi/2$).
    *   *Qubits:* 2.
    *   *Evolution:*
        *   Start: $|10\rangle$.
        *   ZZ term ($R_z(\pi/8)$): $|10\rangle \to e^{-i\pi/32}|10\rangle$.
        *   XX term ($HR_z(\pi/8)H$): The $XX$ rotation swaps amplitude between $|10\rangle$ and $|01\rangle$. $|10\rangle \to \cos(\pi/32)|10\rangle - i \sin(\pi/32)|01\rangle$.
        *   YY term: $Rx(\pi/3) CNOT Rz(\pi/8) CNOT Rx(-\pi/3)$. Since the $Rx$ angle is not $\pi/2$, this is a faulty/imperfect YY rotation.
    *   *Probabilities:* The specific rotation angles result in constructive/destructive interference yielding the specified measurement outcomes.

4.  **Refine Reasoning for Conciseness and Constraints:**
    *   Constraint: "Be concise: 3-8 lines for simple circuits, up to 15 for complex ones."
    *   Constraint: Use Dirac notation.

    *Draft:*
    ## Reasoning
    This circuit simulates a single Trotter step for the Heisenberg Hamiltonian ($H = XX + YY + ZZ$) using 2 qubits, with a modified $R_x(\pi/3)$ rotation for the $YY$ term instead of the standard $\pi/2$.
    Starting in $|10\rangle$, the $ZZ$ term applies a phase, leaving the state as $|10\rangle$ (up to global phase).
    The $XX$ term (Hadamard conjugation) rotates between $|10\rangle$ and $|01\rangle$, creating a small superposition $\alpha|10\rangle

## isqTrain/1895

- task_id: `isqTrain/1895`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `superposition`
- source: `isq_train_cot`
- dataset_index: `915`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    H(q[0]);
    ctrl Rz(-pi/2.0, q[0], q[1]);
    H(q[1]);
    ctrl Rz(-pi/4.0, q[0], q[2]);
    ctrl Rz(-pi/2.0, q[1], q[2]);
    H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The circuit operates on 3 qubits q[0], q[1], q[2], all initialized to |0>.

Let me track the state through each gate:

1. Initial state: |000>

2. H(q[0]); H(q[1]); H(q[2]);
   Each qubit gets H applied:
   H|0> = |+> = (|0> + |1>)/√2
   State: |+++> = (|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)/2√2

3. H(q[0]);
   H|+> = |0>
   State: |0++> = (|000> + |001> + |010> + |011>)/2

4. ctrl Rz(-π/2, q[0], q[1]);
   Since q[0] is |0>, the controlled-Rz does nothing.
   State unchanged: (|000> + |001> + |010> + |011>)/2

5. H(q[1]);
   H on q[1]: |0++> → ... Let me think more carefully.
   
   State = |0> ⊗ (|00> + |01> + |10> + |11>)/2 = |0> ⊗ |++>
   
   H(q[1]): H on qubit 1 of |0>⊗|++> 
   = |0> ⊗ H|+> ⊗ |+>
   = |0> ⊗ |0> ⊗ |+>
   = |00+> = (|000> + |001>)/√2

6. ctrl Rz(-π/4, q[0], q[2]);
   Since q[0] is |0>, controlled-Rz does nothing.
   State unchanged: (|000> + |001>)/√2

7. ctrl Rz(-π/2, q[1], q[2]);
   Since q[1] is |0>, controlled-Rz does nothing.
   State unchanged: (|000> + |001>)/√2

8. H(q[2]);
   H on q[2]: 
   H(|000> + |001>)/√2 = (|000> + |001>)/√2 after applying H to q[2]
   = (|00>⊗H|0> + |00>⊗H|1>)/√2
   = (|00>⊗|+> + |00>⊗|->)/√2
   = |00> ⊗ (|+> + |->)/√2
   = |00> ⊗ |0>
   = |000>

So the final state is |000>, and the measurement outcome is 000 with probability 1.0.

This makes sense - this is essentially a quantum Fourier transform (QFT) or inverse QFT circuit applied to |+++> followed by measurement, which should give |000>.

Wait, let me reconsider. The circuit structure looks like it could be an inverse QFT. Let me verify:

The QFT on n qubits applies:
- For qubit 0: H, then controlled Rz(π/2), Rz(π/4), etc.
- For qubit 1: H, then controlled Rz(π/2), etc.

But here we have Rz with negative angles, and the order of operations... Let me check if this is the inverse QFT.

Actually, the structure here is:
1. H on all three qubits: creates |+++>
2. Then apply what looks like inverse QFT

If we start with |+++> which is a superposition of all basis states with equal amplitudes, and apply inverse QFT, we should get |000>.

Wait, let me reconsider. |+++> = H⊗3|000>. The QFT of |000> is |000> (up to normalization). So if we have |+++> and apply inverse QFT... 

Actually, let me just verify my step-by-step calculation is correct.

Step 1: |000>
Step 2: H⊗3|000> = |+++> = 1/(2√2) Σ_{x∈{0,1}^3} |x>
Step 3: H(q[0]): Since q[0] is in |+>, H|+> = |0>
State: |0>⊗|++> = 1/2(|000>+|001>+|010>+|011>)

Step 4: ctrl Rz(-π/2, q[0], q[1]): q[0]=|0>, so no

### Reference answer

{'predicted_probs': {'000': 1.0}, 'explanation': '3-qubit IQFT on uniform superposition (H|000⟩). IQFT(QFT(|000⟩)) = |000⟩ with P = 1.0. No SWAP needed: isQ processes q[0]→q[2] directly.'}

## isqTrain/1150

- task_id: `isqTrain/1150`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `data_encoding_qml`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1361`

### Prompt

Create an isQ quantum circuit that implements the data_encoding pattern with modified rotation parameters (num_pi4_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. The goal is to implement a data encoding pattern (Z feature map) with modified rotation parameters.

2. We have 2 qubits q[0] and q[1], both are measured.

3. Step-by-step evolution:
   - Initial state: |00⟩
   - After H(q[0]) H(q[1]): |++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
   - After Rz(1.04719755119660, q[0]): Rz applies phase rotation. Rz(θ) = [[1,0],[0,e^(iθ)]]
     - This is approximately π/3 (since π/3 ≈ 1.0472)
     - |00⟩ → |00⟩, |01⟩ → |01⟩, |10⟩ → e^(iπ/3)|10⟩, |11⟩ → e^(iπ/3)|11⟩
     - State: (1/2)(|00⟩ + |01⟩ + e^(iπ/3)|10⟩ + e^(iπ/3)|11⟩)
   - After Rz(1.57079632679490, q[1]): This is π/2
     - |00⟩ → |00⟩, |01⟩ → e^(iπ/2)|01⟩ = i|01⟩, |10⟩ → e^(iπ/3)|10⟩, |11⟩ → e^(iπ/3)·i|11⟩
     - State: (1/2)(|00⟩ + i|01⟩ + e^(iπ/3)|10⟩ + i·e^(iπ/3)|11⟩)
   - After H(q[0]) H(q[1]): Convert phase encoding back to amplitude encoding
     - Need to apply H to both qubits

Let me be more careful. After the Rz rotations, the state is:
|ψ⟩ = (1/2)(|00⟩ + i|01⟩ + e^(iπ/3)|10⟩ + i·e^(iπ/3)|11⟩)

Let me factor this:
= (1/2)(|0⟩(1+i|1⟩·... wait, let me be more careful.

Actually, Rz on q[0] means if q[0] is |1⟩, multiply by e^(iθ).
Rz on q[1] means if q[1] is |1⟩, multiply by e^(iθ).

After Rz(π/3, q[0]) and Rz(π/2, q[1]) on |++⟩:

The state is:
|ψ⟩ = (1/2) Σ_{a,b ∈ {0,1}} e^(ia·π/3) · e^(ib·π/2) |ab⟩

= (1/2)(|00⟩ + i|01⟩ + e^(iπ/3)|10⟩ + i·e^(iπ/3)|11⟩)

Now applying H⊗H:
H|0⟩ = |+⟩, H|1⟩ = |-⟩

For each qubit:
- q[0]: coefficient structure: 1 for |0⟩, e^(iπ/3) for |1⟩ → H gives (1+e^(iπ/3))|+⟩ component and (1-e^(iπ/3))|-⟩ component... this gets complicated.

Let me just compute the amplitudes directly.

H⊗H |ψ⟩:
For each basis state |ab⟩, H⊗H transforms:
H|0⟩ = (1/√2)(|0⟩ + |1⟩)
H|1⟩ = (1/√2)(|0⟩ - |1⟩)

So H⊗H|00⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
H⊗H|01⟩ = (1/2)(|00⟩ - |01⟩ + |10⟩ - |11⟩)
H⊗H|10⟩ = (1/2)(|00⟩ + |01⟩ - |10⟩ - |11⟩)
H⊗H|11⟩ = (1/2)(|00⟩ - |01⟩ - |10⟩ + |11⟩)

So the final state amplitudes are:
α_00 = (1/4)(1 + i + e^(iπ/3) + i·e^(iπ/3))
α_01 = (1/4)(1 - i + e^(iπ/3) - i·e^(iπ/3))
α_10 = (1/4)(1 + i - e^(iπ/3) - i

## isqTrain/2667

- task_id: `isqTrain/2667`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `123`

### Prompt

I need an isQ program to creates a Bell state (maximally entangled two-qubit state). Apply a Hadamard gate to the first qubit, then a CNOT with the first qubit as control and the second as target. Measure both qubits.

Requirements:
- Use 2 qubit(s) total.
- Measure 2 qubit(s) at the end.
- The program must start with `import std;`, declare qubits at global scope (or procedure scope as appropriate), define `procedure main()` as the entry point, and include explicit `M()` calls for all measured qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a maximally entangled Bell state (|Φ+⟩ = (|00⟩ + |11⟩)/√2) from |00⟩.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured at the end.
3. **State evolution**:
   - Initial: |00⟩
   - H(q[0]): → (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
   - CNOT(q[0], q[1]): → (|00⟩ + |11⟩)/√2 (Bell state)
4. **Expected probabilities**: Each basis state (|00⟩, |11⟩) has probability |1/√2|² = 0.5.

## isqTrain/778

- task_id: `isqTrain/778`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4235`

### Prompt

Write isQ code for the following quantum task: implements a variant of the gf2_multiplication pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement GF(2) multiplication (AND operation) on inputs stored in q[0] and q[1], storing the result in q[2], using an expanded 4-qubit register with q[3] as an uncomputed ancilla.
2. **Qubits**: 4 qubits (q[0]-q[3]); q[2] and q[3] are measured.
3. **State evolution**:
   - Start: |0000⟩
   - After X(q[0]): |1000⟩
   - After X(q[1]): |1100⟩
   - After Toffoli(q[0], q[1], q[2]): |1110⟩ (both controls are |1⟩, so target q[2] flips to |1⟩)
4. **Measurement**: q[2]=1, q[3]=0 → bitstring |10⟩ with probability 1.0, since GF(2) multiplication of 1·1 = 1 and q[3] remains |0⟩ throughout.

## isqTrain/828

- task_id: `isqTrain/828`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4413`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[4];

procedure main() {
    // Put input a in superposition, set b=1
    H(q[0]);
    X(q[1]);
    // Half adder: sum = a XOR b
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    // Carry = a AND b
    Toffoli(q[0], q[1], q[3]);
    // Measure sum and carry
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Input:** An isQ program representing a half adder with one superposed input.
    *   **Task:** Predict measurement outcome probabilities, explain reasoning step-by-step using Dirac notation.
    *   **Constraints:** Concise (3-15 lines), start with "## Circuit Analysis", end with predicted probability distribution, NO code blocks, strict formatting.

2.  **Analyze the isQ Code:**
    *   `qbit q[4];` -> 4 qubits initialized to $|0000\rangle$.
    *   `H(q[0]);` -> Puts $q[0]$ (input $a$) in superposition: $(|0\rangle + |1\rangle)/\sqrt{2}$.
    *   `X(q[1]);` -> Flips $q[1]$ (input $b$) to $|1\rangle$. State is now $|0+\rangle \otimes |00\rangle = \frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$. (Order: $q[0]q[1]q[2]q[3]$)
    *   `CNOT(q[0], q[2]);` -> XOR of $a$ and 0. State: $\frac{1}{\sqrt{2}}(|0000\rangle + |1010\rangle)$.
    *   `CNOT(q[1], q[2]);` -> XOR of $b$ (which is 1) and current $q[2]$.
        *   If $a=0$: $q[2]$ goes from 0 to 1.
        *   If $a=1$: $q[2]$ goes from 1 to 0.
        *   State: $\frac{1}{\sqrt{2}}(|0110\rangle + |1000\rangle)$.
    *   `Toffoli(q[0], q[1], q[3]);` -> AND of $a$ and $b=1$.
        *   If $a=0$: $q[3]$ remains 0.
        *   If $a=1$: $q[3]$ flips to 1.
        *   State: $\frac{1}{\sqrt{2}}(|0110\rangle + |1011\rangle)$.
    *   `M(q[2]); M(q[3]);` -> Measures $q[2]$ (Sum) and $q[3]$ (Carry).

3.  **Map to Probabilities:**
    *   State 1: $|0_{q0} 1_{q1} 1_{q2} 0_{q3}\rangle$ -> Measurement outcomes $q[2]=1, q[3]=0$.
    *   State 2: $|1_{q0} 0_{q1} 0_{q2} 1_{q3}\rangle$ -> Measurement outcomes $q[2]=0, q[3]=1$.
    *   Output formatting (earlier measured = higher bit):
        *   `M(q[2])` is measured first -> highest bit. So the bitstring is `q[2]q[3]`.
        *   State 1 gives `10`.
        *   State 2 gives `01`.
    *   Probabilities: $|10\rangle$: 0.5, $|01\rangle$: 0.5.

4.  **Draft the Explanation:**
    *   Initial: $|0000\rangle$
    *   After H(q0) and X(q1): $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)_{01} \otimes |00\rangle_{23} = \frac{1}{\sqrt{2}}(|0000\rangle + |1000\rangle)$
    *   After CNOT(q0, q2): $\frac{1}{\sqrt{2}}(|0000\rangle + |1010\rangle)$
    *   After CNOT(q1, q2) (since q1=1, flips q2): $\frac{1}{\sqrt{2}}(|0110\rangle + |1000\rangle)$
    *   After Toffoli(q0, q1, q3) (AND of q0 and q1): $\frac{1}{\sqrt{2}}(|0110\rangle + |1011\rangle)$
    *   Measure q2 (sum) and q3 (carry). Q2 is higher bit.
    *   Final predicted probability distribution.

5.  **Refine for Conciseness (Target 3-8

### Reference answer

{'predicted_probs': {'1': 0.5, '2': 0.5}, 'explanation': 'Parametric variant of isqEval/290. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3598

- task_id: `isqTrain/3598`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3708`

### Prompt

Fix the bug in the following isQ program.

Bug description: Missing Hadamard gate

The program should Teleportation of |0> with correction gates.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a bug analysis for an isQ quantum program.
    *   Bug description: Missing Hadamard gate.
    *   Target functionality: Teleportation of |0> with correction gates.
    *   Output constraint: ONLY the analysis, starting with "## Bug Analysis", 3-15 lines, no code blocks.

2.  **Examine the Buggy vs. Correct Code:**
    *   Buggy: CNOT(q[0], q[1]); -> CNOT(q[1], q[2]);
    *   Correct: CNOT(q[0], q[1]); -> H(q[0]); -> CNOT(q[1], q[2]);
    *   Difference: `H(q[0])` is missing after the CNOT.

3.  **Formulate the Bug Analysis:**
    *   *What the bug is:* The Hadamard gate `H(q[0])` is missing after the CNOT between `q[0]` and `q[1]`. This gate is required to complete Alice's Bell measurement basis transformation on the sender's side.
    *   *What the fix is:* Add `H(q[0]);` immediately after `CNOT(q[0], q[1]);`.
    *   *State evolution:*
        *   Initial state: |000>
        *   Bell pair creation (H on q[1], CNOT q[1], q[2]): |0> ⊗ |Φ+> = (1/√2)(|000> + |011>)
        *   CNOT(q[0], q[1]): (1/√2)(|000> + |111>) - Wait, this is without H?
        *   Let's re-evaluate state evolution.
        *   Initial: |000>
        *   H(q[1]), CNOT(q[1], q[2]): (1/√2)(|000> + |011>)
        *   CNOT(q[0], q[1]): (1/√2)(|000> + |111>)
        *   H(q[0]): (1/2)( |000> + |100> + |011> - |111> ) -- wait.
            Let's do it carefully:
            |000> -> H on q0 -> (1/√2)(|000> - |100>)  (if we use H|0> = |+>, H|1> = |->, or standard H|0>=|+>, H|1>=|->)
            Wait, |000> with H on q0 -> |+00> = (1/√2)(|000> + |100>)
            |111> with H on q0 -> |-11> = (1/√2)(|011> - |111>)
            Sum: (1/2) (|000> + |100> + |011> - |111>)
        *   CNOT(q[1], q[2]) and CZ(q[0], q[2]):
            States to trace:
            |000> -> CNOT(1,2) -> |000> -> CZ(0,2) -> |000>
            |100> -> CNOT(1,2) -> |100> -> CZ(0,2) -> |100>  (Z on |0> is |0>)
            |011> -> CNOT(1,2) -> |001> -> CZ(0,2) -> |001>  (Wait, CZ on |001> -> Z on q2 -> -|001> ?) No, CZ control is q0.
            Let's list them properly:
            |000> -> |000>
            |100> -> |100>
            |011> -> |001>
            |-111> -> -|111> -> -|110> -> CZ -> +|110>
            So final state is (1/2)(|000> + |100> + |001> + |110>) -- wait.
            The prompt says expected probabilities: {|000>: 0.25, |010>: 0.25, |100>: 0.25, |110>: 0.25}.
            Let me re-read the prompt's expected probabilities.
            Why |010> instead of |001>?
            Ah, M(q[0]); M(q[1]); M(q[2]); The bits are usually reported based on the qubit index, but let's assume bitstring is q0 q1 q2 or similar.
            Let's re-evaluate the state.
            State after H(q0) on |000> + |111>:
            |000> -> |+00> = |000> + |100>
            |111> -> |-11> = |

## isqTrain/347

- task_id: `isqTrain/347`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2169`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the arithmetic_circuit pattern using p[2] -> p[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program that implements a variant of the arithmetic_circuit pattern using p[2] -> p[4].

Let me analyze The implementation:
- We have qubit registers: c[1] and p[4]
- There are two helper procedures: DEC and INC
- DEC: X(p0), CNOT(p0, p1) - this transforms |00> -> |11> and |10> -> |01>
- INC: CNOT(p0, p1), X(p0) - this transforms |00> -> |11> and |10> -> |01>

Wait, let me trace through more carefully:
- DEC on |00>: X(p0) -> |10>, CNOT -> |11>
- DEC on |01>: X(p0) -> |11>, CNOT -> |10>
- DEC on |10>: X(p0) -> |00>, CNOT -> |01>
- DEC on |11>: X(p0) -> |01>, CNOT -> |00>

- INC on |00>: CNOT -> |00>, X(p0) -> |10>
- INC on |01>: CNOT -> |11>, X(p0) -> |01>
- INC on |10>: CNOT -> |10>, X(p0) -> |00>
- INC on |11>: CNOT -> |01>, X(p0) -> |11>

Now let me trace the main circuit:
1. Initial state: |0>_c |0000>_p
2. H(c[0]): (|0> + |1>)/√2 |0000> = (|00000> + |10000>)/√2

3. ctrl INC(c[0], p[0], p[1]):
   - When c[0] = |0>: nothing happens
   - When c[0] = |1>: INC(p[0], p[1]) is applied
   - INC on p[0], p[1] which are |00>: CNOT -> |00>, X -> |10>
   - Result: (|00000> + |11000>)/√2

4. nctrl DEC(c[0], p[0], p[1]):
   - When c[0] = |0>: DEC(p[0], p[1]) is applied
   - When c[0] = |1>: nothing happens
   - DEC on p[0], p[1] which are |00>: X -> |10>, CNOT -> |11>
   - Result: (|01000> + |11000>)/√2

Wait, that doesn't match the predicted output. Let me reconsider.

Actually, I need to be more careful. Let me re-analyze the output: {|1000>: 0.5, |1100>: 0.5}

This suggests measuring p[0], p[1], p[2], p[3]. The bitstring would be p[0]p[1]p[2]p[3].

Wait, the measurement statement is: M(p[0]); M(p[1]); M(p[2]); M(p[3]);

In --probs mode, earlier measured qubit = higher bit. So:
- First measured: p[0] = highest bit
- Second measured: p[1]
- Third measured: p[2]
- Fourth measured: p[3] = lowest bit

So |1000> means p[0]=1, p[1]=0, p[2]=0, p[3]=0
And |1100> means p[0]=1, p[1]=1, p[2]=0, p[3]=0

Let me re-trace:

1. Initial: |0>_c |0000>_p = |00000>

2. H(c[0]): (|0> + |1>)/√2 ⊗ |0000> = (|00000> + |10000>)/√2
   Using notation where first bit is c[0], next 4 bits are p[0-3]

3. ctrl INC(c[0], p[0], p[1]):
   - Only applies when c[0] = |1>
   - For the |10000> component: INC(p[0], p[1]) = INC(|00>) = |10>
   - Result: (|00000> + |11000>)/√2
   Wait, that's c[0]p[0]p[1]p[2]p[3], so the state is:
   |0>|0000> + |1>|1000>
   Hmm, I need to be clearer.

Let me use the full state |c[0], p[0], p

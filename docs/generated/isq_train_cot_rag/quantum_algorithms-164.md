# ISQ training COT RAG corpus: quantum_algorithms shard 164

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3518

- task_id: `isqTrain/3518`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `basis_change`, `interference`
- source: `isq_train_cot`
- dataset_index: `628`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```
import std;

qbit q[2];

procedure main() {
    H(q[0]); H(q[1]);

    CZ(q[0], q[1]);

    H(q[0]); H(q[1]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Predict the output probability distribution of an isQ program.
    *   **Circuit:**
        *   `H(q[0]); H(q[1]);`
        *   `CZ(q[0], q[1]);`
        *   `H(q[0]); H(q[1]);`
        *   `M(q[0]); M(q[1]);`
    *   **Goal:** Generate a concise, step-by-step reasoning (3-15 lines), using Dirac notation, and output the predicted probability distribution at the end.
    *   **Format constraints:** Output only the analysis, starting with "## Circuit Analysis", ending with the distribution, no isQ code blocks.

2.  **Circuit Analysis & State Evolution:**
    *   *Initial state:* $|00\rangle$
    *   *After H on both:* $(H \otimes H)|00\rangle = |++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    *   *After CZ:* CZ applies a phase of -1 to the $|11\rangle$ state.
        State becomes $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
        Note: $H \otimes H \cdot CZ \cdot H \otimes H$ is equivalent to CNOT.
    *   *After H on both:* Apply $H \otimes H$ again.
        *   $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$
        *   Let's trace it:
            *   $|00\rangle \to |++\rangle$
            *   $|01\rangle \to |+-\rangle$
            *   $|10\rangle \to |-+\rangle$
            *   $|11\rangle \to |--\rangle$
        Wait, $H^{\otimes 2} \cdot CZ \cdot H^{\otimes 2}$ acts as CNOT. Let's verify:
        $CNOT_{01}|00\rangle = |00\rangle$
        $CNOT_{01}|01\rangle = |01\rangle$
        $CNOT_{01}|10\rangle = |11\rangle$
        $CNOT_{01}|11\rangle = |10\rangle$
        Let's do the linear algebra for $H \otimes H \cdot (\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle))$:
        $\frac{1}{2} (|++\rangle + |+-\rangle + |-+\rangle - |--\rangle)$
        $= \frac{1}{4} ( (|0\rangle+|1\rangle)(|0\rangle+|1\rangle) + (|0\rangle+|1\rangle)(|0\rangle-|1\rangle) + (|0\rangle-|1\rangle)(|0\rangle+|1\rangle) - (|0\rangle-|1\rangle)(|0\rangle-|1\rangle) )$
        Sum of 1st and 2nd terms: $2|0\rangle(|0\rangle+|1\rangle)$
        Sum of 3rd and 4th terms: $2|1\rangle(|0\rangle+|1\rangle) \times (-1)$ wait:
        1: $|00\rangle + |01\rangle + |10\rangle + |11\rangle$
        2: $|00\rangle - |01\rangle + |10\rangle - |11\rangle$
        3: $|00\rangle + |01\rangle - |10\rangle - |11\rangle$
        4: $-|00\rangle + |01\rangle + |10\rangle - |11\rangle$
        Sum: $(1+1+1-1)|00\rangle = 2|00\rangle$
        $(1-1+1+1)|01\rangle = 2|01\rangle$
        $(1+1-1+1)|10\rangle = 2|10\rangle$
        $(1-1-1-1)|11\rangle = -2|11\rangle$
        Multiply by 1/4: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
        Wait, let me re-evaluate.
        $1 + 2 + 3 - 4$:
        $|00\rangle$: $1 + 1 +

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'The output is |11> with probability 1.0'}

## isqTrain/4829

- task_id: `isqTrain/4829`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_import_qft`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1452`

### Prompt

Code this in isQ: uses QFT for phase estimation-like operation. Import std and qft. Declare 2 global qubits. Apply X(q[0]) to prepare |10>. Apply qft(q). Apply Rz(3.14159265358979, q[0]) to add a pi phase. Apply qft_inv(q). Measure both qubits.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. We have 2 qubits initialized to |00⟩
2. Apply X(q[0]) → |10⟩
3. Apply QFT on both qubits
4. Apply Rz(π, q[0]) - adds a π phase to q[0]
5. Apply QFT⁻¹ on both qubits
6. Measure both qubits

Let me trace through the state evolution:

**Step 1: Initial state |00⟩**

**Step 2: X(q[0]) → |10⟩**

**Step 3: QFT(q) on |10⟩**

The 2-qubit QFT on |10⟩:
QFT maps |x⟩ to 1/√N Σ_k e^(2πixk/N) |k⟩ where N = 2² = 4

|x⟩ = |2⟩ (binary 10 = decimal 2)

QFT|10⟩ = 1/2 Σ_{k=0}^{3} e^(2πi·2·k/4) |k⟩
= 1/2 [|0⟩ + e^(iπ)|1⟩ + e^(2iπ)|2⟩ + e^(3iπ)|3⟩]
= 1/2 [|0⟩ - |1⟩ + |2⟩ - |3⟩]
= 1/2 [|00⟩ - |01⟩ + |10⟩ - |11⟩]

**Step 4: Rz(π, q[0])**

Rz(θ) applies e^(-iθ/2) to |0⟩ and e^(iθ/2) to |1⟩ on that qubit.

For q[0] (the first qubit, which is the higher-order qubit):
- When q[0] = |0⟩: multiply by e^(-iπ/2) = -i
- When q[0] = |1⟩: multiply by e^(iπ/2) = i

State becomes:
1/2 [-i|00⟩ + i|01⟩ + i|10⟩ - i|11⟩]
= -i/2 [|00⟩ - |01⟩ - |10⟩ + |11⟩]

Wait, let me be more careful. In isQ, q[0] and q[1] - which is the "higher-order" bit?

In the bitstring convention for 2 qubits, if we have q[0] and q[1], the state |q[0]q[1]⟩ means q[0] is the higher bit.

Rz(π) on q[0]:
- |00⟩ → e^(-iπ/2)|00⟩ = -i|00⟩
- |01⟩ → e^(-iπ/2)|01⟩ = -i|01⟩
- |10⟩ → e^(iπ/2)|10⟩ = i|10⟩
- |11⟩ → e^(iπ/2)|11⟩ = i|11⟩

State before Rz: 1/2 [|00⟩ - |01⟩ + |10⟩ - |11⟩]

After Rz on q[0]:
1/2 [-i|00⟩ - (-i)|01⟩ + i|10⟩ - i|11⟩]
= 1/2 [-i|00⟩ + i|01⟩ + i|10⟩ - i|11⟩]

Hmm, let me factor:
= -i/2 [|00⟩ - |01⟩ - |10⟩ + |11⟩]
= -i/2 [(|00⟩ + |11⟩) - (|01⟩ + |10⟩)]

Hmm, let me think about this differently. Actually, let me reconsider.

Wait, actually I need to double-check. The QFT of |10⟩...

Actually, let me think about this more carefully using the standard QFT construction.

For 2 qubits, QFT = (H ⊗ I)(controlled-R₂)(I ⊗ H)

But let me just use the formula. The QFT on n qubits maps |x⟩ to 1/√(2^n) Σ_k ω^(xk)|k⟩ where ω = e^(2πi/2^n).

For n=2, ω = e^(2πi/4) = i.

QFT|10⟩ = QFT|2⟩ = 1/2 Σ_{k=0}^{3} i^(2k)|k⟩
= 1/2 [i^0|0⟩ + i^2|1⟩ + i^4|2⟩ + i^6|3⟩]
= 1/2 [|0⟩ + (-1)|1⟩ + 1|2⟩ + (-1)|3⟩]
= 1/2 [|00⟩

## isqTrain/4541

- task_id: `isqTrain/4541`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2030`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;

qbit q[2];
qbit a[2];

procedure my_oracle() {
    CNOT(q[1], a[1]);
}

procedure main() {
    X(q[0]); H(q[1]);  // replaced H with X
    my_oracle();
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ program implementing a simple quantum circuit with two measured qubits (`q[0]`, `q[1]`) and two unmeasured ancilla qubits (`a[0]`, `a[1]`).
    *   Goal: Predict the probability distribution of measurement outcomes and explain the reasoning.
    *   Constraints: Concise (3-15 lines), use Dirac notation, output ONLY the analysis starting with "## Circuit Analysis", no code blocks, end with the predicted probability distribution.

2.  **Analyze the isQ Program:**
    *   Initial state: `|0000>` (q[0], q[1], a[0], a[1]). Note: Standard is to consider only measured qubits for output, but we need the full state for evolution. Let's focus on q[0], q[1], a[1] since a[0] is untouched and remains |0>.
    *   `X(q[0])`: Flips `q[0]` to |1>. State: `|1000>` (q[0], q[1], a[0], a[1]).
    *   `H(q[1])`: Puts `q[1]` in |+>. State: `|1+00>` = `1/sqrt(2)(|10> + |11>)_q |00>_a`.
    *   `my_oracle()` calls `CNOT(q[1], a[1])`.
        *   If `q[1]` is |0>, `a[1]` remains |0>.
        *   If `q[1]` is |1>, `a[1]` flips to |1>.
        *   State becomes `1/sqrt(2)(|1000> + |1111>)` (q[0], q[1], a[0], a[1]).
    *   `H(q[0]); H(q[1])`:
        *   H on q[0]: |1> -> |-> = `1/sqrt(2)(|0> - |1>)`.
        *   H on q[1]: |0> -> |+>, |1> -> |->.
        *   Applying H to q[0] and q[1] on the state `1/sqrt(2)(|1000> + |1111>)`:
            *   `H_{q0,q1} (1/sqrt(2) |10> |00> + 1/sqrt(2) |11> |11>)`
            *   `H_{q0} |1> = 1/sqrt(2)(|0> - |1>)`
            *   `H_{q1} |0> = 1/sqrt(2)(|0> + |1>)`
            *   `H_{q1} |1> = 1/sqrt(2)(|0> - |1>)`
            *   Term 1: `(1/sqrt(2)) * (1/sqrt(2)(|0>-|1>)) * (1/sqrt(2)(|0>+|1>)) |00>_a` = `1/2 (|00> + |01> - |10> - |11>) |00>_a`
            *   Term 2: `(1/sqrt(2)) * (1/sqrt(2)(|0>-|1>)) * (1/sqrt(2)(|0>-|1>)) |11>_a` = `1/2 (|00> - |01> - |10> + |11>) |11>_a`
            *   Combined State on q[0], q[1]: `1/2 (|00>(|00>+|11>)_a + |01>(|00>-|11>)_a - |10>(|00>+|11>)_a - |11>(|00>-|11>)_a)`
    *   Measurements: `M(q[0])`, `M(q[1])`. Since the `q` qubits are entangled with the `a` qubits, tracing out `a` or calculating probabilities based on the full state gives uniform distribution for the measured qubits.
        *   P(|00>) = `(1/2)^2 + (1/2)^2` = `1/4 + 1/4` = `1/2`? Wait.
        *   Let's re-evaluate:
            *   Term 1 (from `|10>_q`): `1/2 (|00> + |01> - |10> - |11>)_q |00>_a`
            *   Term 2

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.2500, P(|01>) = 0.2500, P(|10>) = 0.2500, P(|11>) = 0.2500.'}

## isqTrain/2709

- task_id: `isqTrain/2709`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2886`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
oracle bool[4] g(bool a[4]) {
    bool res[] = [a[0], a[1], a[2], false];
    return res;
}
qbit q[4], res[4];

procedure main(){
    H(q);
    g(q, res);
    H(q); 
    print M(q);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Predict output probability distribution for an isQ circuit.
    *   **Input Circuit:** Applies $H^{\otimes 4}$ to `q`, then `g(q, res)`, then $H^{\otimes 4}$ to `q`, then measures `q`.
    *   **Oracle `g`:** `res[] = [a[0], a[1], a[2], false]`. Wait, the oracle signature is `oracle bool[4] g(bool a[4])`. In `isQ`, `oracle` computes the classical function as a unitary $U_g|x\rangle|0\rangle = |x\rangle|g(x)\rangle$. Here `q` is passed as `x` and `res` is passed as `y` for $|x\rangle|y \oplus g(x)\rangle$. BUT wait, `res` is *not* measured, only `q` is.
    *   **Output Format:** "## Circuit Analysis\n..." concisely (3-8 lines up to 15).
    *   **End with:** Predicted probability distribution.

2.  **Analyze the Circuit:**
    *   `q` has 4 qubits, `res` has 4 qubits. Initially all $|0\rangle$.
    *   `H(q)`: `q` becomes $\sum_{x=0}^{15} |x\rangle / 4$.
    *   `g(q, res)`: The unitary $U_g$ maps $|x\rangle|y\rangle \to |x\rangle|y \oplus g(x)\rangle$. Since $g(x)$ is strictly a function of $x$, this operation acts as a controlled gate on the `res` register, controlled by `q`. It does *not* alter the state of `q` itself, nor does it entangle `q` with `res` in a way that changes the reduced density matrix of `q` if $res$ is discarded (actually, it *does* entangle them, but the next step is $H(q)$, and `res` is untouched).
    *   Wait! Let's look at $U_g$. $U_g|x\rangle|0\rangle = |x\rangle|g(x)\rangle$.
    *   State after $U_g$: $\frac{1}{4} \sum_x |x\rangle|g(x)\rangle$.
    *   Next gate: `H(q)`. Applies $H^{\otimes 4}$ on `q`.
    *   State of `q` after $H^{\otimes 4}$: $\frac{1}{4} \sum_x H^{\otimes 4}|x\rangle|g(x)\rangle = \frac{1}{4} \sum_x (\frac{1}{2} \sum_z (-1)^{x \cdot z}|z\rangle)|g(x)\rangle$.
    *   Notice that $H^{\otimes 4}$ only acts on `q`.
    *   What is the probability of measuring `q` in state $|z\rangle$?
    *   $P(z) = \langle z | \text{Tr}_{res}(|\psi\rangle\langle\psi|) |z\rangle$.
    *   $P(z) = \frac{1}{16} \sum_x \frac{1}{16} \sum_{x'} (-1)^{x \cdot z + x' \cdot z} \langle g(x)|g(x')\rangle$.
    *   Since $g(x)$ is a deterministic function, $\langle g(x)|g(x')\rangle = \delta_{x, x'}$.
    *   Thus, $P(z) = \frac{1}{16} \sum_x \frac{1}{16} (-1)^{2 x \cdot z} = \frac{16}{16} \frac{1}{16} = 1/16$.
    *   Wait, is $g(x)$ constant? No, $g(x)$ varies. But $g(x)$ has no effect on the probability distribution of $q$ because $H^{\otimes 4}$ acts *after* the oracle, and the oracle doesn't entangle $q$ in a way that alters the final $H$ outcome probabilities (since the oracle does not touch `q`).
    *   Actually, $H \to U_g \to H$ is typically used for phase kickback where the oracle writes to a target qubit that was initialized to $|-\rangle$.
    *   Here, `res` is initialized to $|0\rangle$. The oracle writes to `res`. The subsequent

### Reference answer

{'predicted_probs': {'0000': 0.12500000000000003, '0001': 0.12500000000000003, '0010': 0.12500000000000003, '0011': 0.12500000000000003, '0100': 0.12500000000000003, '0101': 0.12500000000000003, '0110': 0.12500000000000003, '0111': 0.12500000000000003}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqExpand/algo/114

- task_id: `isqExpand/algo/114`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `ancilla_usage`
- source: `isq_expansion`
- dataset_index: `3563`

### Prompt

Write isQ code for the following quantum task: implementing a quantum full adder circuit. Use q[0]=A, q[1]=B, q[2]=Cin (carry-in), q[3]=Sum, q[4]=Cout. Set inputs A=1, B=1, Cin=1 via X gates. The full adder computes Sum = A XOR B XOR Cin and Cout = majority(A,B,Cin). Implement Sum with three CNOTs into q[3], and Cout using three Toffoli gates: Toffoli(q[0],q[1],q[4]), Toffoli(q[0],q[2],q[4]), Toffoli(q[1],q[2],q[4]). Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Full adder with A=1, B=1, Cin=1.

Sum = A XOR B XOR Cin: three CNOTs into q[3].
  q[3]: 0 XOR 1 = 1 XOR 1 = 0 XOR 1 = 1

Cout = majority(1,1,1) via three Toffoli gates accumulating into q[4]:
  Toffoli(A,B): q[4] = 0 XOR (1 AND 1) = 1
  Toffoli(A,Cin): q[4] = 1 XOR (1 AND 1) = 0
  Toffoli(B,Cin): q[4] = 0 XOR (1 AND 1) = 1

Final: q=[1,1,1,1,1] = |11111> = index 31 in 32-entry probability array.

## isqTrain/4521

- task_id: `isqTrain/4521`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `interference`, `multi_controlled_logic`, `ancilla_usage`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `3397`

### Prompt

What does this isQ program output when measured?

```isq
import std;

oracle Uf(3,1) = [0,0,0,0,0,0,1,0];

defgate U0 = [
    1, 0, 0, 0, 0, 0, 0, 0;
    0, -1, 0, 0, 0, 0, 0, 0;
    0, 0, -1, 0, 0, 0, 0, 0;
    0, 0, 0, -1, 0, 0, 0, 0;
    0, 0, 0, 0, -1, 0, 0, 0;
    0, 0, 0, 0, 0, -1, 0, 0;
    0, 0, 0, 0, 0, 0, -1, 0;
    0, 0, 0, 0, 0, 0, 0, -1
];

qbit q[3];
qbit anc;

procedure main() {
    
    H(q[0]); H(q[1]); H(q[2]);
    
    X(anc);
    H(anc);
    
    Uf(q[2], q[1], q[0], anc);
    H(q[0]); H(q[1]); H(q[2]);
    U0(q[2], q[1], q[0]);
    H(q[0]); H(q[1]); H(q[2]);
    
    Uf(q[2], q[1], q[0], anc);
    H(q[0]); H(q[1]); H(q[2]);
    U0(q[2], q[1], q[0]);
    H(q[0]); H(q[1]); H(q[2]);
    
    H(anc); X(anc);
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program and predict the probability distribution of measurement outcomes.
The program is essentially two iterations of Grover's algorithm for a 3-qubit search space, followed by an X gate on qubit 0, and then measurement.
Wait, let me trace the oracle and diffusion operator.

Number of qubits: 4 (q[0], q[1], q[2], anc).
Wait, `q` has 3 qubits. `anc` has 1 qubit.
Initial state: |0000> (q[2], q[1], q[0], anc) - wait, the order in the code is `qbit q[3]; qbit anc;`.
Actually, let's look at the problem.
Oracle Uf(3,1) = [0,0,0,0,0,0,1,0].
This means for the basis states |000> to |111>, Uf flips the ancilla if the state is |110>.
Let's check the array: indices are 0 to 7.
Index 0: |000> -> 0
Index 1: |001> -> 0
Index 2: |010> -> 0
Index 3: |011> -> 0
Index 4: |100> -> 0
Index 5: |101> -> 0
Index 6: |110> -> 1
Index 7: |111> -> 0
Wait, the array is `[0,0,0,0,0,0,1,0]`, but this is an oracle definition.
Usually, `oracle Uf(n, m) = [...]` applies an X gate to the m target qubits based on the n control qubits.
Actually, in isQ, `oracle Uf(3,1) = [0,0,0,0,0,0,1,0];` typically means a diagonal matrix or a controlled-X.
Wait, if it's a diagonal matrix of phases, it might be a phase oracle.
Let's re-read the definition. `[0,0,0,0,0,0,1,0]` is exactly 8 elements.
If it's a controlled-NOT, the matrix is not a vector.
Ah! In isQ, an `oracle` defined with an array is typically a phase oracle or it applies X on the ancilla.
Wait, the parameters are `Uf(3,1)`. 3 input qubits, 1 output qubit.
The array `[0,0,0,0,0,0,1,0]` corresponds to the boolean function $f(x)$ for $x=0 \dots 7$.
So $f(x) = 1$ for $x=6$ (which is $|110\rangle$).
The oracle applies $|x\rangle|y\rangle \to |x\rangle|y \oplus f(x)\rangle$.
This is the standard Deutsch-Jozsa / Grover oracle.
Target qubit is `anc`. `anc` is initialized to $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
So applying $U_f$ introduces a phase of $-1$ for the $|110\rangle$ state.
Wait, $|x\rangle (|0\rangle - |1\rangle) \to |x\rangle (|0 \oplus f(x)\rangle - |1 \oplus f(x)\rangle)$.
If $f(x)=0$, state is $|x\rangle(|0\rangle-|1\rangle)$.
If $f(x)=1$, state is $-|x\rangle(|0\rangle-|1\rangle)$.
So it's a phase oracle for $|110\rangle$.

Let's check `U0`.
`U0` is an 8x8 matrix. It has 1 in the top-left, and -1 on the rest of the diagonal.
This is exactly the Grover diffusion operator $2|0\rangle\langle0| - I$.
Wait, the program does:
1. H(q) -> $\sum |x\rangle / \sqrt{8}$
2. X(anc), H(anc) -> anc is $|-\rangle$.
3. Uf(q, anc) -> phase flip on $|110\rangle$ in the `q` register.
4. H(q)^3, U0(q), H(q)^3 -> Grover diffusion on `q` register.
This completes 1 iteration of Grover's algorithm.
5. Uf(q, anc) -> phase flip on $|110\rangle$.
6. H(q)^3, U0(q), H(q)^3 -> Grover diffusion on `q` register

### Reference answer

{'predicted_probs': {'000': 0.007813, '001': 0.007812, '010': 0.007813, '011': 0.007813, '100': 0.007813, '101': 0.007812, '110': 0.007813, '111': 0.945312}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.0078, P(|001>) = 0.0078, P(|010>) = 0.0078, P(|011>) = 0.0078, P(|100>) = 0.0078, P(|101>) = 0.0078, P(|110>) = 0.0078, P(|111>) = 0.9453.'}

## isqTrain/3646

- task_id: `isqTrain/3646`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `5002`

### Prompt

Create an isQ quantum circuit that the 3-qubit inverse Quantum Fourier Transform (QFT†) on input |101>. Use bit-reversal swaps first, then apply inverse rotation stages with negative angles. Measure all qubits.

### Chain-of-thought reasoning

The user wants me to implement a 3-qubit inverse QFT on input |101>.
Let me trace through the logic.
The input state is |101>. In standard Qiskit-like ordering, this means:
q[0] = 1 (least significant bit)
q[1] = 0
q[2] = 1 (most significant bit)
Wait, |101> usually means q[2]q[1]q[0] = |101>. So q[2]=1, q[1]=0, q[0]=1.
The implementation initializes:
X(q[0]) -> q[0] is |1>
X(q[2]) -> q[2] is |1>
So the state is |q[2]q[1]q[0]> = |101>. This matches.

The goal of the inverse QFT is to map the state $\frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i x k / N} |k>$ back to $|x>$.
Wait, the input is |101> = |5>.
In binary, $|5\rangle = |101\rangle$.
Wait, does The implementation really prepare |101> and then do inverse QFT?
The implementation prepares:
X(q[0]); X(q[2]); -> State is |101>.
Then it applies:
CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]); -> This is a swap (three-CNOT decomposition)(q[0], q[2]).
State is now |101> swapped to |101>. Wait, |101> swapped is |101>.
Then H(q[2]).
Then ctrl Rz(-pi/2, q[2], q[1]).
Then H(q[1]).
Then ctrl Rz(-pi/4, q[2], q[0]).
Then ctrl Rz(-pi/2, q[1], q[0]).
Then H(q[0]).

Wait, this looks like it's doing inverse QFT *without* the final bit reversal.
Ah! In standard QFT, the bit reversal is at the end. So in inverse QFT, the bit reversal should be at the beginning.
Wait! If the inverse QFT has bit reversal at the beginning:
Standard QFT on |x> gives $\sum e^{...} |y>$, but with y reversed.
So if we do inverse QFT, we first reverse bits, then apply inverse stages.
In the implementation:
swap(0, 2) via three CNOTs is applied.
Then H(2), CRz(2,1), H(1), CRz(2,0), CRz(1,0), H(0).
This matches inverse QFT *without* bit reversal, but wait:
If we apply H(2) first, this corresponds to the most significant bit, which is q[2] after the swap!
Wait, standard QFT on |x_2 x_1 x_0>:
H(x_0)
CRz(x_0, x_1)
CRz(x_0, x_2)
H(x_1)
CRz(x_1, x_2)
H(x_2)
swap(0, 2) via three CNOTs

Inverse QFT (standard, e.g., Qiskit):
swap(0, 2) via three CNOTs
H(x_2)
CRz(x_1, x_2) -- but with negative angle!
H(x_1)
CRz(x_0, x_2) -- negative angle
CRz(x_0, x_1) -- negative angle
H(x_0)

Let's check The implementation angles:
swap (three-CNOT decomposition)(q[0], q[2]) is done via 3 CNOTs.
H(q[2])
ctrl Rz(-2.0 * pi / 4.0, q[2], q[1]); -> wait, control is q[2], target is q[1]? No, `ctrl Rz(theta, q[2], q[1])` in isQ means control is q[2], target is q[1]? Wait, reference says `ctrl Rz(theta, q[2], q[1])`. In isQ syntax `ctrl @[c] Rz(theta, t)`. If written `ctrl Rz(theta, c, t)`, then `c` is control, `t` is target.
So control q[2], target q[1].
Wait! In the standard inverse QFT after swap(0, 2) via three CNOTs:
The old q[0] becomes q[2].
So H is on q[2]. Then controlled phase on q[1] controlled by q[2].
This matches The implementation exactly.

Wait, the user prompt asks for: "inverse Quantum Fourier Transform (Q

## isqTrain/3065

- task_id: `isqTrain/3065`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `4172`

### Prompt

请用isQ语言编写一个量子电路：initializes 4 qubits to the state |0001> using X gates and measures all.

Requirements:
- Declare `qbit q[4];` at global scope.
- Apply X to qubits that should be |1>.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize a 4-qubit register to the computational basis state |0001> and measure all qubits.
2. **Qubits**: 4 qubits (q[0] to q[3]) are declared globally; all are measured.
3. **State evolution**: The register starts in |0000>. Applying X to q[3] flips it from |0> to |1>, yielding |0001>.
4. **Measurement outcomes**: Since the final state is exactly |0001>, measurement yields outcome 0001 with probability 1.0.

## isqTrain/3710

- task_id: `isqTrain/3710`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1134`

### Prompt

Write an isQ program that QAOA (p=1) for the MaxCut problem on a 3-node triangle graph with edges [(0, 1), (1, 2), (0, 2)]. Use parameters gamma=0.500 and beta=0.500. The circuit:
1. Initialize all qubits in superposition
2. Apply cost unitary: for each edge, use CNOT-Rz-CNOT
3. Apply mixer: Rx(2*beta) on each qubit
4. Measure all 3 qubits

### Chain-of-thought reasoning

Let me trace through the QAOA circuit for MaxCut on a triangle graph with gamma=0.5 and beta=0.5.

1. Initialize 3 qubits in superposition with H gates: |+⟩|+⟩|+⟩ = (1/2√2)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)

2. Cost unitary for each edge (CNOT-Rz-CNOT):
   - Edge (0,1): Rz(1.0) conditioned on qubit 0 parity with qubit 1
   - Edge (1,2): Rz(1.0) conditioned on qubit 1 parity with qubit 2
   - Edge (0,2): Rz(1.0) conditioned on qubit 0 parity with qubit 2

The CNOT-Rz(2γ)-CNOT sequence applies exp(-iγZ⊗Z) between two qubits. With γ=0.5, Rz(1.0).

For the cost unitary, states where the pair of qubits differ (one 0, one 1) get a phase of e^(-iγ), while states where they're the same get e^(iγ).

Let me track phases for each basis state through the three edges:

For edge (0,1): phase depends on whether q0 ⊕ q1 = 0 (same) or 1 (different)
- Same (00 or 11): phase = e^(iγ) = e^(0.5i)
- Different (01 or 10): phase = e^(-iγ) = e^(-0.5i)

For edge (1,2): phase depends on q1 ⊕ q2
For edge (0,2): phase depends on q0 ⊕ q2

The total phase for each state is the product of phases from each edge.

Let me compute for each basis state:
- |000⟩: edges (0,1) same, (1,2) same, (0,2) same → 3 same → phase = e^(1.5i)
- |001⟩: edges (0,1) same, (1,2) diff, (0,2) diff → 1 same, 2 diff → phase = e^(0.5i)e^(-i) = e^(-0.5i)
- |010⟩: edges (0,1) diff, (1,2) same, (0,2) diff → 1 same, 2 diff → phase = e^(-0.5i)
- |011⟩: edges (0,1) diff, (1,2) diff, (0,2) same → 1 same, 2 diff → phase = e^(-0.5i)
- |100⟩: edges (0,1) diff, (1,2) same, (0,2) diff → 1 same, 2 diff → phase = e^(-0.5i)
- |101⟩: edges (0,1) diff, (1,2) diff, (0,2) same → 1 same, 2 diff → phase = e^(-0.5i)
- |110⟩: edges (0,1) same, (1,2) diff, (0,2) diff → 1 same, 2 diff → phase = e^(-0.5i)
- |111⟩: edges (0,1) same, (1,2) same, (0,2) same → 3 same → phase = e^(1.5i)

Wait, for a triangle graph, the MaxCut value of a bitstring is the number of edges cut. States |000⟩ and |111⟩ cut 0 edges, while states like |001⟩, |010⟩, etc. cut 2 edges each.

So states with all same qubits get phase e^(i·3γ) and states with mixed qubits get phase e^(-iγ) (for the 2-edge cut states).

Actually, the cost Hamiltonian is C = Σ Z_i Z_j for edges. The cost value for |000⟩ is +3, for |111⟩ is +3, for |001⟩ is -1 (Z0Z1=1, Z1Z2=-1, Z0Z2=-1 → sum = -1).

Wait, actually MaxCut cost is typically (1-Z_i Z_j)/2 summed over edges, but the QAOA cost unitary uses exp(-iγ C). Let me reconsider.

The standard QAOA for MaxCut uses C = Σ_{(i,j)} (1-Z_iZ_j)/2, so exp(-iγC)

## isqTrain/1421

- task_id: `isqTrain/1421`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5756`

### Prompt

Create an isQ quantum circuit that Apply the 3-qubit Quantum Fourier Transform to the input state |100> and measure all qubits.

### Chain-of-thought reasoning

Let me trace through this 3-qubit QFT applied to |100>.

Initial state: |100>

Step 1: X(q[0]) flips q[0], so |100> → |101>... wait, let me reconsider the qubit ordering.

Actually, wait. Let me re-read. The input is |100> and X(q[0]) is applied. If we think of q[0] as the least significant bit (rightmost), then |100> means q[2]=1, q[1]=0, q[0]=0. Applying X(q[0]) gives |101>.

Hmm, but let me think about this more carefully. In many quantum computing frameworks, |100> means q[0]=1, q[1]=0, q[2]=0, where q[0] is the leftmost/most significant bit.

Actually, let me just trace through and check if the result makes sense with the predicted output.

The predicted output equal superposition over all 8 states, each with probability 1/8.

Let me think about QFT. The QFT on n qubits maps |k⟩ → (1/√N) Σ_j e^{2πijk/N} |j⟩.

For |100⟩ = |4⟩ in 3-qubit system (N=8):
QFT|4⟩ = (1/√8) Σ_{j=0}^{7} e^{2πi·4·j/8} |j⟩
= (1/√8) Σ_{j=0}^{7} e^{πij} |j⟩
= (1/√8) Σ_{j=0}^{7} (-1)^j |j⟩

So the state is (1/√8)(|0⟩ - |1⟩ + |2⟩ - |3⟩ + |4⟩ - |5⟩ + |6⟩ - |7⟩)

This gives equal probability 1/8 for each computational basis state, which matches the predicted output.

Now let me trace through the code step by step.

Let me assume the bit ordering: |q[2]q[1]q[0]⟩, so |100⟩ means q[2]=1, q[1]=0, q[0]=0.

Step 1: X(q[0]) → |101⟩

Now the QFT on 3 qubits. The standard QFT circuit processes from the most significant qubit to the least significant. But here it seems like q[2] is processed first.

Let me trace:

After X(q[0]): state is |101⟩ (q[2]=1, q[1]=0, q[0]=1)

H(q[2]): q[2] is |1⟩, H|1⟩ = |−⟩ = (|0⟩ − |1⟩)/√2
State: (|001⟩ − |101⟩)/√2

Wait, let me be more careful. |101⟩ = |1⟩_q2 |0⟩_q1 |1⟩_q0

H on q[2]: |1⟩ → (|0⟩ - |1⟩)/√2
State: ((|0⟩ - |1⟩)/√2) ⊗ |0⟩ ⊗ |1⟩ = (|001⟩ - |101⟩)/√2

ctrl S(q[1], q[2]): S gate on q[2] controlled by q[1]. S = diag(1, i). Since q[1] is |0⟩, nothing happens.
State unchanged: (|001⟩ - |101⟩)/√2

ctrl T(q[0], q[2]): T gate on q[2] controlled by q[0]. T = diag(1, e^{iπ/4}). When q[0]=|1⟩, apply T to q[2].
In the state (|001⟩ - |101⟩)/√2:
- |001⟩: q[0]=1, q[2]=0. T on |0⟩ = |0⟩. Result: |001⟩
- |101⟩: q[0]=1, q[2]=1. T on |1⟩ = e^{iπ/4}|1⟩. Result: e^{iπ/4}|101⟩

State: (|001⟩ - e^{iπ/4}|101⟩)/√2

H(q[1]): q[1] is |0⟩ → |+⟩ = (|0⟩+|1⟩)/√2
State: (|001⟩ - e^{iπ/4}|101⟩)/√2 → apply H on q[1]
= ((|0⟩+|1⟩)/√2 for q[1]) component-wise
= (|001⟩ + |011⟩ - e^{

# ISQ training COT RAG corpus: quantum_algorithms shard 113

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4056

- task_id: `isqTrain/4056`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5417`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// Deutsch-Jozsa for 2-input balanced oracle [0, 1, 0, 1]
oracle f(2, 1) = [0, 1, 0, 1];
qbit q[3];  // 2 input + 1 output

procedure main() {
    // Initialize output qubit to |->
    X(q[2]);
    H(q[2]);
    // Hadamard on input qubits
    H(q[0]); H(q[1]);
    // Apply oracle
    f(q[0], q[1], q[2]);
    // Hadamard on inputs
    // BUG: missing gate here
    // Measure input qubits (non-zero = balanced)
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

The buggy code is missing the Hadamard gates on the input qubits after the oracle application. In the Deutsch-Jozsa algorithm, after applying the oracle, we need to apply Hadamard gates to the input qubits before measurement. This is a key step that allows us to distinguish between constant and balanced functions.

Let me analyze the state evolution:

1. Initial state: |000>

2. After X(q[2]): |001>

3. After H(q[2]): |0>|-> = (|00> - |01>)|->... wait let me be more careful.

   Actually, q[0] and q[1] are inputs, q[2] is output.
   
   Initial: |000>
   After X(q[2]): |001>
   After H(q[2]): |00>|-> where |-> = (|0>-|1>)/sqrt(2)
   After H(q[0]), H(q[1]): (|00>+|01>+|10>+|11>)/sqrt(4) ⊗ |-> = |+>|+>|->

4. Apply oracle f: The oracle maps |x>|y> to |x>|y ⊕ f(x)>. Since y is in |-> state, this becomes (-1)^f(x)|x>|->.

   For f = [0, 1, 0, 1], meaning f(00)=0, f(01)=1, f(10)=0, f(11)=1.
   
   The state becomes: (|00> - |01> + |10> - |11>)/2 ⊗ |->

5. Apply H on input qubits:
   H⊗2(|00> - |01> + |10> - |11>)/2
   
   Using H⊗2|00> = (|00>+|01>+|10>+|11>)/2
   H⊗2|01> = (|00>-|01>+|10>-|11>)/2
   H⊗2|10> = (|00>+|01>-|10>-|11>)/2
   H⊗2|11> = (|00>-|01>-|10>+|11>)/2
   
   So: (H⊗2|00> - H⊗2|01> + H⊗2|10> - H⊗2|11>)/2
   = [(|00>+|01>+|10>+|11>) - (|00>-|01>+|10>-|11>) + (|00>+|01>-|10>-|11>) - (|00>-|01>-|10>+|11>)]/4
   
   Let me compute term by term:
   Coefficient of |00>: 1 - 1 + 1 - 1 = 0
   Coefficient of |01>: 1 - (-1) + 1 - (-1) = 1+1+1+1 = 4... wait let me redo this more carefully.
   
   Actually, let me think about this differently. The state after phase oracle is:
   Σx (-1)^f(x)|x>/2
   
   After H⊗2, the state of input qubits is:
   Σz Σx (-1)^(f(x)+x·z)/2 |z>
   
   For a balanced function, the amplitude for z=00 (all zeros) is:
   Σx (-1)^f(x)/2 = (1 - 1 + 1 - 1)/2 = 0
   
   So we get non-zero probability for |11> state (both measured as 1).
   
   Actually, let me compute more carefully:
   
   The amplitude for |z> after H⊗2 is: (1/2) Σx (-1)^(f(x) + x·z)
   
   For z=00: (1/2)[(-1)^0 + (-1)^1 + (-1)^0 + (-1)^1] = (1/2)(1-1+1-1) = 0
   For z=01: (1/2)[(-1)^(0+0) + (-1)^(1+1) + (-1)^(0+0) + (-1)^(1+1)] = (1/2)(1+1+1+1) = 1... wait
   
   Wait, x·z means inner product. x = (x1, x2), z = (z1, z2), x·z = x1*z1 + x2*z2.
   
   For z=00: (1/2)[(-1)^(0+0) + (-1)^(1+0) + (-1)^(0+0) + (-1)^(1+0)] = (1/2)(

## isqTrain/3466

- task_id: `isqTrain/3466`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `data_encoding_qml`, `phase_manipulation`, `hamiltonian_simulation`
- source: `isq_train_cot`
- dataset_index: `5714`

### Prompt

帮我写一个isQ程序：a single IQP (Instantaneous Quantum Polynomial) encoding layer in isQ.

IQP circuits are used as feature maps in quantum machine learning.
Structure:
1. H on all qubits
2. ZZ entangling layer: for each pair (i,j), apply    CNOT(i,j), Rz(theta_ij, j), CNOT(i,j)
3. Single-qubit Rz rotations

Use 3 qubits with theta_01=0.5, theta_02=0.3, theta_12=0.7.
Single-qubit: Rz(0.4) on each.

Declare 3 qubits, measure all.

### Chain-of-thought reasoning

Let me analyze this IQP encoding circuit step by step.

1. Goal: Implement an IQP feature map for quantum machine learning on 3 qubits.

2. 3 qubits, all measured.

3. Step-by-step evolution:
- Start: |000>
- H on all: (1/√8)(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)
  This is the |+++> state.

Now for the ZZ entangling layer:
- ZZ_01 with theta=0.5: This applies exp(-i*theta/2 * Z⊗Z⊗I) to qubits 0,1
- ZZ_02 with theta=0.3: This applies exp(-i*theta/2 * Z⊗I⊗Z) to qubits 0,2
- ZZ_12 with theta=0.7: This applies exp(-i*theta/2 * I⊗Z⊗Z) to qubits 1,2

The ZZ entangling gate on |x,y> gives e^{-i*theta/2 * (-1)^{x⊕y} * 2} wait, let me think more carefully.

The ZZ interaction: exp(-i*theta*Z⊗Z/2) on |ab> where a,b ∈ {0,1}
Z|0> = |0>, Z|1> = -|1>
So Z⊗Z|ab> = (-1)^{a+b}|ab> (wait, that's not right either)

Actually: Z⊗Z|ab> = (-1)^a * (-1)^b |ab> = (-1)^{a+b} |ab>

No wait: Z⊗Z means Z on first qubit and Z on second. So Z⊗Z|ab> = (Z|a>)⊗(Z|b>) = ((-1)^a|a>)⊗((-1)^b|b>) = (-1)^{a+b}|ab>

So exp(-i*theta/2 * Z⊗Z)|ab> = e^{-i*theta/2 * (-1)^{a+b}}|ab>

Actually wait, I need to be more careful. Let me reconsider.

For the computational basis state |abc> with bits a, b, c:
- The phase from ZZ_01(theta_01) is e^{-i*theta_01/2 * (-1)^{a+b}}
- The phase from ZZ_02(theta_02) is e^{-i*theta_02/2 * (-1)^{a+c}}
- The phase from ZZ_12(theta_12) is e^{-i*theta_12/2 * (-1)^{b+c}}

Hmm, but the CNOT-Rz-CNOT construction:
CNOT(0,1), Rz(theta, 1), CNOT(0,1)

Let me verify this implements ZZ. If qubit 0 has value a and qubit 1 has value b:
- CNOT(0,1): |a,b> → |a, a⊕b>
- Rz(theta, 1): |a, a⊕b> → e^{-i*theta/2 * (-1)^{a⊕b}} |a, a⊕b>
- CNOT(0,1): |a, a⊕b> → |a, b>

So the net effect is a phase e^{-i*theta/2 * (-1)^{a⊕b}}.

When a=b, a⊕b=0, so phase = e^{-i*theta/2}
When a≠b, a⊕b=1, so phase = e^{i*theta/2}

This is indeed the exp(-i*theta/2 * Z⊗Z) up to a global phase.

OK so after all ZZ layers, each computational basis state |abc> picks up a phase:
φ(abc) = -0.5*theta_01*(-1)^{a⊕b} - 0.5*theta_02*(-1)^{a⊕c} - 0.5*theta_12*(-1)^{b⊕c}

Then Rz(0.4) on each qubit adds a phase of -0.4/2 * (-1)^a for qubit 0, etc.

So after all layers, the state is:
(1/√8) Σ_{abc} e^{iφ(abc)} |abc>

where φ(abc) encodes all the ZZ and single-qubit rotation phases.

Now the key insight for the predicted output: The output says all 8 basis states have equal probability 1/8 = 0.125. This makes sense because:

1. The ZZ interactions and Rz rotations are all diagonal in the computational basis
2. The Hadamards at the beginning create a uniform superposition

## isqTrain/2701

- task_id: `isqTrain/2701`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3482`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[2];

procedure main(){
    H(q[0]);
    CNOT(q[0],q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits $q[0], q[1]$ in the state $|00\rangle$.
2. Applying the Hadamard gate $H(q[0])$ to the first qubit creates a uniform superposition, yielding the state $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
3. Applying the $CNOT(q[0], q[1])$ gate flips the target qubit $q[1]$ whenever the control qubit $q[0]$ is in the state $|1\rangle$. This results in the maximally entangled Bell state $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
4. Both qubits are measured, collapsing the state. The probability of measuring $|00\rangle$ is $0.5$, and the probability of measuring $|11\rangle$ is $0.5$.

Predicted probability distribution: {'00': 0.5, '01': 0.0, '10': 0.0, '11': 0.5}

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1235

- task_id: `isqTrain/1235`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `mid_circuit_measurement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4180`

### Prompt

Code this in isQ: implements the teleportation_protocol pattern using an alternative gate decomposition (CZ -> H CNOT H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement quantum teleportation of |+⟩ state using CZ → H-CNOT-H decomposition for the Z-correction.

2. **Qubits**: 3 qubits (q[0]: message, q[1]: Alice's half of Bell pair, q[2]: Bob's qubit), all measured.

3. **State evolution**:
   - |000⟩ →

## isqTrain/927

- task_id: `isqTrain/927`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5712`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the boolean_synthesis pattern using q[6] -> q[8]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

The circuit computes a boolean function (majority-like operation) on inputs a=1, b=1, c=0 across an 8-qubit register, measuring only q[5], q[6], q[7].

**State evolution:**
1. **Initial:** |00000000⟩
2. **After X(q[0]), X(q[1]):** |11000000⟩ (sets a=1, b=1, c=0)
3. **After Toffoli(q[0],q[1],q[3]):** |11010000⟩ (q[3] = a∧b = 1)
4. **After Toffoli(q[0],q[2],q[4]):** |11010000⟩ (q[4] = a∧c = 0, unchanged)
5. **After CNOT(q[3],q[5]):** |11010100⟩ (q[5] = q[3]⊕0 = 1)
6. **After CNOT(q[4],q[5]):** |11010100⟩ (q[5] = 1⊕0 = 1, unchanged)
7. **After Toffoli(q[1],q[2],q[5]):** |11010100⟩ (q[5] = 1⊕(b∧c=0) = 1)

**Result:** Final computational state |11010100⟩. Measuring q[5]=1, q[6]=0, q[7]=0 yields |100⟩ with probability 1.0.

## isqTrain/351

- task_id: `isqTrain/351`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2554`

### Prompt

Write isQ code for the following quantum task: implements the arithmetic_circuit pattern with a different measurement ordering (reversed measurement order for p). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

The user wants me to analyze the given isQ program that implements an arithmetic circuit pattern with reversed measurement order.
The circuit has:
- `c[1]`: control qubit
- `p[2]`: data qubits

The program does:
1. `H(c[0])` -> `c[0]` is in |+> state. `p[0]`, `p[1]` are in |00>. Overall state: 1/sqrt(2) (|000> + |100>) assuming order c, p0, p1
2. `ctrl INC(c[0], p[0], p[1])`: INC is `CNOT(p0, p1); X(p0);`. When c[0] is |1>, it applies `CNOT(p0, p1); X(p0)`.
   - On |100>, this yields `CNOT` on p -> |100>, then `X` on p0 -> |110>.
   - Overall state: 1/sqrt(2) (|000> + |110>)
3. `nctrl DEC(c[0], p[0], p[1])`: DEC is `X(p0); CNOT(p0, p1);`. When c[0] is |0>, it applies `X(p0); CNOT(p0, p1);`.
   - On |000>, this yields `X` on p0 -> |010>, then `CNOT` -> |011>.
   - Overall state: 1/sqrt(2) (|011> + |110>)
4. Measurement: `M(p[1]); M(p[0]);`
   Wait, the measurement order is p[1] then p[0].
   In `--probs` output, earlier measured qubit = higher bit.
   So p[1] is the MSB (bit 1), p[0] is the LSB (bit 0).
   Let's trace p[1] and p[0] for the two terms in the superposition:
   Term 1: c=0, p[1]=1, p[0]=1 -> state is |011> (order c, p0, p1). Wait!
   Let's re-evaluate INC and DEC carefully.
   Initial: c[0]=|0>, p[0]=|0>, p[1]=|0>. State is |0>_c |00>_p
   `H(c[0])` -> 1/sqrt(2) (|0> + |1>) |00>
   
   `ctrl INC(c[0], p[0], p[1])`:
   When c[0]=|1>, INC(p[0], p[1]) is applied.
   INC does: `CNOT(p[0], p[1]); X(p[0]);`
   |1>|00> -> |1> CNOT(p0,p1)|00> -> |1>|00> -> |1> X(p0)|00> -> |1>|10>
   So state is 1/sqrt(2) (|0>|00> + |1>|10>)

   `nctrl DEC(c[0], p[0], p[1])`:
   When c[0]=|0>, DEC(p[0], p[1]) is applied.
   DEC does: `X(p[0]); CNOT(p[0], p[1]);`
   |0>|00> -> |0> X(p0)|00> -> |0>|10> -> |0> CNOT(p0,p1)|10> -> |0>|11>
   So state is 1/sqrt(2) (|0>|11> + |1>|10>)
   In terms of c, p0, p1: 1/sqrt(2) (|011> + |110>)
   
   We measure p[1] then p[0].
   The bits measured are p[1] and p[0].
   For |011>, p[1]=1, p[0]=1. Measurement bitstring = 11 (binary).
   For |110>, p[1]=1, p[0]=0. Measurement bitstring = 10 (binary).
   Wait! the predicted output in the prompt are: {|01>: 0.5, |11>: 0.5}
   Let's re-read the qubit order in INC and DEC.
   `ctrl INC(c[0], p[0], p[1]);`
   INC definition: `CNOT(p0, p1); X(p0);`
   If initial is |0>|00> + |1>|00>
   ctrl INC on |1>|00>:
   CNOT(p0, p1)|00> = |00>
   X

## isqTrain/2916

- task_id: `isqTrain/2916`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2053`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```isq
import std;
oracle bool[1] g(bool a[4]) {
    bool s[] = [false, true, true, true];
    bool ba[] = s & a;
    bool res[1];
    res[0] = ba[0] != ba[1] != ba[2] != ba[3];
    return res;
}
qbit q[4];
qbit anc[1];

procedure main() {
    X(anc);
    H(anc);
    // H(q); // BUG: missing Hadamard
    g(q, anc);
    H(q);
    for i in 0:4 {
        M(q[i]);
    }
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug**: The Hadamard gate `H(q)` applied to the input register `q` before the oracle call `g(q, anc)` is commented out. In the Bernstein-Vazirani algorithm, the input register must be in an equal superposition of all states (|+>|+>...|+>) to evaluate the oracle function across all possible inputs simultaneously via quantum parallelism.

2. **The fix**: Uncomment `H(q);` before the `g(q, anc);` call to initialize the input qubits into the |+> state.

3. **State evolution**: 
- Initialize ancilla to |-> and input register to |0>|0>|0>|0> using `X(anc)` and `H(anc)`.
- Apply `H(q)` to create superposition: (|+>)^4 |->.
- Apply oracle `g(q, anc)`, which phase-kicks the secret string `s=0111` onto the input register state: (1/2) * Sum_x (-1)^(s.x) |x> |->.
- Apply `H(q)` to the input register, mapping the phase-encoded string to the computational basis: |0111> |->.
- Measurement of `q` deterministically yields `0111`.

## isqTrain/32

- task_id: `isqTrain/32`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `interference`, `isq_syntax_arrays`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `332`

### Prompt

Help me write isQ code that implements the oracle_boolean pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants a reasoning section for a Bernstein-Vazirani (BV) algorithm implementation in isQ.

1.  **Goal:** Implement the Bernstein-Vazirani oracle for the secret string $s=1111$ and demonstrate gate cancellation awareness with an X-X pair.
2.  **Qubits:** 5 qubits total ($q[0]$ to $q[4]$). The first 4 ($q[0]$ to $q[3]$) are measured to retrieve the secret string. $q[4]$ is the ancilla.
3.  **State Evolution:**
    *   Initial state: $|00000\rangle$.
    *   X($q[4]$): Flips ancilla to $|00001\rangle$.
    *   H on all: Creates superposition $|+\rangle|+\rangle|+\rangle|+\rangle|-\rangle$ or $\frac{1}{4} \sum_x |x\rangle |-\rangle$.
    *   CNOTs: The CNOTs with $q[0], q[1], q[2], q[3]$ as controls and $q[4]$ as target implement the inner product $s \cdot x \pmod 2$ for $s=1111$. This maps $\sum_x (-1)^{x \cdot s} |x\rangle |-\rangle$. Essentially, it entangles the phase.
    *   H on inputs ($q[0]$ to $q[3]$): The Hadamard transform converts the phase encoding back to the computational basis. Since the phase was $(-1)^{x \cdot 1111}$, applying H yields exactly $|1111\rangle$ for the first 4 qubits.
    *   X($q[0$]): Flips $q[0]$ to $|0\rangle$? Wait.
    Let's re-read the reference code.
    `H(q[0]); H(q[1]); H(q[2]); H(q[3]);`
    `X(q[0]);` then `X(q[0]);`
    Wait, the reference code applies X to $q[0]$ twice *after* the final H gates.
    Standard BV ends with measuring $|1111\rangle$.
    If X is applied to $q[0]$, it flips it. If X is applied again, it flips back.
    So $q[0]$ ends up in $|1\rangle$ (since X-X = Identity).
    So the state is $|1111\rangle$.
    Then measurements $M(q[0..3])$.
    So the result is `1111`.

    Let's verify the reference code steps:
    1. `X(q[4])` -> $|00001\rangle$
    2. `H` all -> $\sum |x\rangle |-\rangle$
    3. `CNOT`s -> $\sum (-1)^{x \cdot s} |x\rangle |-\rangle$ (where $s=1111$)
    4. `H(q[0..3])` -> $|1111\rangle |-\rangle$
    5. `X(q[0])` followed by `X(q[0])` -> Net Identity operation. State remains $|1111\rangle |-\rangle$.
    6. Measure $q[0..3]$ -> Outcome `1111` with probability 1.0.

    The question asks for reasoning.
    Constraints: 3-8 lines for simple, up to 15 for complex.
    Start with "## Reasoning".

    Lines:
    ## Reasoning
    1. **Goal:** Implements the Bernstein-Vazirani algorithm to find the secret string `s=1111` using a phase oracle, demonstrating that an explicit X-X pair is a gate cancellation (Identity).
    2. **Qubits:** 5 total ($q[0..4]$); $q[0..3]$ are measured.
    3. **Evolution:**
       - $|0^{\otimes 5}\rangle \xrightarrow{X(q_4)} |00001\rangle \xrightarrow{H^{\otimes 5}} \frac{1}{4}\sum_{x\in\{0,1\}^4} |x\rangle|-\rangle$.
       - The CNOT cascade computes the inner product $s \cdot x$: $\frac{1}{4}\sum_x (-1)^{1111 \cdot x}|x\rangle|-\rangle$.
       - Applying $H^{\otimes 4}$ to $q[0..3]$ converts the phase state back to the computational basis: $|1111\rangle|-\rangle$.
       - The explicit `X(q[0])` followed

## isqTrain/4101

- task_id: `isqTrain/4101`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1436`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the measurement output of an isQ circuit.
    *   Circuit:
        *   `X(q[0])` -> State $|100\rangle$
        *   `H(q[0])`
        *   `ctrl Rz(pi/2, q[1], q[0])` -> Wait, `2*pi/4 = pi/2`.
        *   `ctrl Rz(pi/4, q[2], q[0])` -> Wait, `2*pi/8 = pi/4`.
        *   `H(q[1])`
        *   `ctrl Rz(pi/2, q[2], q[1])` -> `2*pi/4 = pi/2`.
        *   `H(q[2])`
        *   `CNOT(q[0], q[2])`
        *   `CNOT(q[2], q[0])`
        *   `CNOT(q[0], q[2])`
    *   Format: "## Circuit Analysis", concise step-by-step reasoning, Dirac notation, up to 15 lines. End with predicted probability distribution.

2.  **Trace State Evolution:**
    *   Initial: $|000\rangle$.
    *   `X(q[0])`: $|100\rangle$.
    *   Wait, `H(q[0])` on $|1\rangle$ gives $|-\rangle$.
    *   State is $(|0\rangle - |1\rangle)/\sqrt{2} \otimes |00\rangle = \frac{1}{\sqrt{2}}(|000\rangle - |100\rangle)$.
    *   Let's carefully look at `ctrl Rz`. `isQ` syntax: `ctrl Rz(theta, control, target)`? Wait. Standard `ctrl` modifier: `ctrl Rz(theta, control_qubit, target)`?
    Let me check the syntax reference: `ctrl @[c1, c2] Gate(target);`
    The code uses `ctrl Rz(theta, q[1], q[0])`. This is equivalent to `CNOT(q[1], q[0])` in terms of control? No, `ctrl Rz(theta, q[1], q[0])` applies `Rz` to `q[0]` controlled on `q[1]`. Wait, the syntax `Rz(theta, target)` normally has 1 target. So `ctrl Rz(theta, q[1], q[0])` means control is `q[1]`, target is `q[0]`. But wait! Is it?
    In isQ, `ctrl Rz(theta, control, target)`? Let me re-read typical isQ syntax or infer.
    Usually, `ctrl G(c, t)` might mean `c` is control, `t` is target. Wait, `ctrl` operates on the *first* qubit?
    Let's look at `ctrl @[c1, c2] Gate(target)`. So `ctrl Rz(..., q[1], q[0])` has control `q[1]` and target `q[0]`. Actually, in isQ, if you write `ctrl Gate(c, t)`, `c` is the control, `t` is the target. Wait, if it's `ctrl Rz(theta, q1, q0)`, then `q1` is the control, `q0` is the target.
    Wait, in QFT, we apply controlled phase from $q_i$ to $q_j$. Let's see if this is QFT.
    `H(q[0])`
    `ctrl Rz(pi/2, q[1], q[0])`
    `ctrl Rz(pi/4, q[2], q[0])`
    `H(q[1])`
    `ctrl Rz(pi/2, q[2], q[1])`
    `H(q[2])`
    This is EXACTLY the Quantum Fourier Transform (QFT) on 3 qubits!
    Wait, in QFT, the matrix applies phases. Let's check the order. Standard QFT applies controlled rotations on $|1\rangle$.
    Wait, the initial state was $|100\rangle = |1\rangle \otimes |0\rangle \otimes |0\rangle$. So it's the state $|1\rangle$ in the computational basis for the first qubit, but wait, the qubits are $q[0], q[1], q[2]$.
    If we apply QFT to $|100\rangle$ (which is $|1\rangle$ in 3-qubit space), QFT of $|1\rangle$

### Reference answer

Uniform distribution across 8 states

## isqTrain/970

- task_id: `isqTrain/970`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4004`

### Prompt

I need an isQ program to implements the lie_trotter pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this Lie-Trotter circuit step by step.

The goal is to implement the Lie-Trotter decomposition for $e^{-itH}$ where H involves ZZ and XX interactions, using CZ gates instead of CNOT gates.

Starting state: |00⟩
After X(q[0]): |10⟩

**Step 1: e^{-it*ZZ} with t = π/8**

The standard ZZ evolution uses CNOT to compute parity. Here we use CNOT → H CZ H decomposition.

The ZZ evolution $e^{-itZZ}$ can be implemented as:
- CNOT(q[0], q[1])
- Rz(2t, q[1])
- CNOT(q[0], q[1])

Since CNOT = (I⊗H) CZ (I⊗H), we replace each CNOT with H-CZ-H.

So the ZZ part becomes:
- H(q[1])
- CZ(q[0], q[1])
- H(q[1])
- Rz(2t, q[1]) = Rz(π/4)
- H(q[1])
- CZ(q[0], q[1])
- H(q[1])

**Step 2: e^{-it*XX} with t = π/8**

XX evolution: H⊗H applied, then ZZ evolution, then H⊗H

- H(q[0]); H(q[1])
- Then same ZZ pattern:
  - H(q[1]); CZ(q[0],q[1]); H(q[1])
  - Rz(π/4, q[1])
  - H(q[1]); CZ(q[0],q[1]); H(q[1])
- H(q[0]); H(q[1])

Let me trace the state evolution:

Initial: |00⟩
After X(q[0]): |10⟩

Step 1: e^{-itZZ}
H(q[1]): |10⟩ (q[1] is |0⟩, H|0⟩ = |+⟩, but wait - q[1] is the second qubit which is |0⟩)
State: |1⟩⊗|+⟩ = (|10⟩ + |11⟩)/√2

CZ(q[0], q[1]): applies Z to q[1] when q[0]=|1⟩
(|10⟩ - |11⟩)/√2 = |1⟩⊗|−⟩

H(q[1]): |1⟩⊗|1⟩ = |11⟩

Rz(π/4, q[1]): e^{-iπ/8}|11⟩

H(q[1]): e^{-iπ/8}|1⟩⊗|−⟩ = e^{-iπ/8}(|10⟩ - |11⟩)/√2... wait, let me be more careful.

Actually, wait. Let me reconsider. Rz(θ)|0⟩ = |0⟩, Rz(θ)|1⟩ = e^{-iθ/2}|1⟩... no.

Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

So Rz(θ)|0⟩ = e^{-iθ/2}|0⟩, Rz(θ)|1⟩ = e^{iθ/2}|1⟩

Hmm, but the convention might differ. Let me use the standard: Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}).

Let me redo this more carefully.

State after X(q[0]): |10⟩

ZZ evolution: e^{-itZZ} where t = π/8
e^{-itZZ}|ab⟩ = e^{-it(-1)^{a+b}}|ab⟩ when we think of ZZ eigenvalues...

Actually, ZZ|ab⟩ = (-1)^{a⊕b}|ab⟩... no.

ZZ = Z⊗Z. Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩.
So ZZ|00⟩ = |00⟩, ZZ|01⟩ = -|01⟩, ZZ|10⟩ = -|10⟩, ZZ|11⟩ = |11⟩.

So eigenvalues: |00⟩→+1, |01⟩→-1, |10⟩→-1, |11⟩→+1.

e^{-itZZ}|10⟩ = e^{it}|10⟩ (eigenvalue -1, so e^{-it(-1)} = e^{it})

With t = π/8: e^{iπ/8}|10⟩

Now XX evolution: e^{-itXX}
First basis change: H⊗H
H|1⟩ = |−⟩, H|0⟩ = |+⟩
H⊗H|10⟩ = |−⟩⊗|+⟩ = (|0⟩-|1⟩)/√2 ⊗

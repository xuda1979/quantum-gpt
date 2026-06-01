# ISQ training COT RAG corpus: quantum_algorithms shard 126

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/44

- task_id: `isqExpand/algo/44`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `qpe`, `s_gate`, `inverse_qft`, `phase_estimation`
- source: `isq_expansion`
- dataset_index: `1556`

### Prompt

帮我写一个isQ程序：implements Quantum Phase Estimation (QPE) to estimate the phase of the S gate acting on its eigenstate |1>. Use 2 phase qubits (q[0] as MSB, q[1] as LSB) and 1 eigenstate qubit (q[2]). The S gate has eigenvalue i for |1>, corresponding to phase 1/4. Implement the inverse QFT and SWAP using CNOT gates. Only measure q[0] and q[1].

### Chain-of-thought reasoning

## Reasoning
Goal: QPE to estimate phase of S gate on eigenstate |1>.

S|1> = i|1> = e^{i*pi/2}|1>, so phase phi = (pi/2)/(2*pi) = 1/4.

With 2 phase qubits, the result encodes phi * 2^2 = 1 = binary |01>.

Circuit design:
1. H(q[0]), H(q[1]): superposition
2. X(q[2]): prepare eigenstate |1>
3. Controlled operations (q[0]=MSB):
   - q[0] controls U^{2^1} = S^2 = Z: ctrl @[q[0]] Z(q[2])
   - q[1] controls U^{2^0} = S^1 = S: ctrl @[q[1]] S(q[2])
4. Inverse QFT: H(q[0]), ctrl inv S(q[1], q[0]), H(q[1]), SWAP
5. Measure q[0], q[1]

Both phase qubits receive phase kicks. After inverse QFT and SWAP, the result is |01> with probability 1, correctly encoding phase = 1/4.

## isqTrain/1275

- task_id: `isqTrain/1275`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `64`

### Prompt

帮我写一个isQ程序：implements a variant of the simon_algorithm pattern using out[3] -> out[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to generate reasoning for a Simon's algorithm implementation with specific requirements:
- Uses out[3] -> out[5] (output register from index 3 to 5, so 3 output qubits)
- Expanded qubit register compared to base version (additional qubits in ground state)
- Period s = 100 (binary)

Let me trace through the circuit:

1. Goal: Implement Simon's algorithm with period s = 100, using an expanded register

2. Qubits: The base Simon's algorithm uses 3 input qubits and 3 output qubits. With the "significantly expanded" register, we need more qubits. The output uses out[3] -> out[5], suggesting out has at least 6 qubits (indices 0-5).

Wait, Analyzing the circuit requirements more carefully:
- qbit q[3] - input register (3 qubits)
- qbit out[5] - output register (5 qubits)

But the oracle f returns bool[3] and uses out as target. The reference shows out[5] being declared.

Let me re-read: "out[3] -> out[5]" means the oracle writes to out[3], out[4], out[5]? That's 3 output qubits.

Actually Analyzing the code again:
- f(q, out) - this queries the oracle
- The oracle signature: oracle bool[3] f(bool x[3]) returns 3 boolean values

So the oracle computation writes to 3 qubits of the out register.

The "significantly expanded" register with "additional qubits left in ground state" means we have extra qubits that don't participate in the computation.

Now let me trace the quantum states:

Initial state: |000⟩_q ⊗ |00000⟩_out

After H(q[0]); H(q[1]); H(q[2]):
|+++⟩_q ⊗ |00000⟩_out = (1/√8) Σ_x |x⟩ ⊗ |00000⟩

After f(q, out):
The oracle computes f(x) into the output register. Since f(x) = [x[0], x[1], false], the output qubits (which ones exactly?) get the function values.

Wait, the oracle in isQ works differently. Looking at the syntax, when you call f(q, out), it performs the transformation |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩.

The output register has 5 qubits, but only 3 are used by the oracle (indices 3, 4, 5 based on "out[3] -> out[5]").

Actually, I need to reconsider. The circuit should out[5] but the oracle returns bool[3]. The oracle automatically maps to the first 3 qubits of out unless specified otherwise. But the prompt says "out[3] -> out[5]" which suggests using qubits out[3], out[4], out[5].

Hmm, let me just work with The implementation as given:
- 3 input qubits (q[0], q[1], q[2])
- 5 output qubits (out[0] to out[4])

But only 3 of the output qubits are actually used by the oracle, leaving 2 in ground state.

After Hadamards on input: (1/√8) Σ_x |x⟩|0...0⟩

After oracle f: (1/√8) Σ_x |x⟩|f(x)⟩ (plus extra |0⟩s for unused output qubits)

Since f(x) = f(x ⊕ 100), pairs (x, x⊕100) give same output.

The function values:
- f(000) = [0, 0, 0]
- f(001) = [0, 0, 0] 
- f(010) = [0, 1, 0]
- f(011) = [0, 1, 0]
- f(100) = [1, 0, 0]
- f(101) = [1, 0, 0]
- f(110) = [1, 1, 0]
- f(111) = [1, 1, 0]

After oracle, we get:
(1/√8)(|000⟩ + |001⟩)|000⟩ + (1/√8)(|010⟩ + |011⟩)|010⟩ + (1/√8)(|100⟩ + |101⟩)|100⟩ + (1/√8)(|110⟩ + |111⟩)|110⟩

Now applying Hadamard to input qubits again. The key insight is that we can trace out the output register since it's not measured. The state after tracing out output

## isqTrain/3615

- task_id: `isqTrain/3615`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3774`

### Prompt

实现以下量子计算任务（使用isQ）：a 3-qubit Grover search for target state |101> using 2 Grover iterations for higher amplification. The circuit:
1. Initialize 3 qubits in superposition
2. Apply oracle+diffusion twice
3. Measure all qubits
Use `deriving gate` for oracle and diffusion procedures.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement 3-qubit Grover search targeting |101⟩ with 2 iterations for amplified probability.

Qubits: 3 (q[0], q[1], q[2]), all measured.

State evolution:
1. **Initialize**: |000⟩ → H⊗3 → |s⟩ = (1/√8)Σ|x⟩, uniform superposition over 8 states
2. **Oracle**: X(q[1]) transforms |101⟩↔|111⟩, ctrl CZ flips |111⟩ phase, X(q[1]) restores → |101⟩ gets -1 phase
3. **Diffusion 1**: Reflects state about mean |s⟩, amplifying |101⟩ amplitude. Amplitude of target: sin(3θ/2) where sin(θ/2)=1/√8
4. **Oracle+Diffusion 2**: Second amplification. Target amplitude becomes sin(5θ/2)≈0.972
5. **Final state**: |101⟩ has amplitude ≈0.972 (probability ≈0.945), other states ≈0.088 amplitude each (probability ≈0.0078 each)

Expected probabilities follow from sin²(5θ/2) for |101⟩≈0.9453, with remaining ~0.055 distributed equally among 7 non-target states (~0.0078 each).

## isqTrain/4122

- task_id: `isqTrain/4122`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `3734`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[4];

procedure main() {
    X(q[1]);
    X(q[3]);

    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    H(q[3]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of an isQ quantum circuit to predict the measurement output and probability distribution. The analysis should be concise, use Dirac notation, and follow specific formatting rules.

2.  **Analyze the Circuit:**
    *   Qubits: `q[0], q[1], q[2], q[3]`. Initial state: $|0000\rangle$.
    *   `X(q[1]); X(q[3]);`: State becomes $|1010\rangle$ (in $q_3 q_2 q_1 q_0$ order: $q_3=1, q_2=0, q_1=1, q_0=0$).
        Wait, standard index order is $q_3 q_2 q_1 q_0$ or $q_0 q_1 q_2 q_3$. Let's trace carefully:
        $q_0 = 0, q_1 = 1, q_2 = 0, q_3 = 1$.
        So state is $|q_3 q_2 q_1 q_0\rangle = |1010\rangle$.
    *   Next we have a sequence of CNOTs.
        *   `CNOT(q[0], q[3]); CNOT(q[3], q[0]); CNOT(q[0], q[3]);`
            Since $q_0 = 0$ and $q_3 = 1$:
            CNOT(q0, q3) -> control=0, target=1 -> q3 becomes 1 XOR 0 = 1. State: $|1010\rangle$
            CNOT(q3, q0) -> control=1, target=0 -> q0 becomes 0 XOR 1 = 1. State: $|1011\rangle$
            CNOT(q0, q3) -> control=1, target=1 -> q3 becomes 1 XOR 1 = 0. State: $|0011\rangle$
        *   `CNOT(q[1], q[2]); CNOT(q[2], q[1]); CNOT(q[1], q[2]);`
            Since $q_1 = 1$ and $q_2 = 0$:
            CNOT(q1, q2) -> control=1, target=0 -> q2 becomes 0 XOR 1 = 1. State: $|0111\rangle$
            CNOT(q2, q1) -> control=1, target=1 -> q1 becomes 1 XOR 1 = 0. State: $|0101\rangle$
            CNOT(q1, q2) -> control=0, target=1 -> q2 becomes 1 XOR 0 = 1. State: $|0101\rangle$
        Wait, let's re-verify the swap (three-CNOT decomposition)-like sequence.
        CNOT(c, t); CNOT(t, c); CNOT(c, t) swaps c and t.
        Initial: q0=0, q3=1. Swap them -> q0=1, q3=0.
        Initial: q1=1, q2=0. Swap them -> q1=0, q2=1.
        So after swaps: $q_3=0, q_2=1, q_1=0, q_0=1$.
        State is $|0101\rangle$.
    *   Next gates: This looks like a Quantum Fourier Transform (QFT) applied in reverse order or some specific permutation of it, or actually an inverse QFT. Let's trace the QFT definition.
        Standard QFT (high-to-low index):
        For each qubit $i$ (from $N-1$ down to 0):
            H(q[i])
            for each qubit $j$ (from $i-1$ down to 0):
                ctrl Rz( -2*pi / 2^(i-j+1), q[i], q[j] )
        Wait, let's look at the circuit's structure:
        `H(q[3])`
        `ctrl Rz(-pi/2, q[3], q[2])`
        `H(q[2])`
        `ctrl Rz(-pi/4, q[3], q[1])`
        `ctrl Rz(-pi/2, q[2], q[1])`
        `H(q[1])`
        `ctrl Rz(-pi/8, q[3], q[0])`
        `ctrl Rz(-pi/4, q[2], q[0])`
        `ctrl Rz(-pi/2, q[1], q[0])`
        `H

### Reference answer

Uniform distribution across 16 states

## isqTrain/1385

- task_id: `isqTrain/1385`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5771`

### Prompt

实现以下量子计算任务（使用isQ）：the Bernstein-Vazirani algorithm to find the secret string s = 01 (MSB first). Use 2 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Implement Bernstein-Vazirani algorithm to find secret string s=01 using phase kickback.
2. **Qubits:** 2 input qubits (q[0], q[1]) and 1 ancilla (anc[0]). Only input qubits are measured.
3. **State evolution:**
   - Initialize to |00>|1>, apply H to ancilla: |00>|->
   - Apply H to input register: (1/2)Σ|x>|-> where x∈{0,1}²
   - Oracle CNOT(q[1], anc[0]) adds phase (-1)^(s·x): (1/2)Σ(-1)^(s·x)|x>|->
   - Since s=01, only |x> states with x[1]=1 get phase flip
   - Final H on input register transforms superposition to |01>|->
4. **Probabilities:** Input register collapses to |01> with certainty, yielding measurement probabilities {|01>: 1.0}

## isqTrain/2903

- task_id: `isqTrain/2903`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3513`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
oracle bool[1] f_const(bool a[3]) {
    bool res[] = [true];
    return res;
}
qbit q[3], anc[1];
procedure main() {
    X(anc[0]);
    H(anc[0]);
    for i in 0:3 {
        H(q[i]);
    }
    f_const(q, anc);
    for i in 0:3 {
        H(q[i]);
    }
    for i in 0:3 {
        M(q[i]);
    }
    M(anc[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction for a given isQ program.
    *   Format: Markdown starting with "## Circuit Analysis".
    *   Content: Step-by-step reasoning using Dirac notation, quantum state evolution, final state, and probability distribution.
    *   Constraints: 3-8 lines for simple, up to 15 for complex. Be concise and precise.

2.  **Analyze the isQ Code:**
    *   `oracle bool[1] f_const(bool a[3]) { bool res[] = [true]; return res; }` -> This is a constant oracle. It always returns 1. Wait, how does it act on qubits?
    *   In isQ, an oracle acting on `q` and `anc` where the function returns `1` does a phase shift or a bit flip?
    *   Normally, `f_const` acts as $U_f |x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle$. If it's a standard oracle, $f(x) = 1$.
    *   Let's trace `f_const(q, anc)`. The order is `q[3], anc[1]`. So inputs are `q`, `anc` is the target.
    *   If $f(x) = 1$, then $y \oplus f(x) = y \oplus 1$, which is exactly applying an X gate to the target `anc` unconditionally.
    *   Wait, the isQ oracle syntax defines `f_const(q, anc)` where `q` corresponds to `a[3]` and `anc` to the return target.
    *   Initial state: $|0000\rangle$ (q[0], q[1], q[2], anc[0]). Let's use $|x\rangle_3 |y\rangle_1$.
    *   Operations on `anc[0]`:
        *   `X(anc[0])` -> $|0001\rangle$
        *   `H(anc[0])` -> $|000\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |000\rangle|-\rangle$.
    *   Operations on `q[0..2]`:
        *   `H(q[0..2])` -> Creates superposition over all $|x\rangle$. State is $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle|-\rangle$.
    *   Oracle `f_const(q, anc)`:
        *   Since $f(x)=1$, it maps $|x\rangle|y\rangle \to |x\rangle|y \oplus 1\rangle$.
        *   In the $|-\rangle$ basis, $y \oplus 1$ flips $|0\rangle$ to $|1\rangle$ and $|1\rangle$ to $|0\rangle$, which is $X|-\rangle = -|-\rangle$.
        *   So the state becomes $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle (-|-\rangle) = -\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle|-\rangle$.
        *   Wait, is it phase oracle or bit oracle? isQ standard oracle applies $U_f|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle$. Thus $|-\rangle$ gets a phase of $(-1)^{f(x)}$. Since $f(x)=1$, it's $-1$. So the state is $-\frac{1}{\sqrt{8}} \sum_{x} |x\rangle|-\rangle$.
    *   Operations on `q[0..2]`:
        *   `H(q[0..2])` applied to $\sum_{x} |x\rangle$ results in $|000\rangle$. (Standard Deutsch-Jozsa constant function outcome).
        *   State becomes $-|000\rangle|-\rangle = -\frac{1}{\sqrt{2}} |0000\rangle + \frac{1}{\sqrt{2}} |0001\rangle$.
    *   Measurements:
        *   `M(q[i])` measures q[0], q[1], q[2] in the $|000\rangle$ state. Outcomes are all 0.
        *   `M(anc[0])` measures the ancilla in $|-\rangle$. Probability of 0 is 0.5, probability

### Reference answer

{'predicted_probs': {'0000': 0.5, '0001': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2035

- task_id: `isqTrain/2035`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `isq_syntax_deriving_gate`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1112`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
procedure swap_gate(qbit a, qbit b) {
    CNOT(a, b);
    CNOT(b, a);
    CNOT(a, b);
} deriving gate
qbit q[3];
procedure main() {
    X(q[1]);
    ctrl swap_gate(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a concise step-by-step quantum circuit analysis of the provided isQ code, followed by the predicted probability distribution of the measurements.

2.  **Analyze the isQ code**:
    *   `qbit q[3];`: 3 qubits initialized to $|000\rangle$.
    *   `X(q[1]);`: Apply X gate to $q_1$. State becomes $|010\rangle$.
    *   `ctrl swap_gate(q[0], q[1], q[2]);`: Wait, let's look closely at the syntax `ctrl swap_gate(q[0], q[1], q[2])`. The `swap_gate(a, b)` takes 2 arguments. If we do `ctrl swap_gate(q[0], q[1], q[2])`, the first argument acts as the control, and the rest are passed to the gate. BUT the syntax usually is `ctrl Gate(control, target)` or similar. Actually, in isQ, `ctrl swap_gate(q[0], q[1], q[2])` means `q[0]` is the control qubit, and `swap_gate(q[1], q[2])` is the controlled operation.
    *   Let's check the state of `q[0]`: It is $|0\rangle$.
    *   Since `q[0]` is $|0\rangle$, a controlled operation with `q[0]` as the control will *not* trigger. The state remains $|010\rangle$.
    *   Let's double check standard isQ syntax: `ctrl @[c] Gate(t);` or just `ctrl Gate(c, t)`. When passing 3 qubits to `ctrl swap_gate`, `q[0]` is the control, `q[1]` and `q[2]` are the targets of the swap gate. Because `q[0]` is $|0\rangle$, the controlled-swap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)) does nothing.
    *   Measurement: `M(q[0]); M(q[1]); M(q[2]);`
    *   The system will measure $|010\rangle$ with probability 1.0.

3.  **Format the Output**:
    *   "## Circuit Analysis"
    *   Steps: 3-8 lines.
    *   Use Dirac notation.
    *   End with "Predicted probability distribution: {'010': 1.0}"

4.  **Drafting the steps**:
    *   Initial state: $|q_0 q_1 q_2\rangle = |000\rangle$.
    *   Apply `X(q[1])`: Flips $q_1$ to 1, state becomes $|010\rangle$.
    *   Apply `ctrl swap_gate(q[0], q[1], q[2])`: This applies a controlled-swap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)) where $q_0$ is the control and $q_1, q_2$ are the targets.
    *   Since $q_0$ is in state $|0\rangle$, the controlled-swap operation (three-CNOT decomposition) does not execute.
    *   Final state remains $|010\rangle$.
    *   Measurement outcomes: Measuring all three qubits yields $|010\rangle$ with certainty.

5.  **Refining according to constraints**:
    *   Concise, 3-8 lines.
    *   No code blocks.
    *   Ends with prediction.

    Draft:
    ## Circuit Analysis
    1. The circuit initializes 3 qubits to the state $|000\rangle$.
    2. `X(q[1])` flips the second qubit, changing the state to $|010\rangle$.
    3. `ctrl swap_gate(q[0], q[1], q[2])` applies a controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) gate with $q_0$ as the control and $q_1, q_2$ as the targets.
    4. Since the control qubit $q_0$ is in the state $|0\rangle$, the gate does not apply the swap operation (three-CNOT decomposition).
    5. The final quantum state before measurement is $|010\rangle$.
    6. Measurement of the qubits will deterministically yield the bitstring '010'.

    Predicted probability distribution: {'010': 1.0}

6.  **Final sanity check**:
    Does `ctrl swap_gate(q[0], q[1], q[2])` mean `q[0]` is control? Yes, in isQ `ctrl gate(c, t)` means `c` is the new control, and `t` goes to the gate. If gate

### Reference answer

{'predicted_probs': {'010': 1.0}, 'explanation': 'Fredkin: control=0, no swap. State |010>, P=1.0.'}

## isqTrain/987

- task_id: `isqTrain/987`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4908`

### Prompt

Implement a quantum circuit in isQ: implements the suzuki_trotter pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit implements a second-order Suzuki-Trotter decomposition S2(t) for t = π/8, applied to initial state |10⟩, with reversed measurement order.

Starting state: |10⟩

The Suzuki-Trotter pattern S2(t) = e^(-i*t/2*ZZ) * e^(-i*t*XX) * e^(-i*t/2*ZZ)

Let me trace through:

1. Initial state: |10⟩ (after X(q[0]))

2. First ZZ half-step (t/2 = π/16):
   - CNOT(q[0], q[1]): |10⟩ → |11⟩
   - Rz(π/8, q[1]): |11⟩ → e^(-iπ/16)|11⟩
   - CNOT(q[0], q[1]): e^(-iπ/16)|11⟩ → e^(-iπ/16)|10⟩

Wait, let me recalculate. Rz(θ) adds a phase of e^(-iθ/2) to |0⟩ and e^(iθ/2) to |1⟩.

Actually, Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]

So after CNOT, state is |11⟩. Rz(0.392699..., q[1]) applies to qubit 1.
|11⟩ → e^(i*0.392699/2)|11⟩ = e^(i*π/16)|11⟩

Hmm, but there's also the global phase consideration. Let me just track the state.

Actually, the ZZ interaction e^(-i*θ*ZZ/2) can be decomposed as CNOT-Rz(2θ)-CNOT on the target.

Wait, let me re-derive. e^(-i*θ*Z⊗Z) = exp(-iθ(Z⊗Z))

The decomposition is:
CNOT(c,t) * (I⊗Rz(2θ)) * CNOT(c,t) = e^(-iθ*Z⊗Z)

So for e^(-i*(t/2)*ZZ), we need Rz(t) = Rz(π/8) = Rz(0.392699...)

Let me trace through more carefully:

Initial: |10⟩

First half ZZ step:
- CNOT(q[0], q[1]): |10⟩ → |11⟩
- Rz(π/8, q[1]): |11⟩ → e^(iπ/16)|11⟩ (since Rz(θ)|1⟩ = e^(iθ/2)|1⟩)
- CNOT(q[0], q[1]): e^(iπ/16)|10⟩

Full XX step:
- H(q[0]); H(q[1]): e^(iπ/16)|10⟩ → e^(iπ/16) * H|1⟩⊗H|0⟩ = e^(iπ/16) * |-⟩⊗|+⟩ 
  = e^(iπ/16) * (|0⟩-|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2
  = e^(iπ/16)/2 * (|00⟩+|01⟩-|10⟩-|11⟩)

- CNOT(q[0], q[1]): 
  |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩
  = e^(iπ/16)/2 * (|00⟩+|01⟩-|11⟩-|10⟩)
  = e^(iπ/16)/2 * (|00⟩+|01⟩-|10⟩-|11⟩)

- Rz(π/4, q[1]):
  |00⟩→e^(-iπ/8)|00⟩, |01⟩→e^(iπ/8)|01⟩, |10⟩→e^(-iπ/8)|10⟩, |11⟩→e^(iπ/8)|11⟩
  = e^(iπ/16)/2 * (e^(-iπ/8)|00⟩+e^(iπ/8)|01⟩-e^(-iπ/8)|10⟩-e^(iπ/8)|11⟩)

- CNOT(q[0], q[1]):
  = e^(iπ/16)/2 * (e^(-iπ/8)|00⟩+e^(iπ/8)|01⟩-e^(-iπ/8)|11⟩-e^(iπ/8)|10⟩)

- H(q[0]); H(q[1

## isqTrain/691

- task_id: `isqTrain/691`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2109`

### Prompt

帮我写一个isQ程序：implements a variant of the half_full_adder pattern using q[5] -> q[7]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Step 1: Understand the goal. The user wants an isQ program for a "half_full_adder" variant. Analyzing the circuit requirements, it implements a full adder using 7 qubits, where `q[0]`, `q[1]`, `q[2]` are inputs (all initialized to 1 using X gates), `q[3]` stores the sum, and `q[4]` stores the carry_out. `q[5]` and `q[6]` are additional qubits in an expanded register, left in the ground state.

Step 2: Analyze the quantum state evolution Based on the circuit design.
Initial state: |0000000>
After X(q[0]), X(q[1]), X(q[2]): |1110000>
CNOT(q[0], q[3]): q[0]=1, so q[3] flips to 1. State: |1111000>
CNOT(q[1], q[3]): q[1]=1, so q[3] flips to 0. State: |1110000>
CNOT(q[2], q[3]): q[2]=1, so q[3] flips to 1. State: |1111000> (Sum = 1)
Toffoli(q[0], q[1], q[4]): q[0]=1, q[1]=1, so q[4] flips to 1. State: |1111100>
Toffoli(q[0], q[2], q[4]): q[0]=1, q[2]=1, so q[4] flips to 0. State: |1111000>
Toffoli(q[1], q[2], q[4]): q[1]=1, q[2]=1, so q[4] flips to 1. State: |1111100> (Carry = 1)
Measure q[3], q[4], q[5], q[6]. These are in states 1, 1, 0, 0 respectively.

Step 3: Map to the output bitstring.
Earlier measured qubit = higher bit.
Order of measurement: q[3], q[4], q[5], q[6].
Values: q[3]=1, q[4]=1, q[5]=0, q[6]=0.
Bitstring: 1100.
Wait, let's re-verify the Toffoli majority gate logic.
Actually, The circuit should:
Toffoli(q[0], q[1], q[4]);
Toffoli(q[0], q[2], q[4]);
Toffoli(q[1], q[2], q[4]);
If q[4] starts at 0:
q0=1, q1=1 => q4 = 1
q0=1, q2=1 => q4 = 1 XOR 1 = 0
q1=1, q2=1 => q4 = 0 XOR 1 = 1.
So q4 ends up as 1.
The output bitstring for q[3]q[4]q[5]q[6] is 1100, which perfectly matches the predicted output.

Wait, is the prompt asking me to WRITE the code or GENERATE REASONING for the code?
"Task type: code_generation" - Actually, the system prompt says:
"Generate a reasoning section that explains... Output ONLY the reasoning section, starting with "## Reasoning". Do NOT include the isQ code"

Let's write out the reasoning.

1. Goal: Implement a 7-qubit full adder circuit where inputs a=1, b=1, carry_in=1 are stored in q[0]-q[2], sum and carry_out in q[3]-q[4], with q[5]-q[6] as unused ground-state qubits.
2. Qubits: 7 qubits total. Inputs: q[0..2]. Outputs: q[3], q[4]. Unused: q[5..6]. Measured: q[3], q[4], q[5], q[6].
3. Evolution:
- Start: |0000000>
- Inputs: X(q[0..2]) -> |1110000>
- Sum logic: CNOTs flip q[3] based on q[0,1,2]. Three CNOTs apply XOR: 0 -> 1 -> 0 -> 1. State: |1111000>
- Carry logic: Toffoli gates on q[4] implement Majority via XOR: 0 -> 1 -> 0 -> 1. State: |1111100>
4. Probabilities: Measuring q[3]=1, q[4]=

## isqTrain/3645

- task_id: `isqTrain/3645`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `1644`

### Prompt

Code this in isQ: the 3-qubit inverse Quantum Fourier Transform (QFT†) on input |100>. Use bit-reversal swaps first, then apply inverse rotation stages with negative angles. Measure all qubits.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit implements the inverse Quantum Fourier Transform (QFT†) on 3 qubits with input |100>.

Initial state: |000>

After X(q[0]): |100>

Now the inverse QFT on 3 qubits. The QFT circuit typically works from qubit n-1 down to 0, applying H then controlled rotations with decreasing angles. The inverse QFT reverses this with negative angles.

For 3-qubit QFT† with bit-reversal:

The standard QFT for 3 qubits maps:
QFT|j⟩ = (1/√8) Σ_k e^{2πijk/8} |k⟩

So QFT† maps computational basis states back.

Actually, let me trace through the circuit more carefully.

Starting state: |100⟩ = |q[2]q[1]q[0]⟩ where q[0] is least significant bit.

Wait, I need to be careful about indexing. In the isQ code, q[0] gets X applied to prepare |100⟩. So if q[0] is the least significant bit, then |100⟩ means q[2]=1, q[1]=0, q[0]=0. But X(q[0]) sets q[0]=1.

Let me reconsider. The state |100⟩ in standard notation has the leftmost bit as the most significant. So |100⟩ = qubit 2 is 1, qubit 1 is 0, qubit 0 is 0.

But the code does X(q[0]), which would give us q[0]=1. So maybe in this context, q[0] corresponds to the leftmost (most significant) bit, meaning the state is |100⟩ with q[0]=1, q[1]=0, q[2]=0.

Let me trace through assuming q[0] is the most significant bit:
- After X(q[0]): |100⟩ (q[0]=1, q[1]=0, q[2]=0)

Now bit-reversal swaps. For 3 qubits, we swap q[0]↔q[2]:
- CNOT(q[0], q[2]): q[2] gets q[0]^q[2] = 1^0 = 1 → state |101⟩
- CNOT(q[2], q[0]): q[0] gets q[2]^q[0] = 1^1 = 0 → state |001⟩  
- CNOT(q[0], q[2]): q[2] gets q[0]^q[2] = 0^1 = 1 → state |011⟩

Hmm, that doesn't seem right for a simple swap. Let me reconsider.

Actually, CNOT swap sequence:
- CNOT(a, b): b = a XOR b
- CNOT(b, a): a = b XOR a  
- CNOT(a, b): b = a XOR b

Starting with a=1, b=0:
After CNOT(a,b): a=1, b=1
After CNOT(b,a): a=0, b=1
After CNOT(a,b): a=0, b=0

Wait, that's wrong. CNOT doesn't modify the control, only the target.

Starting: q[0]=1, q[2]=0
CNOT(q[0], q[2]): control=q[0]=1, target=q[2]. So q[2] = q[2] XOR q[0] = 0 XOR 1 = 1. State: q[0]=1, q[2]=1
CNOT(q[2], q[0]): control=q[2]=1, target=q[0]. So q[0] = q[0] XOR q[2] = 1 XOR 1 = 0. State: q[0]=0, q[2]=1
CNOT(q[0], q[2]): control=q[0]=0, target=q[2]. So q[2] unchanged = 1. State: q[0]=0, q[2]=1

So after swap: q[0]=0, q[1]=0, q[2]=1 → |001⟩

Now the inverse QFT stages (working from q[2] down to q[0]):

H(q[2]): Applied to |001⟩, H on q[2] (which is 1): |0⟩→|+⟩, |1⟩→|−⟩
So |001⟩ → |0,-⟩ = (|001⟩ - |000⟩)/√2 = (1/√2)(|001⟩ - |000⟩)

Wait, q[2] is the last qubit. If

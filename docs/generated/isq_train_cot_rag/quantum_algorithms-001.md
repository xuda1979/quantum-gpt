# ISQ training COT RAG corpus: quantum_algorithms shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3600

- task_id: `isqTrain/3600`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4557`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong rotation angle (doubled)

The program should QPE for Rz(pi/2), 3 precision qubits, theta=7/8.

### Chain-of-thought reasoning

Let me analyze this quantum phase estimation (QPE) circuit for Rz(pi/2).

The goal is to perform QPE for Rz(pi/2) with 3 precision qubits, where theta = 7/8.

First, let me understand the Rz gate:
Rz(θ) = [[1, 0], [0, e^(iθ)]]

Rz(pi/2) has eigenvalues 1 and e^(i*pi/2) = i.

The phase we want to estimate is pi/2, which in terms of 2*pi would be 1/4. But the problem states theta = 7/8. Let me think about this more carefully.

For Rz(θ), the eigenvalues are e^(±iθ/2) (with proper normalization). Wait, let me reconsider.

Actually, in many quantum computing frameworks:
Rz(θ) = e^(-iθ/2) * [[1, 0], [0, e^(iθ)]]

But the global phase doesn't matter for QPE. The eigenvalue for |1⟩ is e^(iθ) (ignoring global phase).

For Rz(pi/2), the eigenvalue for |1⟩ is e^(i*pi/2) = i.

The phase is pi/2 = 2*pi * (1/4), so φ = 1/4 in units of 2*pi.

With 3 precision qubits, we'd measure 0.25 * 8 = 2, which is |010⟩.

But The predicted output probability distribution, not a single state. This suggests there might be some noise or the problem is set up differently.

Wait, let me re-read: "theta=7/8". So the phase to estimate is 7/8 * 2*pi? That would be 7/4 * pi = 7*pi/4.

Hmm, but the controlled operations suggest Rz(pi/2)^4 = I (which means 4*pi/2 = 2*pi global phase... wait).

Let me think about this differently. The comment says "prec[0] controls Rz(pi/2)^4 = Rz(4.0*pi)". This suggests Rz(pi/2)^4 means applying Rz(pi/2) four times, which gives Rz(2*pi) = I (up to global phase).

Actually wait - Rz(pi/2)^4 = Rz(4 * pi/2) = Rz(2*pi). But Rz(2*pi) = -I (it's a rotation by 2*pi which gives a -1 phase in SU(2)). However, for controlled operations, this is effectively I.

And Rz(pi/2)^2 = Rz(pi) = Z (up to global phase).

So the controlled operations are:
- prec[0] controls Rz(pi/2)^4 → skipped (identity)
- prec[1] controls Rz(pi/2)^2 → ctrl Z
- prec[2] controls Rz(pi/2)^1 → ctrl Rz(pi/2)

This all looks correct in the buggy code.

Now let me look at the inverse QFT part. The QFT on 3 qubits is:
- Apply H to qubit 0
- Apply controlled R2 (rotation by 2*pi/2^2 = pi/2) from qubit 1 to qubit 0
- Apply H to qubit 1
- Apply controlled R2 from qubit 2 to qubit 0
- Apply controlled R3 (rotation by 2*pi/2^3 = pi/4) from qubit 2 to qubit 1
- Apply H to qubit 2

Wait, but there's also a swap at the beginning for the standard QFT. The inverse QFT would be:
- Swap qubits 0 and 2
- Apply H to qubit 2
- Apply controlled R3† from qubit 1 to qubit 2
- Apply controlled R2† from qubit 0 to qubit 2
- Apply H to qubit 1
- Apply controlled R2† from qubit 0 to qubit 1
- Apply H to qubit 0

But the code has:

CNOT(prec[0], prec[2]);
CNOT(prec[2], prec[0]);
CNOT(prec[0], prec[2]);
H(prec[0]);
ctrl Rz(-1.5707963267949, prec[1], prec[0]);
H(prec[1]);
ctrl Rz(-0.7853981633974, prec[2], prec[0]);
ctrl Rz(-1.5707963267949, prec[2], prec[1]);
H(prec[2

## isqTrain/881

- task_id: `isqTrain/881`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5194`

### Prompt

Implement the following in isQ: implements the inner_product_mod2 pattern but with a different initial state preparation (flip q[[0, 2, 3, 4]] -> q[6]).

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Goal:** Generate reasoning for a specific isQ quantum program implementing the `inner_product_mod2` pattern but with a different initial state preparation (flip `q[[0, 2, 3, 4]] -> q[6]`).
    *   **circuit implementation:** The prompt provides an isQ code snippet as a "circuit implementation", but wait, the prompt says "Prompt: Write an isQ program that implements the inner_product_mod2 pattern but with a different initial state preparation (flip q[[0, 2, 3, 4]] -> q[6])." and *then* gives a "circuit implementation". The implementation *doesn't* match the prompt's request (the reference code only flips `q[6]` with `X(q[6])`, not `q[[0, 2, 3, 4]] -> q[6]`). Wait, The implementation is just an example of the structure. Let me re-read carefully: "Write an isQ program that implements the inner_product_mod2 pattern but with a different initial state preparation (flip q[[0, 2, 3, 4]] -> q[6])."
    *   Wait, the task type is `code_generation`, but I am asked to "Generate a reasoning section that explains... Output ONLY the reasoning section".
    *   Let me deduce what the *actual* circuit described by the prompt would do, or if I should explain the *reference* solution? The prompt says: "Generate a reasoning section that explains: 1. The goal of the circuit 2. How many qubits... 3. Step-by-step quantum state evolution... 4. Why the predicted output..."
    *   The "circuit implementation" code actually sets `x=[1,0,1]` and `y=[1,1,0]`? No, it just flips `q[6]` at the start. Wait, if `q[6]` starts as 1, and then Toffoli gates XOR into it.
    *   Let's look at the "circuit implementation" again.
        *   `X(q[6])` -> q[6] is 1.
        *   `ctrl ctrl X(q[0], q[3], q[6])` -> XORs `q[0]*q[3]` into `q[6]`.
        *   `ctrl ctrl X(q[1], q[4], q[6])` -> XORs `q[1]*q[4]` into `q[6]`.
        *   `ctrl ctrl X(q[2], q[5], q[6])` -> XORs `q[2]*q[5]` into `q[6]`.
        *   But q[0], q[3], etc., are never initialized! They are all 0. So `q[0]*q[3]` = 0, `q[1]*q[4]` = 0, `q[2]*q[5]` = 0.
        *   XORing 0s into `q[6]` (which is 1) leaves it as 1.
        *   Measurement yields `|1>` with probability 1.0.
    *   Wait, the prompt says: "Write an isQ program that implements the inner_product_mod2 pattern but with a different initial state preparation (flip q[[0, 2, 3, 4]] -> q[6])."
    *   Does this mean the user wants me to explain the *reference* solution or the *prompt's* requested code? The prompt says "Generate a reasoning section that explains...". Usually, this is for The implementation provided in the prompt, but The implementation provided *doesn't* match the prompt text.
    *   Let's look at the "circuit implementation" code again.
        *   `qbit q[7];`
        *   `X(q[6]);`
        *   `ctrl ctrl X(q[0], q[3], q[6]);` (XOR `x[0]*y[0]` into IP)
        *   `ctrl ctrl X(q[1], q[4], q[6]);` (XOR `x[1]*y[1]` into IP)
        *   `ctrl ctrl X(q[2], q[5], q[6]);` (XOR `x[2]*y[2]` into IP)
        *   `M(q[6]);`
    *   The comment says `// Encode x = [1, 0, 1]` but there's no code for it (only `X(q[6])`).
    *   The comment says `// Encode y = [1

## isqTrain/742

- task_id: `isqTrain/742`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1272`

### Prompt

Write isQ code for the following quantum task: implements the qft_adder pattern with modified rotation parameters (num_pi2_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

The user wants me to analyze a quantum circuit that implements a QFT adder pattern with modified rotation parameters.

Let me trace through the circuit step by step:

1. Initial state: |00>
2. X(q[0]) → |10>
3. H(q[1]) → |1⟩⊗|+⟩ = (|10⟩ + |11⟩)/√2
4. ctrl S(q[0], q[1]) → When q[0]=|1⟩, apply S to q[1]
   S|+⟩ = (|0⟩ + i|1⟩)/√2
   So state becomes: |1⟩⊗(|0⟩ + i|1⟩)/√2 = (|10⟩ + i|11⟩)/√2
5. H(q[0]) → |+⟩⊗(|0⟩ + i|1⟩)/√2
   = (|00⟩ + i|01⟩ + |10⟩ + i|11⟩)/2

Wait, let me redo this more carefully.

Initial: |00⟩
After X(q[0]): |10⟩
After H(q[1]): |1⟩⊗|+⟩ = (|10⟩ + |11⟩)/√2
After ctrl S(q[0], q[1]): When q[0]=|1⟩, apply S to q[1]
  S = [[1,0],[0,i]]
  S|0⟩ = |0⟩, S|1⟩ = i|1⟩
  So (|10⟩ + |11⟩)/√2 → (|10⟩ + i|11⟩)/√2

After H(q[0]):
  |0⟩⊗(|0⟩ + i|1⟩)/2 + |1⟩⊗(|0⟩ + i|1⟩)/2
  Wait no...
  H on q[0]: |1⟩ → |−⟩ = (|0⟩ - |1⟩)/√2
  So (|10⟩ + i|11⟩)/√2 → ((|0⟩ - |1⟩)/√2 ⊗ |0⟩ + i(|0⟩ - |1⟩)/√2 ⊗ |1⟩)/√2
  = (|00⟩ - |10⟩ + i|01⟩ - i|11⟩)/2

Hmm, let me be more careful.

After X(q[0]): |10⟩ = |1⟩_0 ⊗ |0⟩_1

After H(q[1]): |1⟩_0 ⊗ (|0⟩ + |1⟩)/√2_1 = (|10⟩ + |11⟩)/√2

After ctrl S(q[0], q[1]):
  Controlled-S with q[0] as control and q[1] as target
  When q[0]=|1⟩, apply S to q[1]
  |10⟩ → |10⟩ (S doesn't change |0⟩)
  |11⟩ → i|11⟩ (S|1⟩ = i|1⟩)
  State: (|10⟩ + i|11⟩)/√2

After H(q[0]):
  H on qubit 0: |1⟩ → (|0⟩ - |1⟩)/√2
  So: ((|0⟩ - |1⟩)/√2 ⊗ |0⟩ + i(|0⟩ - |1⟩)/√2 ⊗ |1⟩)/√2
  = (|00⟩ - |10⟩ + i|01⟩ - i|11⟩)/2

Now apply phase rotations:
Rz(π, q[0]) = Z on q[0]
Rz(π/3, q[1]) on q[1]

Rz(π, q[0]): Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩
State: (|00⟩ + |10⟩ + i|01⟩ + i|11⟩)/2

Rz(π/3, q[1]):
Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]
Rz(π/3) = [[e^{-iπ/6}, 0], [0, e^{iπ/6}]]

Apply to qubit 1:
|0⟩ → e^{-iπ/6}|0⟩
|1⟩ → e^{iπ/6}|1⟩

State: (e^{-iπ/6}|00⟩ + e^{-iπ/6}|10⟩ + i·e^{iπ/6}|01⟩ + i·e^{iπ/6}|11⟩)/2

Now inverse QFT:
H(q[0]):
H on qubit 0: (|0⟩ + |1⟩)/√2 and (|0⟩ -

## isqTrain/4352

- task_id: `isqTrain/4352`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1912`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;

// Oracle for balanced function f(x) = x[0] XOR x[1]
oracle bool[1] f(bool x[2]) {
    // XOR of two input bits yields a balanced function
    bool res[] = [x[0] != x[1]];
    return res;
}

// Input register: 2 qubits
qbit q[2];
// Ancilla qubit for phase kickback
qbit anc[1];

procedure main() {
    // Prepare ancilla in |-> state for phase kickback
    X(anc[0]);
    H(anc[0]);
    // Create uniform superposition on input register
    H(q[0]); H(q[1]);
    // Single oracle query -- the key quantum speedup
    f(q, anc);
    // Interfere to extract function type
    H(q[0]); H(q[1]);
    // Measure input register only
    // Balanced function guarantees non-zero outcome
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a concise step-by-step reasoning for an isQ quantum program.
    *   Format: "## Circuit Analysis" section, no code blocks, predict probability distribution at the end.
    *   Specifics: Use Dirac notation, keep it concise (3-15 lines), focus on the state evolution.
    *   Program: Deutsch-Jozsa with a balanced oracle ($f(x) = x_0 \oplus x_1$) followed by $H Z H = X$ on the first qubit.

2.  **Analyze the Code:**
    *   Initialization: $q[0..1] = |00\rangle$, $anc[0] = |0\rangle$. State is $|000\rangle$.
    *   `X(anc[0]); H(anc[0]);`: anc is in $|-\rangle$. State: $\frac{1}{\sqrt{2}}(|00\rangle - |01\rangle)$ (using order $q_0 q_1 anc$).
    *   `H(q[0]); H(q[1]);`: Uniform superposition. State: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   `f(q, anc);`: Oracle applies $(-1)^{f(x)}$ to the input register.
        *   $f(00)=0$, $f(01)=1$, $f(10)=1$, $f(11)=0$.
        *   State becomes: $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle) \otimes |-\rangle$.
    *   `H(q[0]); H(q[1]);`: Second Hadamard transform on input register.
        *   $H^{\otimes 2}$ on the input state gives:
        *   $H(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$
        *   Actually, let's trace it exactly: $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$.
        *   $|00\rangle - |01\rangle - |10\rangle + |11\rangle = |0\rangle(|0\rangle - |1\rangle) - |1\rangle(|0\rangle - |1\rangle) = (|0\rangle - |1\rangle) \otimes (|0\rangle - |1\rangle)$.
        *   Applying H gives $|-\rangle \otimes |-\rangle = |11\rangle$. (Wait, $H|-\rangle = |1\rangle$).
        *   So after the second Hadamards, the input register is exactly $|11\rangle$.
    *   `H(q[0]); Z(q[0]); H(q[0]);`: This is $X(q[0])$.
        *   Applies $X$ to the first qubit. State becomes $X_0|11\rangle = |01\rangle \otimes |-\rangle$.
    *   `M(q[0]); M(q[1]);`: Measures $q_0$ and $q_1$.
        *   Since the state is $|01\rangle$, the measurement outcome is 100% $q_0=0, q_1=1$.
    *   Wait, is $q_0$ the higher bit or lower bit? "earlier measured qubit = higher bit". `M(q[0])` is earlier, so it's the higher bit. `01` means $q_0=0, q_1=1$. Let's double check.
        *   If state is $|q_0 q_1\rangle = |0\rangle \otimes |1\rangle$, then $q_0=0$ (bit 1) and $q_1=1$ (bit 0).
        *   So bitstring is `01`. Yes, `01` corresponds to $q_0=0, q_1=1$.

3.  **Draft the Reasoning:**
    *   Start with initial state $|00\rangle \otimes |0\rangle$.
    *   Ancilla prep: $|00\rangle \otimes |-\rangle$.
    *   Input Hadamards: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes |-\rangle$.
    *   Oracle $f

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 1.0000.'}

## isqTrain/4089

- task_id: `isqTrain/4089`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3877`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[4];

unit grover_oracle(qbit q[4]) {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[3]);
    X(q[2]);
    X(q[1]);
    X(q[0]);
} deriving gate

unit grover_diffusion(qbit q[4]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    for i in 0:3 {
        grover_oracle(q);
        grover_diffusion(q);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Predict the measurement output of the given isQ circuit.
    *   **Input:** An isQ circuit implementing Grover's algorithm with a custom oracle and 3 iterations.
    *   **Requirements:** Generate "Circuit Analysis" starting exactly with `## Circuit Analysis`. Explain operations, state evolution, final state, and probability distribution. Use Dirac notation. Be concise.

2.  **Analyze the Circuit:**
    *   **Qubits:** 4 qubits `q[0..3]`.
    *   **Initialization:** `H(q[0]); H(q[1]); H(q[2]); H(q[3]);` prepares the equal superposition state $|+\rangle^{\otimes 4} = \frac{1}{4} \sum_{x=0}^{15} |x\rangle$.
    *   **Oracle:**
        *   `X` on all qubits maps $|x_0 x_1 x_2 x_3\rangle \to |\bar{x}_0 \bar{x}_1 \bar{x}_2 \bar{x}_3\rangle$.
        *   `ctrl<2> CZ(q[0], q[1], q[2], q[3])` with 2 controls? Wait, let me check the syntax carefully. Actually, `ctrl<2>` means 2 controls? Or `CZ` is a 2-qubit gate, so `ctrl<2> CZ(c0, c1, c2, c3)` is a 4-qubit gate.
        *   Wait, standard isQ `ctrl<2> CZ` on 4 qubits: `CZ` takes 2 qubits. `ctrl<2>` adds 2 more controls. So it's a 4-qubit controlled-Z. The target is Z. This applies a phase of -1 if *all* controls and the target's control are 1.
        *   Let's trace the state $|x_0 x_1 x_2 x_3\rangle$ through the oracle:
            *   X gates: state is $|\bar{x}_0 \bar{x}_1 \bar{x}_2 \bar{x}_3\rangle$.
            *   ctrl CZ: applies -1 phase *only* if all 4 qubits are `1`.
            *   This means $|0000\rangle \to -|1111\rangle \to -|0000\rangle$. All other states pick up no phase and map back to themselves.
            *   So the oracle marks $|0000\rangle$.
        *   Let's double check standard Grover. If oracle marks $|0000\rangle$, the diffusion operator marks $|0000\rangle$ as well? No, standard diffusion marks $|0000\rangle$ in the X-basis.
    *   **Diffusion Operator:**
        *   `H` on all.
        *   `X` on all.
        *   `ctrl<2> CZ` on all.
        *   `X` on all.
        *   `H` on all.
        *   This is exactly the standard diffusion operator $2|\psi\rangle\langle\psi| - I$, which flips the state around the $|0000\rangle$ axis? Wait. The standard diffusion operator is $H^{\otimes 4} (2|0000\rangle\langle 0000| - I) H^{\otimes 4}$. The `ctrl<2> CZ` with `X` gates implements exactly $2|0000\rangle\langle 0000| - I$.
        *   Wait, if the oracle marks $|0000\rangle$ AND the diffusion operator reflects around $|0000\rangle$ (no, diffusion reflects around the mean, which is $|+\rangle^{\otimes 4}$), let's check the implementation.
        *   $D = H^{\otimes n} X^{\otimes n} (\text{ctrl-Z}) X^{\otimes n} H^{\otimes n}$. This reflects around $|+\rangle^{\otimes n}$.
        *   Let's re-evaluate the Oracle.
            *   Start with $|x\rangle$. Apply X: $|\bar{x}\rangle$.
            *   Apply `ctrl<2> CZ(c0, c1, c2, c3)`. This flips the phase of $|1111\rangle$.
            *   Apply X: goes back to $|x\rangle$.
            *   So the oracle flips the phase of the state $|0000\rangle$.
            *   Yes, $U_w |0000\rangle = -|0000\rangle$.

### Reference answer

Deterministic output: state |0000> with probability ~0.96

## isqTrain/1403

- task_id: `isqTrain/1403`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4247`

### Prompt

Help me write isQ code that the Bernstein-Vazirani algorithm to find the secret string s = 00001 (MSB first). Use 5 input qubits and 1 ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Goal:** Generate a reasoning section (3-15 lines) for a Bernstein-Vazirani algorithm implementation in isQ finding the secret string `s = 00001`.
    *   **Format:** Start with `## Reasoning`, use Dirac notation, concise, no code blocks.
    *   **Algorithm:** Bernstein-Vazirani with `s = 00001`.
    *   **Circuit:** 5 input qubits (`q[0]` to `q[4]`) initialized to $|0\rangle^{\otimes 5}$, 1 ancilla (`anc[0]`) initialized to $|1\rangle$.
    *   **Steps:** Ancilla to $|-\rangle$, H on inputs, Oracle (CNOT from `q[4]` to `anc[0]`), H on inputs, Measure inputs.

2.  **Trace the State Evolution:**
    *   Initial state: $|0\rangle^{\otimes 5}|1\rangle$
    *   X(anc), H(anc) -> $|0\rangle^{\otimes 5}|-\rangle$
    *   H(q[0..4]) -> $\frac{1}{\sqrt{2^5}} \sum_{x=0}^{2^5-1} |x\rangle|-\rangle = |+\rangle^{\otimes 5}|-\rangle$
    *   Oracle $U_f$ where $f(x) = s \cdot x$ and $s = 00001$ (so only $q_4$ controls the CNOT). The phase kickback applies $(-1)^{f(x)}$ to $|x\rangle$. Since $s = 00001$, it applies $-1$ only to states where $x_4=1$. $|x\rangle \to (-1)^{x_4}|x\rangle|-\rangle$.
    *   H(q[0..4]) on $\sum_x (-1)^{x_4}|x\rangle$: This is the exact inverse of the operation that takes $|00001\rangle \to \sum_x (-1)^{x_4}|x\rangle$. Thus, the H gates map it back to $|s\rangle = |00001\rangle$.
    *   Measurement: Measures exactly $|00001\rangle$ with probability 1.0.

3.  **Draft the Reasoning (Concise):**
    *   Goal: Implement Bernstein-Vazirani to find the secret 5-bit string s = 00001.
    *   Setup: Uses 5 input qubits (measured) and 1 ancilla.
    *   Initialization: Prepare ancilla in $|-\rangle$ and input register in uniform superposition $|+\rangle^{\otimes 5}$.
    *   Oracle: CNOT(q[4], anc[0]) computes $f(x) = s \cdot x \mod 2$. Phase kickback maps the state to $\frac{1}{\sqrt{2^5}} \sum_x (-1)^{s \cdot x} |x\rangle|-\rangle$.
    *   Interference: Applying Hadamard gates to the input register transforms the state into $|s\rangle|-\rangle = |00001\rangle|-\rangle$.
    *   Result: Measuring the input qubits deterministically yields the secret string 00001 (q[0] is MSB).

4.  **Refine and Format:**
    *   Check line count (6 lines, well within 3-15).
    *   Check Dirac notation.
    *   Check start with `## Reasoning`.
    *   Ensure no code block.

5.  **Final Polish:**
    ## Reasoning
    1. **Goal:** Implement the Bernstein-Vazirani algorithm to identify the secret bit string $s = 00001$.
    2. **Setup:** Uses 5 input qubits (measured) and 1 ancilla qubit.
    3. **Initialization:** Hadamard gates place the input register into a uniform superposition $|+\rangle^{\otimes 5}$, and X followed by H places the ancilla in $|-\rangle$.
    4. **Oracle:** The CNOT(q[4], anc[0]) applies a phase kickback of $(-1)^{x_4}$ to the input state, mapping it to $\sum (-1)^{s \cdot x}|x\rangle|-\rangle$.
    5. **Interference:** Applying Hadamard gates to the input register performs an inverse transform, resolving the superposition into the exact basis state $|s\rangle = |00001\rangle

## isqTrain/1993

- task_id: `isqTrain/1993`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3093`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    ctrl X(q[0], q[1]);
    nctrl X(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |00>.
2. H(q[0]) creates an equal superposition on the first qubit: (|00> + |10>)/√2.
3. ctrl

### Reference answer

{'predicted_probs': {'01': 0.5, '11': 0.5}, 'explanation': 'Expected probabilities: [0.0, 0.5, 0.0, 0.5]'}

## isqTrain/1170

- task_id: `isqTrain/1170`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `203`

### Prompt

Help me write isQ code that implements the iqp_circuit pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement an IQP (Instantaneous Quantum Polynomial) circuit pattern (H → diagonal gates → H) with explicit H-H identity pair to demonstrate gate cancellation awareness.

**Qubits:** 3 qubits (q[0], q[1], q[2]), all measured at the end.

**State evolution:**
1. **Initial:** |000⟩
2. **First H layer:** H⊗³ → |+++⟩ = (1/2√2)Σ|x⟩ for all x∈{0,1}³
3. **T gates:** T⊗³ applies phase e^(iπk/4) where k = Hamming weight of |x⟩
4. **CZ(q[0],q[1]):** Flips sign when q[0]=q[1]=1 (affects |110⟩, |111⟩)
5. **CZ(q[1],q[2]):** Flips sign when q[1]=q[2]=1 (affects |011⟩, |111⟩)
6. **Second H layer:** H⊗³ transforms back to computational basis, creating interference
7. **H-H on q[0]:** Identity operation (H²=I), demonstrating cancellation awareness
8. **Final state:** Interference produces non-uniform probabilities

**Expected probabilities** follow from constructive/destructive interference in the H⊗³ transformation of the diagonal phases, giving asymmetric distribution with |010⟩ and |111⟩ having highest probability (~0.232).

## isqTrain/3426

- task_id: `isqTrain/3426`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `118`

### Prompt

Write an isQ program that a 2-bit quantum adder in isQ that demonstrates carry overflow.

Compute a + b where a = 11 (binary, 3) and b = 01 (binary, 1).
Expected: sum bits = 00, carry_out = 1 (since 3+1=4 = 100 binary).

Register layout:
- q[0]=a[0], q[1]=a[1]: input a
- q[2]=b[0], q[3]=b[1]: input b (overwritten with sum)
- q[4]=carry_out

Declare 5 global qubits, measure all.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement a 2-bit quantum adder computing 3 + 1 = 4, demonstrating carry overflow where sum bits become 00 and carry_out = 1.

**Qubits:** 5 global qubits; q[0-1] = input a bits, q[2-3] = input b bits (overwritten with sum), q[4] = carry_out. All 5 are measured.

**State evolution:**
1. **Initialization:** X(q[0]), X(q[1]), X(q[2]) sets a=11, b=01 → |11100⟩
2. **Toffoli(q[0], q[2], q[4]):** Carry from bit 0: a[0]∧b[0] = 1∧1 = 1, flips q[4] → |11101⟩
3. **CNOT(q[0], q[2]):** Sum bit 0: q[2] = 1⊕1 = 0 → |11001⟩
4. **CNOT(q[4], q[3]):** Add carry to b[1]: q[3] = 0⊕1 = 1 → |11011⟩
5. **CNOT(q[1], q[3]):** Add a[1] to b[1]: q[3] = 1⊕1 = 0 → |11001⟩

**Final state:** |11001⟩ — q[0]=1, q[1]=1, q[2]=0, q[3]=0, q[4]=1

**Expected probabilities:** {|11001⟩: 1.0} — The sum bits q[3:2]=00 and carry q[4]=1 correctly represent 3+1=4 (binary 100), confirming overflow.

## isqTrain/2700

- task_id: `isqTrain/2700`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1780`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
oracle bool[1] g(bool a[6]) {
    bool s[] = [true, true, true, false, true, true];
    bool ba[] = s & a;
    bool res[1];
    res[0] = ba[0] != ba[1] != ba[2] != ba[3] != ba[4] != ba[5];
    return res;
}
qbit q[6], res[1];

procedure main(){
    X(res);
    H(res);
    H(q);
    g(q, res);
    H(q); 
    print M(q); 
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Explain the output probability distribution of an isQ quantum circuit.
    *   Circuit: A Bernstein-Vazirani algorithm implementation.
    *   Format: Concise (3-15 lines), step-by-step reasoning, Dirac notation, specific start/end markers.
    *   Output format: "## Circuit Analysis" followed by explanation and ending with predicted probability distribution.

2.  **Analyze the Circuit:**
    *   `X(res)`: Flips the result qubit to $|1\rangle$.
    *   `H(res)`: Puts result in $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
    *   `H(q)`: Puts 6 query qubits into uniform superposition $\frac{1}{\sqrt{2^6}} \sum_{x \in \{0,1\}^6} |x\rangle$.
    *   `g(q, res)`: An oracle computing the dot product of the input and secret string `s = [1, 1, 1, 0, 1, 1]` (which is `111011` or binary `59`). Wait, let me re-check the array.
        `bool s[] = [true, true, true, false, true, true];`
        Indices: 0, 1, 2, 3, 4, 5.
        Values: 1, 1, 1, 0, 1, 1.
        String: $s = s_5 s_4 s_3 s_2 s_1 s_0$ or $s_0 s_1 s_2 s_3 s_4 s_5$? The isQ manual/docs often use MSB to LSB or vice versa. Let's look at the boolean logic: `res[0] = ba[0] != ba[1] != ba[2] != ba[3] != ba[4] != ba[5]`. This is a bitwise XOR (which represents sum modulo 2, i.e., dot product).
        `s` is `111011`.
        Wait, isQ arrays are usually measured such that earlier qubits/indices might be LSB or MSB. Let's trace the standard BV algorithm.
        The state after `H(q)` is $\sum |x\rangle|-\rangle$.
        The oracle applies a phase $(-1)^{s \cdot x}$ to the state $|x\rangle$.
        `H(q)` is applied again. This maps the phase state $|s\rangle$ to $|0\rangle$.
        So the final state of `q` should be exactly $|s\rangle$.
        Let's check the expected measurement probabilities: `{'110111': 1.0}`.
        Wait, The predicted output `110111`.
        Let's reverse `111011`? Reverse is `110111`.
        Ah, in isQ, when you measure `print M(q);`, the bitstring is formatted with `q[0]` as the highest bit or lowest bit?
        Usually, `q[0]` is the highest bit (left-most).
        Let's look at the string `s`: `s[0]` to `s[5]`.
        `s[0]=1, s[1]=1, s[2]=1, s[3]=0, s[4]=1, s[5]=1`.
        If `q[0]` corresponds to `s[0]`, the string is `111011`.
        But The predicted output `110111`.
        Wait, let's look at `ba[0] != ba[1] ...`.
        If `s` is mapped to qubits, `q[5]` corresponds to `s[0]`, `q[4]` to `s[1]`, etc.? Or `q[0]` to `s[5]`?
        Actually, `110111` reversed is `111011`. So `s[5]` is the highest bit? No, `s[5]=1`, `s[4]=1`, `s[3]=1`... wait.
        Let's write `s` values:
        s[0] = 1
        s[1] = 1
        s[2] = 1
        s[3] = 0
        s[4] = 1
        s[5] = 1
        Order of bits in predicted output `110111`:
        bit 5: 1
        bit 4: 1
        bit 3: 0
        bit 2: 1

### Reference answer

{'predicted_probs': {'110111': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

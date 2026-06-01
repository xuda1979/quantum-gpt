# ISQ training COT RAG corpus: quantum_algorithms shard 117

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/47

- task_id: `isqExpand/algo/47`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `qpe`, `s_gate`, `bug_fix`, `controlled_operation`
- source: `isq_expansion`
- dataset_index: `302`

### Prompt

Fix the bug in this quantum program:

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    H(q[1]);
    X(q[2]);
    ctrl S(q[1], q[2]);
    H(q[0]);
    ctrl inv S(q[1], q[0]);
    H(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

In QPE with 2 phase qubits for the S gate:
- q[0] (MSB) should control U^{2^1} = S^2 = Z
- q[1] (LSB) should control U^{2^0} = S^1 = S

The buggy code only has ctrl @[q[1]] S(q[2]) but is missing ctrl @[q[0]] Z(q[2]).

Without the controlled-Z from q[0], the MSB phase qubit gets no phase information and the inverse QFT cannot correctly recover the phase.

Fix: Add ctrl @[q[0]] Z(q[2]) before ctrl @[q[1]] S(q[2]).

With the fix, the QPE correctly estimates phase 1/4, measuring |01> with probability 1.

## isqTrain/1218

- task_id: `isqTrain/1218`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5737`

### Prompt

Write an isQ program that implements the quantum_volume pattern with modified rotation parameters (num_pi4_to_pi6). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the given isQ program. Let me trace through the circuit and compute the predicted output.

The circuit structure:
1. Two qubits: q[0] and q[1], both initialized to |0⟩
2. Gates applied:
   - Ry(π/3) on q[0]
   - Ry(π/5) on q[1]
   - CNOT(q[0], q[1])
   - Rz(π/4) on q[0]
   - Rx(π/6) on q[1]
   - CNOT(q[0], q[1])
   - Measure both qubits

Let me trace through the state evolution.

Initial state: |00⟩

After Ry(π/3) on q[0]:
Ry(θ) = cos(θ/2)|0⟩⟨0| - sin(θ/2)|1⟩⟨0| + sin(θ/2)|0⟩⟨1| + cos(θ/2)|1⟩⟨1|
For θ = π/3:
cos(π/6) = √3/2 ≈ 0.866
sin(π/6) = 1/2 = 0.5

So: (cos(π/6)|0⟩ + sin(π/6)|1⟩) ⊗ |0⟩ = (0.866|0⟩ + 0.5|1⟩)|0⟩

After Ry(π/5) on q[1]:
θ = π/5
cos(π/10) ≈ 0.951
sin(π/10) ≈ 0.309

State: (0.866|0⟩ + 0.5|1⟩)(0.951|0⟩ + 0.309|1⟩)
= 0.866*0.951|00⟩ + 0.866*0.309|01⟩ + 0.5*0.951|10⟩ + 0.5*0.309|11⟩
= 0.8236|00⟩ + 0.2676|01⟩ + 0.4755|10⟩ + 0.1545|11⟩

After CNOT(q[0], q[1]):
|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

State: 0.8236|00⟩ + 0.2676|01⟩ + 0.4755|11⟩ + 0.1545|10⟩
= 0.8236|00⟩ + 0.2676|01⟩ + 0.1545|10⟩ + 0.4755|11⟩

After Rz(π/4) on q[0]:
Rz(θ) = e^(-iθ/2)|0⟩⟨0| + e^(iθ/2)|1⟩⟨1|
For θ = π/4:
Phase on |0⟩: e^(-iπ/8)
Phase on |1⟩: e^(iπ/8)

State: e^(-iπ/8)[0.8236|00⟩ + 0.2676|01⟩] + e^(iπ/8)[0.1545|10⟩ + 0.4755|11⟩]
= e^(-iπ/8)*0.8236|00⟩ + e^(-iπ/8)*0.2676|01⟩ + e^(iπ/8)*0.1545|10⟩ + e^(iπ/8)*0.4755|11⟩

After Rx(π/6) on q[1]:
Rx(θ) = cos(θ/2)I - i*sin(θ/2)X
For θ = π/6:
cos(π/12) ≈ 0.9659
sin(π/12) ≈ 0.2588

This transforms each basis state on q[1]:
|0⟩ → cos(π/12)|0⟩ - i*sin(π/12)|1⟩
|1⟩ → -i*sin(π/12)|0⟩ + cos(π/12)|1⟩

Let me compute the new state:
For the |00⟩ component:
e^(-iπ/8)*0.8236 * (cos(π/12)|0⟩ - i*sin(π/12)|1⟩) ⊗ (nothing for q[0], this is for q[1])

Wait, let me be more careful. The state after

## isqTrain/3789

- task_id: `isqTrain/3789`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3523`

### Prompt

Code this in isQ: the Deutsch-Jozsa algorithm for a 2-input balanced oracle with truth table [1, 0, 1, 0]. Use the oracle keyword, prepare output in |-> state, apply Hadamard-oracle-Hadamard, measure input qubits. Result should be non-zero (balanced).

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate reasoning for a specific Deutsch-Jozsa algorithm implementation (2-input, balanced oracle `[1, 0, 1, 0]`).
    *   Constraints: Concise (3-15 lines), Dirac notation, start with "## Reasoning", NO isQ code blocks.
    *   Input prompt specifies the circuit: 3 qubits, output prepared in |->, H on inputs, Oracle `f(2, 1) = [1, 0, 1, 0]`, H on inputs, measure all. Expected probs: `{|010>: 0.5, |011>: 0.5}`.

2.  **Trace the Circuit:**
    *   Initial state: $|000\rangle$ (q[0], q[1] are inputs, q[2] is output).
    *   Prepare output: $X(q[2])$ then $H(q[2])$. State becomes $|00\rangle \otimes (H|1\rangle) = |00\rangle \otimes |-\rangle$.
    *   H on inputs: $H(q[0])H(q[1])$ on $|00\rangle$ gives $|++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$. Total state: $\frac{1}{2}\sum_{x \in \{0,1\}^2} |x\rangle \otimes |-\rangle$.
    *   Oracle `f`: $|x\rangle|y\rangle \to |x\rangle|y \oplus f(x)\rangle$. Since the second qubit is in $|-\rangle$, it applies a phase kickback: $(-1)^{f(x)}|x\rangle|-\rangle$. The oracle truth table is $[1, 0, 1, 0]$. So $f(00)=1, f(01)=0, f(10)=1, f(11)=0$. The state becomes $\frac{1}{2}(-|00\rangle + |01\rangle - |10\rangle + |11\rangle) \otimes |-\rangle = \frac{1}{2}(-|0\rangle + |1\rangle)(|0\rangle - |1\rangle) \otimes |-\rangle$ or similar? Wait, let's be exact.
    *   $(-1)^{f(x)}$ for $x \in \{00, 01, 10, 11\}$ gives $\{-1, 1, -1, 1\}$.
    *   State is $\frac{1}{2}(-|00\rangle + |01\rangle - |10\rangle + |11\rangle) \otimes |-\rangle$.
    *   Apply H on inputs again: $H \otimes H \frac{1}{2}(-|00\rangle + |01\rangle - |10\rangle + |11\rangle) = H(-|0\rangle+|1\rangle) \otimes H(|0\rangle-|1\rangle)$? No.
    *   $H(-|0\rangle+|1\rangle) = -|+\rangle + |-\rangle = -|0\rangle$. So input qubits become $|10\rangle$.
    *   Wait, let's check the predicted output: `{|010>: 0.5, |011>: 0.5}`.
    *   Why $|010\rangle$ and $|011\rangle$ instead of $|10\rangle$ on inputs? Ah! The output qubit `q[2]` is measured as well, and it remains in $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   Since the inputs are exactly $|1\rangle$ and $|0\rangle$, the full state is $|10\rangle \otimes |-\rangle = \frac{1}{\sqrt{2}}(|100\rangle - |101\rangle)$.
    *   Wait, if the final state is $|10\rangle \otimes |-\rangle$, why does the prompt say `{|010>: 0.5, |011>: 0.5}`? Let's check the bit ordering in isQ.
    *   Earlier measured qubit = higher bit.
    *   If we measure M(q[0]), M(q[1]), M(q[2]).
    *   The measured integer is `(q[0] << 2) | (q[1] << 1) | q[2

## isqTrain/3428

- task_id: `isqTrain/3428`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `5655`

### Prompt

请用isQ语言编写一个量子电路：a 3-qubit QFT followed by inverse QFT in isQ, applied to the state |101>.

The QFT + IQFT roundtrip should return the original state.

3-qubit QFT circuit:
1. H(q[0]), ctrl-Rz(pi/2) from q[1], ctrl-Rz(pi/4) from q[2]
2. H(q[1]), ctrl-Rz(pi/2) from q[2]
3. H(q[2])
4. Swap q[0] and q[2]

Declare 3 qubits. Prepare |101>, apply QFT, apply IQFT.
Measure all. Expected: |101>.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Verify that 3-qubit QFT followed by inverse QFT acts as identity, returning |101⟩.
2. Three qubits q[0], q[1], q[2] are declared globally; all three are measured.
3. State preparation: X(q[0]) and X(q[2]) transform |000⟩ → |101⟩.
4. Forward QFT on q[0]: H creates superposition, then ctrl-Rz(π/2) from q[1] and ctrl-Rz(π/4) from q[2] apply phase rotations. Repeating for q[1] (with ctrl-Rz(π/2) from q[2]) and q[2] (H only) produces the Fourier transform.
5. Swap q[0]↔q[2] reorders output qubits to match standard QFT bit-reversal convention.
6. Inverse QFT reverses the swap, then applies H and negated ctrl-Rz gates in reverse order, exactly undoing each forward operation.
7. Since IQFT = QFT†, the roundtrip is identity: |101⟩ → QFT → ... → IQFT → |101⟩ with probability 1.0.

## isqTrain/850

- task_id: `isqTrain/850`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2204`

### Prompt

Create an isQ quantum circuit that implements the finite_field_inversion pattern. Include explicit identity operations in the circuit (X-X pair before M(q[1])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement finite field inversion in GF(2) where 1^(-1) = 1, with explicit X-X identity pair demonstrating gate cancellation.
2. **Qubits**: 2 qubits (q[0] input, q[1] inverse register); only q[1] is measured.
3. **State evolution**:
   - |00⟩ →X(q[0])→ |10⟩ (set input to 1)
   - →CNOT(q[0],q[1])→ |11⟩ (copy to inverse register)
   - →X(q[1])→ |10⟩ →X(q[1])→ |11⟩ (X-X pair cancels, identity operation)
4. **Result**: q[1] is in |1⟩ state, so measurement yields {|1⟩: 1.0}.

## isqTrain/880

- task_id: `isqTrain/880`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3464`

### Prompt

Implement the following in isQ: implements a variant of the inner_product_mod2 pattern using q[7] -> q[8]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute the binary inner product x·y mod 2 of two 3-bit vectors, storing the result in an ancilla qubit using Toffoli gates for conditional XOR operations.

2. **Qubits**: 8-qubit register; q[0-2] encode x, q[3-5] encode y, q[6] accumulates the result, and q[6-7] are measured.

3. **State evolution**:
   - After encoding X(q[0]), X(q[2]): |00000000⟩ → |10100000⟩ (x=[1,0,1])
   - After encoding X(q[3]), X(q[4]): |10100000⟩ → |10111000⟩ (y=[1,1,0])
   - Toffoli(q[0],q[3],q[6]): q[0]∧q[3]=1, flips q[6] → |10111010⟩
   - Toffoli(q[1],q[4],q[6]): q[1]∧q[4]=0, no change → |10111010⟩
   - Toffoli(q[2],q[5],q[6]): q[2]∧q[5]=0, no change → |10111010⟩

4. **Final measurement**: IP = 1⊕0⊕0 = 1, so q[6]=|1⟩, q[7]=|0⟩. Measuring q[6] then q[7] yields bitstring |10⟩ with probability 1.0.

## isqTrain/4190

- task_id: `isqTrain/4190`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4990`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[0], q[2]);
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this quantum circuit step by step.

Initial state: |000⟩

After H on all three qubits:
H|0⟩ = |+⟩ = (1/√2)(|0⟩ + |1⟩)

So after H(q[0]), H(q[1]), H(q[2]):
State = |+⟩|+⟩|+⟩ = (1/2√2)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

Now let's trace through the gates:

CNOT(q[0], q[1]) - flips q[1] when q[0] is |1⟩
Rz(π, q[1]) - applies a phase of -1 to |1⟩ state of q[1], wait let me check: Rz(2.0 * 0.500, q[1]) = Rz(1.0, q[1])

Wait, Rz(θ) = [[1, 0], [0, e^(iθ)]]. So Rz(1.0) applies a phase e^(i) to |1⟩.

Actually wait, let me reconsider. The convention for Rz might be different. Let me use the standard convention: Rz(θ)|0⟩ = |0⟩, Rz(θ)|1⟩ = e^(iθ)|1⟩.

So Rz(1.0, q[1]) applies phase e^(i) to q[1] when it's |1⟩.

The sequence CNOT(q[0], q[1]); Rz(1.0, q[1]); CNOT(q[0], q[1]) is a controlled-phase operation. Let me think about this more carefully.

Actually, let me think about what CNOT-Rz-CNOT does. 

Let's consider the effect on |q0 q1⟩:
- |00⟩ → CNOT → |00⟩ → Rz on q1 → |00⟩ → CNOT → |00⟩
- |01⟩ → CNOT → |01⟩ → Rz on q1 → e^(i)|01⟩ → CNOT → e^(i)|01⟩
- |10⟩ → CNOT → |11⟩ → Rz on q1 → e^(i)|11⟩ → CNOT → e^(i)|10⟩
- |11⟩ → CNOT → |10⟩ → Rz on q1 → |10⟩ → CNOT → |11⟩

So the effect is:
- |00⟩ → |00⟩
- |01⟩ → e^(i)|01⟩
- |10⟩ → e^(i)|10⟩
- |11⟩ → |11⟩

This is equivalent to applying a phase e^(i) when q[0] OR q[1] is |1⟩ (but not both). Actually it's equivalent to applying Rz(1) on q[0] and Rz(1) on q[1], up to a global phase.

Wait, let me reconsider. Rz(θ) on q[0] would give:
- |00⟩ → |00⟩
- |01⟩ → |01⟩
- |10⟩ → e^(i)|10⟩
- |11⟩ → e^(i)|11⟩

And Rz(θ) on q[1] would give:
- |00⟩ → |00⟩
- |01⟩ → e^(i)|01⟩
- |10⟩ → |10⟩
- |11⟩ → e^(i)|11⟩

Combined Rz(1) on q[0] and Rz(1) on q[1]:
- |00⟩ → |00⟩
- |01⟩ → e^(i)|01⟩
- |10⟩ → e^(i)|10⟩
- |11⟩ → e^(2i)|11⟩

But CNOT-Rz-CNOT gives:
- |00⟩ → |00⟩
- |01⟩ → e^(i)|01⟩
- |10⟩ → e^(i)|10⟩
- |11⟩ → |11⟩

So it's not the same. Let me think again.

Actually, CNOT(q[0], q[1]) followed by Rz(θ, q[1]) followed by CNOT(q[0], q[1]) is equivalent to applying a controlled-Rz gate, but with the control being q[0] on target q[1]... No wait.

Let me redo this:
- The first CNOT entangles q[0] and q[1]
- The Rz applies to q[1]
- The second CNOT undoes the entanglement

So the net effect is: when q[0] is |1⟩, q[1] gets

### Reference answer

Uniform distribution across 8 states

## isqTrain/18

- task_id: `isqTrain/18`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2126`

### Prompt

Implement the following in isQ: implements the qft_subcircuit pattern with modified rotation parameters (pi2_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Goal: Generate a reasoning section explaining a QFT-like circuit with modified rotation parameters (all `Rz` rotations use `pi/4`).
    *   Input circuit code: isQ code with 3 qubits. `q[2]` is initialized to |1>. Then `qft3(q[0], q[1], q[2])` is called.
    *   Final probabilities: uniform distribution over all 8 states (0.125 probability each).
    *   Output constraints: "## Reasoning" header, Dirac notation, 3-8 lines (simple) to 15 lines (complex), NO isQ code blocks.

2.  **Analyze the Circuit:**
    *   Initial state: `|000>` (global declaration). Then `X(q[2])` makes it `|001>`.
    *   `qft3` steps:
        *   `H(a)`: `H` on `q[0]`. State goes from $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |00\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
        *   `ctrl Rz(pi/4, b, a)`: `Rz(pi/4)` on `b` (`q[1]`) controlled by `a` (`q[0]`). Wait, isQ syntax `ctrl Rz(pi/4, b, a)` means control on `b`, target `a`, or control on `a` target `b`? Actually, isQ `ctrl Rz(theta, target, control)` or similar. Let's assume standard `ctrl Rz(theta, target_qubit, control_qubit)` or wait, the reference says `ctrl Rz(pi/4.0, b, a)`. If it's controlled by `a` on target `b`: Since `b` is |0>, phase on |0> doesn't matter. If target is `a`, controlled by `b`: Since `b` is |0>, nothing happens. Wait, The predicted output a uniform distribution over all 3 qubits `|000>` to `|111>`!
        *   Wait, if the initial state is `|001>` (q[2] is flipped), let's trace `qft3(q[0], q[1], q[2])`.
        *   Actually, let's look at the predicted output: 0.125 for ALL 8 states. This means the final state is a uniform superposition $\frac{1}{\sqrt{8}} \sum_{x=0}^7 |x\rangle$ up to some phases.
        *   Why does it produce uniform distribution? The operations are `H`, `Rz(pi/4)`, `Rz(pi/4)`, `H`, `Rz(pi/4)`, `H`.
        *   Let's check the unitary. $H$ makes superposition. $Rz$ adds phases. The $H$ gates at the end of the sequence (or rather applied to `q[0]`, `q[1]`, `q[2]` sequentially with some C-Rzs) essentially just map computational basis states to superpositions. If the initial state is $|4\rangle = |100\rangle$ (wait, `X(q[2])` means `q[2]=1`, so the state is $|001\rangle$). Wait, if `q[0]` is the most significant bit (as per standard isQ/probs mode), then `q[2]` is the least significant bit. `X(q[2])` creates $|001\rangle$.
        *   Wait, standard QFT on $|001\rangle$ (which is $|1\rangle$) gives a specific phase state: $\frac{1}{\sqrt{8}} \sum_{k=0}^7 \omega^{1 \cdot k} |k\rangle$, where $\omega = e^{2\pi i / 8}$. The probabilities of measuring this state are indeed uniform! The probability for any basis state $|k\rangle$ is $|\frac{1}{\sqrt{8}} e^{i\phi}|^2 = 1/8 = 0.125$.
        *   Ah! The circuit implements a modified QFT, but ANY QFT (even with modified/incorrect phases) maps computational basis states to superpositions where all amplitudes have magnitude $1/\sqrt{2^n}$. Since it's composed of Hadamards (which have uniform magnitude outputs) and phase gates (which only change phases, not magnitudes), the output state for any computational basis input MUST have

## isqTrain/2911

- task_id: `isqTrain/2911`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `699`

### Prompt

Create an isQ quantum circuit that implementing the Bernstein-Vazirani algorithm with secret string s=110 on 3 qubits.

Requirements:
- Use 3 input qubits and 1 ancilla.
- Define the oracle using the isQ `oracle` keyword.
- Declare main qubits at global scope.
- Use `procedure main()` as entry point.
- Measure all 3 input qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement Bernstein-Vazirani to find secret string s=110 by querying an oracle that computes f(x)=s·x mod 2.
2. **Qubits**: 3 input qubits q[0], q[1], q[2] (measured) plus 1 ancilla anc[0] (for phase kickback).
3. **State evolution**:
   - Start: |000⟩|0⟩
   - After X(anc), H(anc): |000⟩|−⟩ where |−⟩=(|0⟩−|1⟩)/√2
   - After H(q[0]), H(q[1]), H(q[2]): (1/√8)∑ₓ|x⟩|−⟩ (equal superposition over all 3-bit x)
   - After oracle g(q, anc): (1/√8)∑ₓ(−1)^(s·x)|x⟩|−⟩ (phase encodes s·x mod 2)
   - After H(q[0]), H(q[1]), H(q[2]): |110⟩|−⟩ (H converts phase pattern to computational basis)
4. **Result**: Measuring q[0], q[1], q[2] yields |110⟩ with probability 1.0, correctly recovering the secret string.

## isqQA/quantum_algorithms/47_principle_advantage

- task_id: `isqQA/quantum_algorithms/47_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `量子振幅估计`
- source: `qa_pipeline`
- dataset_index: `3871`

### Prompt

量子振幅估计是诸多量子机器学习和量子金融算法（如期权定价、风险分析）的核心子程序。请从宏观原理出发，详细阐述量子振幅估计算法是如何将概率估计问题转化为相位估计问题的？同时，严格对比QAE与经典蒙特卡洛方法在达到误差水平为ε时的时间复杂度差异，并深入剖析这种“二次加速”背后的物理与数学来源。

### Reference answer

量子振幅估计是量子计算中极其重要的一类算法，它巧妙地将概率幅的估计问题转化为了相位估计问题，从而实现了相对经典方法的平方级加速。

**宏观原理：从概率到相位的转化**
QAE的核心思想基于这样一个前提：假设我们有一个酉算子A，能够将系统的初始态|0⟩制备到目标叠加态：
A|0⟩ = √(1-a)|Ψ_bad⟩ + √a|Ψ_good⟩
其中a就是我们希望估计的目标概率（即测量得到“好”状态的振幅平方）。为了估计a，QAE构造了类似Grover迭代的酉算子Q = -A S_0 A† S_χ，其中S_0是关于初始态|0⟩的反射算子，S_χ是关于好状态|Ψ_good⟩的反射算子。
在由|Ψ_bad⟩和|Ψ_good⟩张成的二维子空间中，算子Q的作用等价于一个旋转。设√a = sin(θ)，那么Q在该子空间中的特征值将包含相位信息，即 e^{±i2θ}。QAE算法将这个算子Q作为黑盒，利用量子相位估计（QPE）算法的框架，通过施加一系列受控的Q^(2^j)操作以及逆量子傅里叶变换（IQFT），精确提取出相位2θ。测得相位后，即可通过简单的三角函数关系 a = sin²(θ) 高精度地反推出目标概率a。

**时间复杂度对比**
在经典计算中，估计概率a的标准方法是蒙特卡洛模拟。根据中心极限定理，经典蒙特卡洛方法若要达到误差为ε的精度（即估计值与真实值的偏差不大于ε），其方差决定了所需的采样次数与1/ε²成正比，时间复杂度为 O(1/ε²)。
而在量子振幅估计中，由于QPE可以利用m个辅助比特将相位空间分割为2^m个等分，要达到误差ε的精度，QAE只需要对黑盒算子A（及其逆算子）进行 O(1/ε) 次查询。这使得算法的时间复杂度从经典的 O(1/ε²) 锐减到了量子的 O(1/ε)。

**量子加速的来源剖析**
这种显著的“二次加速”其根本来源可以归结为以下深层的物理与数学机制：
1. 数学层面：特征值的指数级分辨率。在QPE框架下，对受控酉算子Q进行k次幂操作，等价于将其特征值的相位放大了k倍。量子寄存器可以借助n个量子比特同时表示和计算2^n个不同的相位假设，这种利用二进制移相获得指数级相位分辨率的机制，是经典概率累加所不具备的。它将经典统计学中消耗大量样本的方差缩减问题，转化为了确定性的代数相位求解问题。
2. 物理层面：量子态的相干与干涉。经典蒙特卡洛依赖于大量独立同分布的随机采样，其误差衰减受制于随机游走的标准差（即O(1/√N)的统计规律）。而QAE在物理上利用了量子态的叠加与干涉效应。Grover算子Q实际上在状态空间中执行了精密的“相位旋转”，每一次应用Q，都在相空间中刻划着精确的几何轨迹。量子干涉使得错误的概率分量在计算过程中相互抵消，而目标概率的特征信息则被转化为可提取的相对相位差。因此，QAE完全绕过了经典随机采样必须面对的统计涨落瓶颈，在量子态演化的深层逻辑上实现了对概率分布的确定性代数提取。

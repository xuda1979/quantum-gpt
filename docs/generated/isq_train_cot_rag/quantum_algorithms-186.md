# ISQ training COT RAG corpus: quantum_algorithms shard 186

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/16

- task_id: `isqTrain/16`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5624`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the qft_subcircuit pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this circuit carefully.

The task is to write an isQ program implementing a QFT subcircuit on qubits q[3] -> q[5], but The circuit should q[0], q[1], q[2] with q[2] initialized to |1>.

Let me trace through The implementation:

1. Initial state: |00000⟩ (5 qubits)
2. After X(q[2]): |00100⟩
3. Apply qft3(q[0], q[1], q[2]):

The qft3 procedure performs a 3-qubit QFT on qubits a, b, c (which are q[0], q[1], q[2]).

Starting state for the QFT part: |001⟩ (on qubits q[0], q[1], q[2])

Let me trace the QFT on |001⟩:

Step 1: H(a) = H(q[0]) on |001⟩
- This applies H to the first qubit: (|0⟩ + |1⟩)/√2 ⊗ |01⟩ = (|001⟩ + |101⟩)/√2

Step 2: ctrl Rz(π/2, b, a) = CRz(π/2, q[1], q[0])
- Phase shift on |1⟩ state of q[0] when q[1] is |1⟩
- State is (|001⟩ + |101⟩)/√2
- The |101⟩ component has q[1]=|0⟩, so no phase added
- Wait, let me reconsider. CRz(θ, control, target)? Or CRz(θ, target, control)?

In isQ, `ctrl Rz(pi/2.0, b, a)` means controlled-Rz with b as control and a as target? Or is it the other way?

Actually, looking at the syntax: `ctrl Rz(pi/2.0, b, a)` - this is a controlled operation. The Rz gate is applied to `a`, controlled by `b`. Wait, but `ctrl` typically applies to the next gate call.

Let me reconsider the isQ syntax. `ctrl Rz(pi/2.0, b, a)` - this seems to be a controlled-Rz with b as control and applied to a.

Wait, actually looking more carefully: `ctrl Rz(pi/2.0, b, a)` - I think in isQ, the `ctrl` modifier means the control qubit comes first, then the gate parameters. So this is: control = b, apply Rz(π/2) to a when b is |1⟩.

Hmm, but that doesn't match standard QFT. In QFT, we typically have:
- H on qubit k
- Controlled R_k on qubit k, controlled by qubit j (where j > k)

Let me re-examine. Standard 3-qubit QFT on qubits a, b, c:

For qubit a (most significant):
1. H(a)
2. CRz(π/2, a) controlled by b → CRz(b, a) with phase π/2? No...

Actually, the standard QFT has:
- H(a)
- Controlled-R2 from b to a (phase π/2 on a when b is |1⟩)
- Controlled-R3 from c to a (phase π/4 on a when c is |1⟩)
- H(b)
- Controlled-R2 from c to b
- H(c)
- swap(a, c) via three CNOTs

So `ctrl Rz(pi/2.0, b, a)` means: controlled by b, apply Rz(π/2) to a. This makes sense for QFT.

Let me trace with input |001⟩ (binary, where a=q[0] is MSB, c=q[2] is LSB):

Wait, I need to be careful about bit ordering. If we write the state as |a,b,c⟩ with a being q[0]:

Initial state for QFT: |0,0,1⟩ (q[2]=|1⟩)

Step 1: H(a) on |001⟩
= (|0⟩+|1⟩)/√2 ⊗ |01⟩ = (|001⟩ + |101⟩)/√2

Step 2: ctrl Rz(π/2, b, a) - phase π/2 on a when b=|1⟩
Current state: (|001⟩ + |101⟩)/√2
|001⟩: a=0, b=0 → no phase
|101⟩: a=1, b=0 → no phase
State unchanged: (|001⟩ + |101⟩)/√2

Step 3: ctrl Rz(π/4, c

## isqTrain/3042

- task_id: `isqTrain/3042`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5716`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[4];
procedure bellpair(qbit a, qbit b) {
    H(a);
    CNOT(a, b);
} deriving gate
procedure main() {
    bellpair(q[0], q[1]);
    bellpair(q[2], q[3]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 4 qubits to |0000⟩ and applies the `bellpair` gate to pairs (q[0], q[1]) and (q[2], q[3]).
2. The `bellpair` procedure applies a Hadamard (H) gate to the first qubit, followed by a CNOT with the first qubit as control and the second as target.
3. Applying `bellpair` to q[0] and q[1] transforms |00⟩ to $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
4. Applying `bellpair` to q[2] and q[3] independently transforms |00⟩ to $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
5. The combined final quantum state is the tensor product of the two Bell states: $\frac{1}{2}(|0000\rangle + |0011\rangle + |1100\rangle + |1111\rangle)$.
6. Measuring all qubits collapses the state to one of the four basis states in the superposition. Each state has an equal probability of $\frac{1}{4} = 0.25$.

Predicted probability distribution:
- |0000⟩: 0.25
- |0001⟩: 0.0
- |0010⟩: 0.0
- |0011⟩: 0.25
- |0100⟩: 0.0
- |0101⟩: 0.0
- |0110⟩: 0.0
- |0111⟩: 0.0
- |1000⟩: 0.0
- |1001⟩: 0.0
- |1010⟩: 0.0
- |1011⟩: 0.0
- |1100⟩: 0.25
- |1101⟩: 0.0
- |1110⟩: 0.0
- |1111⟩: 0.25

### Reference answer

{'predicted_probs': {'0000': 0.25, '0011': 0.25, '1100': 0.25, '1111': 0.25}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1222

- task_id: `isqTrain/1222`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5523`

### Prompt

Implement a quantum circuit in isQ: implements the quantum_volume pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this quantum volume circuit step by step.

The circuit has 2 qubits, and I need to trace through the state evolution.

Initial state: |00⟩

1. Ry(π/3) on q[0]:
Ry(π/3)|0⟩ = cos(π/6)|0⟩ + sin(π/6)|1⟩ = (√3/2)|0⟩ + (1/2)|1⟩

State: ((√3/2)|0⟩ + (1/2)|1⟩) ⊗ |0⟩

2. Ry(π/5) on q[1]:
Ry(π/5)|0⟩ = cos(π/10)|0⟩ + sin(π/10)|1⟩

cos(π/10) ≈ 0.9511
sin(π/10) ≈ 0.3090

State: ((√3/2)|0⟩ + (1/2)|1⟩) ⊗ (cos(π/10)|0⟩ + sin(π/10)|1⟩)

3. CNOT(q[0], q[1]): Control q[0], target q[1]
This flips q[1] when q[0] = |1⟩

State becomes:
(√3/2)cos(π/10)|00⟩ + (√3/2)sin(π/10)|01⟩ + (1/2)cos(π/10)|11⟩ + (1/2)sin(π/10)|10⟩

Wait, let me recalculate. CNOT(q[0], q[1]) with q[0] as control:
- |00⟩ → |00⟩
- |01⟩ → |01⟩
- |10⟩ → |11⟩
- |11⟩ → |10⟩

So the state after CNOT:
(√3/2)cos(π/10)|00⟩ + (√3/2)sin(π/10)|01⟩ + (1/2)sin(π/10)|11⟩ + (1/2)cos(π/10)|10⟩

Wait, let me redo this more carefully.

Before CNOT:
(√3/2)cos(π/10)|00⟩ + (√3/2)sin(π/10)|01⟩ + (1/2)cos(π/10)|10⟩ + (1/2)sin(π/10)|11⟩

After CNOT(q[0], q[1]) (control q[0], target q[1]):
|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

So:
(√3/2)cos(π/10)|00⟩ + (√3/2)sin(π/10)|01⟩ + (1/2)cos(π/10)|11⟩ + (1/2)sin(π/10)|10⟩

4. Rz(π/4) on q[0]:
Rz(π/4)|0⟩ = e^{-iπ/8}|0⟩
Rz(π/4)|1⟩ = e^{iπ/8}|1⟩

5. Rx(π/6) on q[1]:
Rx(π/6)|0⟩ = cos(π/12)|0⟩ - i sin(π/12)|1⟩
Rx(π/6)|1⟩ = -i sin(π/12)|0⟩ + cos(π/12)|1⟩

6. CNOT(q[0], q[1]) again

7. X(q[0]) followed by X(q[0]) - these cancel out (identity)

8. Measure both qubits

This is getting complex. Let me verify the probabilities numerically.

Given probabilities:
|00⟩: 0.6377359759582624
|01⟩: 0.1122640240417365
|10⟩: 0.21257865865275538
|11⟩: 0.0374213413472457

These sum to 1.0 ✓

The X-X pair cancels out, so it's effectively identity before measurement.

Let me write the reasoning:

## Reasoning

1. Goal: Implement a quantum volume pattern with 2 qubits using random SU(4)-like operations, demonstrating gate cancellation with X-X pair.

2. Two qubits (q[0], q[1]) are used and both measured; X-X on q[0] cancels to identity before measurement.

3. State evolution:
- Start: |00⟩
- After Ry(π/3)⊗Ry(π/5): (

## isqTrain/2939

- task_id: `isqTrain/2939`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4269`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[5];
procedure main() {
    for i in 0:5 {
        H(q[i]);
    }
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
    M(q[4]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Goal:** Provide a step-by-step reasoning for an isQ quantum program.
    *   **Input Program:** A simple program with 5 qubits. A Hadamard gate is applied to each qubit, followed by measurements on all qubits.
    *   **Format Constraints:** Concise (3-8 lines), Dirac notation, start with "## Circuit Analysis", no code blocks, end with the predicted probability distribution.
    *   **Input state:** $|00000\rangle$
    *   **Operations:** $H^{\otimes 5}$

2.  **Step-by-Step Execution:**
    *   **Initial State:** All 5 qubits are in state $|00000\rangle$.
    *   **Operation:** `for i in 0:5 { H(q[i]); }` applies a Hadamard gate to each of the 5 qubits.
    *   **State Evolution:**
        *   $|0\rangle \xrightarrow{H} \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        *   For 5 qubits: $H^{\otimes 5} |00000\rangle = \frac{1}{\sqrt{2^5}} \sum_{x=0}^{31} |x\rangle = \frac{1}{\sqrt{32}} \sum_{x \in \{0,1\}^5} |x\rangle$.
    *   **Final State:** A uniform superposition of all 32 possible computational basis states from $|00000\rangle$ to $|11111\rangle$.
    *   **Measurement:** The probability of measuring any specific basis state $|x\rangle$ is $|\frac{1}{\sqrt{32}}|^2 = \frac{1}{32} = 0.03125$.
    *   **Probabilities:** Uniform distribution across all 32 states.

3.  **Draft the Response:**
    *   *Constraint Check:* 3-8 lines for simple circuits. This is very simple.
    *   Line 1: Start with "## Circuit Analysis".
    *   Line 2: Initial state is |00000>.
    *   Line 3: The Hadamard gates (H) place each of the 5 qubits into an equal superposition |+>.
    *   Line 4: The resulting 5-qubit state is an equal superposition of all 32 basis states: (1/√32) * Σ |x⟩.
    *   Line 5: Because the amplitudes are all equal, each of the 32 possible measurement outcomes has an equal probability of 1/32 (0.03125).
    *   Line 6: Final predicted probabilities.

4.  **Refine Response:**
    ## Circuit Analysis
    1. The circuit starts with 5 qubits in the initial state |00000>.
    2. The loop applies a Hadamard gate (H) to each qubit, placing each into the superposition |+> = (|0> + |1>) / √2.
    3. The joint state becomes an equal superposition of all 32 basis states: (1/√32) * Σ |x⟩ where x ∈ {0,1}^5.
    4. Upon measurement, every basis state from |00000> to |11111> has an equal probability of 1/32 (0.03125).
    Predicted probability distribution: {'00000': 0.03125, '00001': 0.03125, ..., '11111': 0.03125}

    Let's make sure it outputs exactly the JSON structure or the mapping requested. The prompt says "Return a JSON array" but then the expected measurement probabilities show a dictionary. I will use the dictionary format as given in the predicted output at the end. Wait, the prompt says "Return a JSON array", but then it says "Expected measurement probabilities: {'00000': ...}". I'll format the end exactly to match the predicted output or simply write the dictionary.

    Let's combine and format strictly to 3-8 lines.

    ## Circuit Analysis
    - Initial state is |00000>.
    - Applies a Hadamard gate to each of the 5 qubits, changing each |0> to |+>.
    - The final state before measurement is an equal superposition of all 32 computational basis states: (1/√32) Σ |x>.
    - Measurement probabilities are uniformly distributed.
    {'00000': 0.03125, '00001': 0.03125, '00010': 0.03125

### Reference answer

{'predicted_probs': {'00000': 0.03125000000000001, '00001': 0.03125000000000001, '00010': 0.03125000000000001, '00011': 0.03125000000000001, '00100': 0.03125000000000001, '00101': 0.03125000000000001, '00110': 0.03125000000000001, '00111': 0.03125000000000001, '01000': 0.03125000000000001, '01001': 0.03125000000000001, '01010': 0.03125000000000001, '01011': 0.03125000000000001, '01100': 0.03125000000000001, '01101': 0.03125000000000001, '01110': 0.03125000000000001, '01111': 0.03125000000000001, '10000': 0.03125000000000001, '10001': 0.03125000000000001, '10010': 0.03125000000000001, '10011': 0.03125000000000001, '10100': 0.03125000000000001, '10101': 0.03125000000000001, '10110': 0.03125000000000001, '10111': 0.03125000000000001, '11000': 0.03125000000000001, '11001': 0.03125000000000001, '11010': 0.03125000000000001, '11011': 0.03125000000000001, '11100': 0.03125000000000001, '11101': 0.03125000000000001, '11110': 0.03125000000000001, '11111': 0.03125000000000001}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4842

- task_id: `isqTrain/4842`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `quantum_counting`, `interference`
- source: `isq_train_cot`
- dataset_index: `2915`

### Prompt

请用isQ语言编写一个量子电路：implements just the oracle part of Grover for marking |10> on 2 qubits. Apply H to both qubits, then X(q[1]), CZ, X(q[1]). Measure both. Without diffusion, probabilities stay uniform.

### Chain-of-thought reasoning

## Reasoning
The circuit applies a Grover oracle marking |10⟩ with a phase flip, but omits the diffusion operator, so measurement probabilities remain uniform.

**Qubits:** 2 (q[0], q[1]), both measured.

**State evolution:**
1. **H(q[0]); H(q[1]):** |00⟩ → (|00⟩+|01⟩+|10⟩+|11⟩)/2
2. **X(q[1]):** Swaps |0⟩↔|1⟩ on q[1]: → (|01⟩+|00⟩+|11⟩+|10⟩)/2
3. **CZ(q[0],q[1]):** Flips phase when both |1⟩: → (|01⟩+|00⟩+|11⟩−|10⟩)/2
4. **X(q[1]):** Swaps back: → (|00⟩+|01⟩−|10⟩+|11⟩)/2

The oracle successfully marks |10⟩ with a −1 phase, but without diffusion to amplify this, all probabilities stay 0.25.

## isqTrain/751

- task_id: `isqTrain/751`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2123`

### Prompt

Implement the following in isQ: implements the modular_adder pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a modular adder that computes (a + b) mod N, specifically (2 + 1) mod 3 = 0.

2. **Qubits**: 3 qubits (q[0], q[1] for data, q[2] for overflow flag); only q[0] and q[1] are measured.

3. **State evolution**:
   - Initial: |000⟩
   - X(q[1]): |010⟩ — encodes a=2 (binary 10)
   - X(q[0]): |011⟩ — adds 1, giving 3 (binary 11)
   - Toffoli(q[0], q[1], q[2]): |111⟩ — flag q[2]=1 since value ≥ 3
   - CNOT(q[2], q[0]): |101⟩ — subtract 3 step 1 (flip LSB)
   - CNOT(q[2], q[1]): |001⟩ — subtract 3 step 2 (flip MSB)

4. **Measurement ordering**: M(q[1]) measured first (higher bit), M(q[0]) measured second (lower bit). Final state |001⟩ yields q[1]=0, q[0]=0, giving bitstring |00⟩ with probability 1.0.

## isqExpand/algo/133

- task_id: `isqExpand/algo/133`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `entanglement`
- source: `isq_expansion`
- dataset_index: `1350`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0944, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    Rz(4.1888, q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    Rz(2.0944, q[2]);
    CNOT(q[1], q[2]);
    Rx(1.0472, q[0]); Rx(1.0472, q[1]); Rx(1.0472, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
Cost layer: CNOT-Rz-CNOT for each edge. Angles: 2.0944, 4.1888, 2.0944.
Mixer: Rx(1.0472) on each qubit.

Heavy edge (0,2) drives asymmetry. Optimal cut states |010> and |101> dominate.
P(|010>) = P(|101>) ~ 0.477, others ~ 0.008.

### Reference answer

{'predicted_probs': [0.007812, 0.007813, 0.476562, 0.007813, 0.007813, 0.476562, 0.007813, 0.007812], 'explanation': 'QAOA with gamma=pi/3, beta=pi/6 on weighted triangle: w(0,1)=1, w(0,2)=2, w(1,2)=1. The stronger weight on edge (0,2) -> Rz(4.1888) vs Rz(2.0944). Optimal MaxCut: {0} vs {1,2}, cutting w01+w02=3. States |010> and |101> (complementary cuts) get P ~ 0.477 each.'}

## isqTrain/1004

- task_id: `isqTrain/1004`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `isq_syntax_for_loop`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2568`

### Prompt

Implement a quantum circuit in isQ: implements the qdrift pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. **Goal**: Implement qdrift pattern for H = XX + ZZ on initial state |10⟩

2. **Qubits**: 2 qubits (q[0] and q[1]), both measured

3. **State evolution**:

Starting state: |00⟩

After X(q[1]): |10⟩

Now let's trace through the qdrift implementation:

For H = XX + ZZ, with t = π/4, λ = 2, N = 4, τ = t*λ/N = π/4, rotation = 2τ = π/2

**Sample 1: ZZ term**
- CNOT(q[0], q[1]) on |10⟩ → |11⟩
- Rz(π/2, q[1]) on |11⟩ → e^{-iπ/4}|11⟩
- CNOT(q[0], q[1]) → e^{-iπ/4}|10⟩

Wait, let me recalculate. Rz(θ) = exp(-iθZ/2), so Rz(π/2)|1⟩ = exp(-iπ/4)|1⟩

Actually, let me be more careful. The ZZ interaction is exp(-iτ ZZ/2) = exp(-i(π/4)ZZ/2) with τ = π/4.

Actually, looking at the circuit:
- CNOT, Rz(θ), CNOT implements exp(-iθ/2 * ZZ) effectively

With Rz(π/2), this gives exp(-iπ/4 * ZZ)

**Sample 1: ZZ on |10⟩**
- |10⟩
- CNOT(q[0], q[1]): |11⟩
- Rz(π/2, q[1]): e^{-iπ/4}|11⟩
- CNOT(q[0], q[1]): e^{-iπ/4}|10⟩

**Sample 2: XX term**
XX in Hadamard basis: H⊗H converts XX to ZZ
- H(q[0]); H(q[1]) on e^{-iπ/4}|10⟩ → e^{-iπ/4}(|-+⟩)

Wait, H|0⟩ = |+⟩, H|1⟩ = |-⟩
So H⊗H|10⟩ = |-+⟩

- e^{-iπ/4}|-+⟩
- CNOT: |-⟩|+⟩ → since first qubit is |-⟩ = (|0⟩ - |1⟩)/√2, CNOT with target on second qubit:
  Actually wait, CNOT(q[0], q[1]) means q[0] is control, q[1] is target.
  
  |-+⟩ = (|0⟩ - |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2 = (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
  
  After CNOT(q[0], q[1]):
  (|00⟩ + |01⟩ - |11⟩ - |10⟩)/2 = (-|10⟩ - |11⟩ + |00⟩ + |01⟩)/2 = |-+⟩
  
  Hmm, that's the same state. That's because CNOT doesn't change the state in the Hadamard basis in this way... Let me recalculate.
  
  Actually, |-+⟩ after CNOT:
  CNOT|00⟩ = |00⟩, CNOT|01⟩ = |01⟩, CNOT|10⟩ = |11⟩, CNOT|11⟩ = |10⟩
  
  So CNOT(|00⟩ + |01⟩ - |10⟩ - |11⟩)/2 = (|00⟩ + |01⟩ - |11⟩ - |10⟩)/2
  
  That's the same as the input, so it stays |-+⟩. Hmm, but that doesn't seem right for implementing the rotation.
  
  Wait, actually the CNOT conjugated by Hadamards implements a ZZ rotation. The structure is:
  H⊗H → CNOT → Rz(θ) → CNOT → H⊗H
  
  This implements something like exp(-iθ XX/2).

Let me redo this more carefully.

After Sample 1: e^{-iπ/4}|10⟩

Sample 2: XX term
- H(q[0]), H(q[1]): e^{-iπ/4}|-+⟩
- CNOT(q[0], q[1]): Need to compute CNOT on |-+⟩

|-+⟩ = (|0⟩ - |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2
     = (|00⟩ + |01⟩ - |10⟩ - |11⟩

## isqTrain/4574

- task_id: `isqTrain/4574`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4104`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[4];

procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure diffuser() {
    H(q[3]); H(q[1]); H(q[2]);  // target different qubit
    X(q[0]); X(q[1]); X(q[2]);
    ctrl ctrl my_z(q[0], q[1], q[2]);
    
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
}

procedure main() {
    
    X(q[3]); H(q[3]);
    
    H(q[0]); H(q[1]); H(q[2]);
    
    
    ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]); 
    diffuser();
    
    
    ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]); 
    diffuser();
    
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

This is a Grover's search algorithm implementation with 2 iterations. Let me trace through the circuit carefully.

We have 4 qubits: q[0], q[1], q[2], q[3].

**Initialization:**
- q[3]: X then H → |-> state (eigenstate of X with eigenvalue -1)
- q[0], q[1], q[2]: H on each → equal superposition over 8 states

Initial state: (1/√8) Σ_{x∈{0,1}^3} |x>|-> = (1/√8)(Σ_x |x>)(|0>-|1>)/√2

**Oracle 1:** `ctrl ctrl ctrl X(q[0], q[1], q[2], q[3])`
This is a multi-controlled X on q[3] with q[0], q[1], q[2] as controls. It flips q[3] when q[0]=q[1]=q[2]=1.

Since q[3] is in |-> state, this effectively marks |111> with a phase flip. After the oracle, the state becomes:
(1/√8)(Σ_x (-1)^{f(x)} |x>)|-> where f(x) = 1 iff x = 111.

Wait, but we only measure q[0], q[1], q[2]. The q[3] ancilla stays in |-> throughout (phase kickback).

**Diffuser 1:** Now let me trace the diffuser carefully.

The diffuser acts on q[0], q[1], q[2] (and accidentally includes H on q[3] which shouldn't matter much... wait, let me re-read):

Wait, this is unusual. The diffuser has H(q[3]) at the beginning but NOT at the end. This is different from a standard diffuser. Let me trace this carefully.

Actually, looking more carefully: the diffuser applies H to q[3], q[1], q[2] at the start. Then at the end, it applies H to q[0], q[1], q[2]. So q[3] gets H applied once (at start) but not uncomputed.

This is important. Let me track the state of q[3] as well.

Let me start over and track all 4 qubits.

**Initial state:** |0000>

**After X(q[3]):** |0001>

**After H(q[3]):** |0000>(1/√2)(|0>-|1>) = (1/√2)(|0000> - |0001>)

Actually, let me just track the full 4-qubit state.

After X(q[3]); H(q[3]): q[3] is in |-> = (|0>-|1>)/√2

After H(q[0]); H(q[1]); H(q[2]): 
State = (1/√8)(|000>+|001>+|010>+|011>+|100>+|101>+|110>+|111>) ⊗ (|0>-|1>)/√2

= (1/4)(|0000>-|0001>+|0010>-|0011>+|0100>-|0101>+|0110>-|0111>+|1000>-|1001>+|1010>-|1011>+|1100>-|1101>+|1110>-|1111>)

**Oracle 1:** ctrl ctrl ctrl X(q[0], q[1], q[2], q[3])
This flips q[3] when q[0]=q[1]=q[2]=1. So |1110> ↔ |1111>.

State after oracle:
(1/4)(|0000>-|0001>+|0010>-|0011>+|0100>-|0101>+|0110>-|0111>+|1000>-|1001>+|1010>-|1011>+|1100>-|1101>-|1110>+|1111>)

So the |111x> components had their signs swapped. The |111> component in the first 3 qubits now has the opposite sign.

**Diffuser 1:**

Let me trace through the diff

### Reference answer

{'predicted_probs': {'0000': 0.03125, '0001': 0.03125, '0010': 0.03125, '0011': 0.03125, '0100': 0.28125, '0101': 0.28125, '0110': 0.28125, '0111': 0.03125}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0000>) = 0.0312, P(|0001>) = 0.0312, P(|0010>) = 0.0312, P(|0011>) = 0.0312, P(|0100>) = 0.2812, P(|0101>) = 0.2812, P(|0110>) = 0.2812, P(|0111>) = 0.0312.'}

## isqExpand/algo/171

- task_id: `isqExpand/algo/171`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `half_adder`, `toffoli_gate`, `cnot_gate`, `arithmetic_circuit`, `measurement`
- source: `isq_expansion`
- dataset_index: `3485`

### Prompt

Implement a quantum circuit in isQ: an isQ quantum program that implements a half adder to compute 1+1. Use 4 qubits: q[0] and q[1] as inputs (both initialized to |1⟩), q[2] for carry, and q[3] for sum. Use a Toffoli gate for the carry (AND) and CNOT gates for the sum (XOR). Measure the carry and sum qubits at the end.

### Chain-of-thought reasoning

A half adder computes sum = a XOR b and carry = a AND b. For 1+1: a=1, b=1, so sum=0 and carry=1. We use 4 qubits: q[0]=a=1, q[1]=b=1, q[2]=carry, q[3]=sum. Initialize inputs with X gates. CNOT(q[0],q[3]) copies a into sum; CNOT(q[1],q[3]) XORs b giving sum=a XOR b=0. Toffoli(q[0],q[1],q[2]) computes carry=a AND b=1. Final state: q[0]=1,q[1]=1,q[2]=1,q[3]=0 which is |0111⟩ = index 7 (q[0] is LSB). So expected_probs[7]=1.0, all others 0.

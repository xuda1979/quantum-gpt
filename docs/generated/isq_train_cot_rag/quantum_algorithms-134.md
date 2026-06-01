# ISQ training COT RAG corpus: quantum_algorithms shard 134

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4134

- task_id: `isqTrain/4134`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `5050`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[4];

procedure main() {
    X(q[3]);
    H(q[0]); H(q[1]); H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 5.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 5.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 5.0 / 8.0 * 4.0, q[2], q[3]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    ctrl Rz(-3.14159265358979 / 4.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 2.0, q[2], q[1]);
    H(q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

The user wants to predict the measurement output of an isQ circuit and describe the probability distribution.
The circuit is essentially the Quantum Fourier Transform (QFT) followed by its inverse (IQFT) applied to a specific state, or maybe just QFT followed by some operations. Wait, let's trace it carefully.

Initial state: |0000>
X(q[3]) -> |0001>
H(q[0]); H(q[1]); H(q[2]) -> |+++1> = 1/sqrt(8) sum_{x=0}^3 |x, 1>

Then there are controlled-Rz gates:
ctrl Rz(2*pi * 5/8 * 1, q[0], q[3])
ctrl Rz(2*pi * 5/8 * 2, q[1], q[3])
ctrl Rz(2*pi * 5/8 * 4, q[2], q[3])

Wait, the target is q[3]!
This looks like phase encoding. If we use the computational basis |x_0 x_1 x_2 1>, where q[0] is the least significant bit (so x_0 is bit 0, etc).
Wait, if q[0] is control, the phase added is 5/8 * 1 * 2pi * x_0.
If q[1] is control, phase added is 5/8 * 2 * 2pi * x_1.
If q[2] is control, phase added is 5/8 * 4 * 2pi * x_2.
So phase added is 5/8 * (x_0 + 2 x_1 + 4 x_2) * 2pi = 5/8 * x * 2pi.
So this prepares the state 1/sqrt(8) sum_{x=0}^7 exp(i * 2pi * (5/8) * x) |x>|1>.
Actually, Rz(theta) is a rotation around Z. If we use the definition Rz(theta) = exp(-i Z theta / 2).
Wait, the standard isQ ctrl Rz might apply a phase to the target.
Let's see the QFT part.
Then:
CNOT(q[0], q[2]);
CNOT(q[2], q[0]);
CNOT(q[0], q[2]);
This is a swap (three-CNOT decomposition) between q[0] and q[2].

Then:
H(q[0]);
ctrl Rz(-pi/2, q[1], q[0]);  -> controlled by q[1], target q[0]. This is CRk with k=2. (Usually Rz(pi/2) is T or S? Rz(-pi/2) corresponds to phase -1/4)
ctrl Rz(-pi/4, q[2], q[0]);
H(q[1]);
ctrl Rz(-pi/2, q[2], q[1]);
H(q[2]);
This is exactly the Inverse QFT!
Wait, let's check the standard IQFT on 3 qubits.
Start with swapping qubits? The swap (three-CNOT decomposition) was applied *before* the IQFT operations!
In QFT, the operations are H, then CRk, then swap (three-CNOT decomposition).
So if we apply swap (three-CNOT decomposition) first, then H and CRk, that is actually QFT!
Wait, standard QFT:
H(q[0])
CR(q[1], q[0], pi/2)
CR(q[2], q[0], pi/4)
H(q[1])
CR(q[2], q[1], pi/2)
H(q[2])
swap (three-CNOT decomposition)(q[0], q[2])
So QFT is H, CR, swap (three-CNOT decomposition).
If we do swap (three-CNOT decomposition) first, then H, CR, that is exactly the same as QFT without the trailing swap (three-CNOT decomposition). Wait, no.
Standard QFT in bit-reversed order is just H, CR.
Let's trace the matrix.
Let's evaluate the state after phase encoding: 1/sqrt(8) sum exp(i 2pi 5/8 x) |x>.
Let's write the binary representation of x. q[0] is bit 0, q[1] is bit 1, q[2] is bit 2.
Actually, let's consider the standard QFT definition.
$QFT |x\rangle = \frac{1}{\sqrt{N}} \sum_y \omega^{x y} |y\rangle$.
If the phase encoding prepares $| \psi \rangle = \sum_x e^{i 2\pi (5/8) x} |x\rangle$, and then we apply QFT again?
Wait, the IQFT usually has negative phases: CRz(-pi/2) etc.
But

### Reference answer

Dominant output states: |1101> with probability ~0.43 each

## isqTrain/3618

- task_id: `isqTrain/3618`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1239`

### Prompt

Write an isQ program that a 4-qubit Grover search for target state |0011> using the optimal 3 iterations. The circuit should:
1. Initialize 4 qubits in uniform superposition
2. Apply 3 Grover iterations (oracle + diffusion) using a for loop
3. Measure all 4 qubits
Use `deriving gate` and `ctrl<2> CZ` for the multi-controlled phase.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Use Grover's algorithm on 4 qubits to amplify the amplitude of target state |0011>.
2. **Qubits**: 4 qubits (q[0]–q[3]), all measured at the end.
3. **Initialization**: H⊗4 on |0000> produces uniform superposition |s⟩ = (1/4)∑|x⟩ over 16 basis states, each with amplitude 1/4.
4. **Oracle**: X on q[0], q[1] maps |0011>→|1111>; `ctrl<2> CZ` applies a -1 phase to |1111>; X gates restore, yielding a phase flip on |0011> only.
5. **Diffusion**: H⊗4 → X⊗4 → `ctrl<2> CZ` (reflects |1111>) → X⊗4 → H⊗4 reflects all amplitudes about the mean, amplifying the marked state.
6. **3 iterations**: For N=16, optimal k ≈ π/(4·arcsin(1/4)) ≈ 2.6; choosing k=3 gives amplitude sin(7θ) where θ=arcsin(1/4), yielding |⟨0011|ψ⟩|² ≈ 0.963.
7. **Measurement**: |0011> has probability ~0.963; all other 15 states share ~0.037 total (~0.00244 each).

## isqTrain/733

- task_id: `isqTrain/733`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `phase_manipulation`, `qft_based_arithmetic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `288`

### Prompt

Write an isQ program that implements a variant of the qft_adder pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The task asks me to write reasoning for a QFT adder variant that uses q[2] -> q[4], meaning a 4-qubit register where the QFT operations act on qubits 2 through 4 (but wait, q[2] to q[4] would be indices 2, 3 - that's only 2 qubits).

Analyzing the circuit requirements:
- 4 qubits total: q[0], q[1], q[2], q[3]
- Input state prepared on q[0] and q[1] as |11>
- QFT is applied to q[0] and q[1] (2-qubit QFT)
- q[2] and q[3] are left in |0> state
- All 4 qubits are measured

Wait, the prompt says "q[2] -> q[4]" which might mean expanding from a 2-qubit register to a 4-qubit register, with additional qubits in ground state.

Let me trace through the circuit:

Initial state: |0000>

After X(q[0]), X(q[1]): |1100>

2-qubit QFT on q[0], q[1]:
1. H(q[1]): This acts on q[1] (the MSB in big-endian convention for QFT)
   |11> → H on q[1] → (|01> + |11>)/√2 (in terms of q[1],q[0])
   
Actually, let me be more careful. Let's write the full 4-qubit state.

State: |q[0]q[1]q[2]q[3]>

After X(q[0]), X(q[1]):
|1100>

2-qubit QFT on q[0] and q[1]:

Step 1: H(q[1])
|1100> → (|1000> - |1100>)/√2

Wait, H|1> = (|0> - |1>)/√2
So |11>_q[0],q[1] with H on q[1]:
|1>_q[0] ⊗ H|1>_q[1] ⊗ |00>_{q[2],q[3]}
= |1>_q[0] ⊗ (|0> - |1>)/√2_{q[1]} ⊗ |00>
= (|10> - |11>)/√2 ⊗ |00>
= (|1000> - |1100>)/√2

Step 2: ctrl S(q[0], q[1])
S = diag(1, i), so controlled-S applies S to q[1] when q[0] is |1>

State: (|1000> - |1100>)/√2

For the |1000> component: q[0]=1, q[1]=0 → S|0> = |0>, no change
For the |1100> component: q[0]=1, q[1]=1 → S|1> = i|1>

Result: (|1000> - i|1100>)/√2

Step 3: H(q[0])
H|1> on q[0]:
(|0> - |1>)/√2

So (|1000> - i|1100>)/√2
= (|1>_q[0] ⊗ |0>_q[1] - i|1>_q[0] ⊗ |1>_q[1]) ⊗ |00> / √2
= |1>_q[0] ⊗ (|0> - i|1>)_q[1] ⊗ |00> / √2
= [(|0> - |1>)/√2]_q[0] ⊗ (|0> - i|1>)_q[1] ⊗ |00> / √2
= (|0000> - |0100> - i|1000> + i|1100>) / 2

Hmm, let me redo this more carefully.

After H(q[0]):
State is (|1000> - i|1100>)/√2

Applying H to q[0]:
|1> → (|0> - |1>)/√2

|1000> → (|0000> - |1000>)/√2
|1100> → (|0100> - |1100>)/√2

New state: [(|0000> - |1000>)/√2 - i(|0100> - |1100>)/√2] / √2
= (|0000> - |1000> - i|010

## isqTrain/2883

- task_id: `isqTrain/2883`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `735`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```isq
import std;
qbit q[4];
// Multi-controlled X with 3 controls
procedure main() {
    X(q[0]);
    X(q[1]);
    // X(q[2]); // BUG: missing initialization
    ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug**: The initialization for `q[2]` is commented out (`// X(q[2]);`). This leaves `q[2]` in the initial $|0\rangle$ state instead of $|1\rangle$.
2. **The Fix**: Uncomment the `X(q[2]);` gate to properly initialize the qubit to $|1\rangle$ before the multi-controlled operation.
3. **State Evolution**: 
   - Initial state: $|0000\rangle$
   - After `X(q[0])`, `X(q[1])`, and `X(q[2])`: $|1110\rangle$
   - After `ctrl ctrl ctrl X(q[0], q[1], q[2], q[3])`: Since all three control qubits are in $|1\rangle$, the target `q[3]` is flipped, resulting in the final state $|1111\rangle$.

## isqTrain/3451

- task_id: `isqTrain/3451`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `boolean_logic`, `reversible_computing`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2655`

### Prompt

Help me write isQ code that the inner product mod 2 oracle for two 2-bit strings in isQ.

Given x = (x0, x1) and y = (y0, y1), compute:
  f(x,y) = (x0*y0 + x1*y1) mod 2

This is the inner product mod 2, which is a useful building block.

Test case: x = 11, y = 10. f = (1*1 + 1*0) mod 2 = 1.

Use 4 data qubits (x0,x1,y0,y1) and 1 ancilla for the result.
Oracle: Toffoli(x0, y0, anc) then Toffoli(x1, y1, anc).
This XORs x0*y0 and x1*y1 into the ancilla.

Declare 4 data qubits and 1 ancilla. Measure all 5.

### Chain-of-thought reasoning

## Reasoning
Goal: Compute inner product mod 2 of two 2-bit strings x=(1,1) and y=(1,0), storing result in ancilla.

5 qubits: q[0]=x0, q[1]=x1, q[2]=y0, q[3]=y1, q[4]=result.

**State evolution:**
1. Initial: |00000⟩
2. X(q[0]), X(q[1]), X(q[2]): |11100⟩ (sets x=11, y=10)
3. Toffoli(q[0], q[2], q[4]): Since x0=1 and y0=1, flips q[4] → |11101⟩ (XORs x0·y0=1 into result)
4. Toffoli(q[1], q[3], q[4]): Since x1=1 but y1=0, no flip → |11101⟩ (XORs x1·y1=0, result stays 1)

Final state |11101⟩ gives measurement outcome with probability 1.0, confirming f=(1·1+1·0) mod 2 = 1.

## isqTrain/3447

- task_id: `isqTrain/3447`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1759`

### Prompt

I need an isQ program to 4-qubit W-state preparation in isQ.

The 4-qubit W state is:
|W4> = (|0001> + |0010> + |0100> + |1000>) / 2

Each computational basis state has exactly one qubit in |1>.
Each such state has probability 1/4.

Use a chain of controlled rotations and CNOTs:
1. X(q[0]) to start with |1000>
2. Ry(2*arccos(sqrt(1/4))) = Ry(2*arccos(0.5)) = Ry(2*pi/3) on q[0]
3. Transfer and split amplitudes using controlled gates

Declare 4 qubits, measure all.

### Chain-of-thought reasoning

Let me analyze this 4-qubit W-state preparation circuit step by step.

The goal is to prepare |W4⟩ = (|0001⟩ + |0010⟩ + |0100⟩ + |1000⟩)/2

Let me trace through the state evolution:

1. Initial state: |0000⟩
2. X(q[0]): |1000⟩
3. Ry(2π/3, q[0]): This rotates q[0]. Ry(2π/3) with input |1⟩ gives cos(π/3)|1⟩ + sin(π/3)|0⟩ = 0.5|1⟩ + (√3/2)|0⟩
   Wait, let me be more careful. The Ry matrix is:
   Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]
   
   So Ry(2π/3) applied to |1⟩ = [0, 1]:
   cos(π/3)|1⟩ - sin(π/3)|0⟩... no wait:
   
   Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
   Ry(θ)|1⟩ = -sin(θ/2)|0⟩ + cos(θ/2)|1⟩
   
   Ry(2π/3)|1⟩ = -sin(π/3)|0⟩ + cos(π/3)|1⟩ = -(√3/2)|0⟩ + (1/2)|1⟩
   
   State becomes: -(√3/2)|0000⟩ + (1/2)|1000⟩
   
   Hmm, but the angles and ordering... Let me think about what The predicted output: {|0001⟩: 0.125, |0010⟩: 0.125, |0100⟩: 0.5, |1000⟩: 0.25}

Wait, that doesn't look like a W state with equal amplitudes. Let me re-read...

The expected measurement probabilities show:
- |0001⟩: 0.125 = 1/8
- |0010⟩: 0.125 = 1/8
- |0100⟩: 0.5 = 1/2
- |1000⟩: 0.25 = 1/4

This is NOT a uniform W state! The amplitudes are sqrt(1/8), sqrt(1/8), sqrt(1/2), sqrt(1/4) = 1/(2√2), 1/(2√2), 1/√2, 1/2.

Hmm, but the prompt says the W state should be (|0001⟩+|0010⟩+|0100⟩+|1000⟩)/2 with equal probability 1/4 each. But the predicted output doesn't match that.

Let me re-examine. Maybe the predicted output in the prompt is wrong, or maybe I should just describe what the code actually does.

Actually wait - looking at the predicted output again, the prompt says:
"Expected measurement probabilities: {|0001>: 0.125, |0010>: 0.125, |0100>: 0.5, |1000>: 0.25}"

This might be intentionally showing that The implementation doesn't produce the correct W state, or there might be some qubit ordering issue.

Let me trace through more carefully:

The qubits are q[0], q[1], q[2], q[3]. In the bitstring representation for --probs, "earlier measured qubit = higher bit."

So M(q[0]) first → highest bit, M(q[1]) → next, M(q[2]) → next, M(q[3]) → lowest bit.

So bitstring |b3 b2 b1 b0⟩ where b0 corresponds to q[0] measurement.

Wait, let me reconsider. If q[0] is measured first and is the highest bit, then the bitstring would be q[0]q[1]q[2]q[3].

|1000⟩ means q[0]=1, q[1]=0, q[2]=0, q[3]=0.

OK so let me trace through the circuit:

1. Start: |0000⟩ (all qubits in |0⟩)
2. X(q[0]): |1000⟩ (qubit 0 is |1⟩)
3. Ry(2π/3, q[0]): Rotates q[0]. Applied to |1⟩:
   Ry(2π/3)|1⟩ = -sin(π/3)|0⟩ + cos(π/3)|1⟩ = -(√3/2

## isqTrain/2654

- task_id: `isqTrain/2654`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `global_phase`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2860`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[6];

procedure main() {
    // Encode a = 1 in GF(3): binary 01
    X(q[0]);
    // Encode b = 2 in GF(3): binary 10
    X(q[3]);
    // GF(3) multiplication by 1 is identity
    // Copy b register to product register
    CNOT(q[2], q[4]);
    CNOT(q[3], q[5]);
    // Measure the product register
    M(q[4]);
    M(q[5]);
}

```

vs.

```isq
import std;
qbit q[6];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Encode a = 1 in GF(3): binary 01
    X(q[0]);
    // Encode b = 2 in GF(3): binary 10
    X(q[3]);
    // GF(3) multiplication by 1 is identity
    // Copy b register to product register
    CNOT(q[2], q[4]);
    CNOT(q[3], q[5]);
    // Measure the product register
    M(q[4]);
    M(q[5]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A initializes 6 qubits to |0>, applies X gates to q[0] and q[3] putting them in |1>, and uses CNOT gates to classically copy the |0> state of q[2] to q[4] and the |1> state of q[3] to q[5]. It measures q[4] and q[5].
2. Program B performs the exact same operations but explicitly includes a `GPhase(0.0)` gate at the beginning.
3. The only difference is the `GPhase(0.0)` gate, which applies a global phase of $e^{i0} = 1$. This operation acts as an identity gate, leaving the quantum state mathematically and physically unchanged.
4. Since the global phase is exactly 1, the quantum states of both programs are identical at all steps. Thus, the measurement probabilities are exactly the same (100% probability of measuring q[4]=0 and q[5]=1).
5. Verdict: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/2003

- task_id: `isqTrain/2003`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3176`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    X(q[1]);
    Toffoli(q[0], q[1], q[2]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initialization:** The circuit starts with 3 qubits in the initial state $|000\rangle$.
2. **State Evolution:**
   - `X(q[0])` flips the first qubit, updating the state to $|100\rangle$.
   - `X(q[1])` flips the second qubit, updating the state to $|110\rangle$.
   - `Toffoli(q[0], q[1], q[2])` applies an X gate to the third qubit if both controls (q[0] and q[1]) are in the $|1\rangle$ state. Since both are $|1\rangle$, the target qubit is flipped, changing the state to $|111\rangle$.
3. **Final State:** The quantum state before measurement is $|111\rangle$.
4. **Measurement:** Measuring `q[2]` finds it in the $|1\rangle$ state with absolute certainty.

**Predicted probability distribution:**
- `1`: 1.0

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Equality check a=3 == 3: result=1 with P=1.0.'}

## isqTrain/1112

- task_id: `isqTrain/1112`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `224`

### Prompt

Write an isQ program that implements the simon_algorithm pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to analyze the Simon's algorithm pattern with the given isQ code.

The circuit is:
1. Initialize |q0 q1 out0 out1⟩ = |0000⟩
2. H(q[0]); H(q[1]) creates superposition on input register
3. Oracle f(q, out) maps based on f(x) = x0 XOR x1
4. H(q[0]); H(q[1]) Hadamard on input register
5. H(q[0]); H(q[0]) - identity pair (demonstrates gate cancellation)
6. M(q[0]); M(q[1]) measure input qubits

Wait, let me reconsider the circuit. The output register is also involved but the oracle function `f` is called which computes f(x) and stores in `out`.

The oracle f has the property:
- f(00) = 00
- f(01) = 01  
- f(10) = 01
- f(11) = 00

So s = 11 (since f(x) = f(x ⊕ s) means f(00) = f(11) and f(01) = f(10)).

Let me trace through:

1. Initial state: |0000⟩ (q[0], q[1], out[0], out[1])

2. H(q[0]); H(q[1]): creates (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩) ⊗ |00⟩

3. Oracle f(q, out): For each |x⟩|00⟩, creates |x⟩|f(x)⟩
   State becomes: (1/2)(|00⟩|00⟩ + |01⟩|01⟩ + |10⟩|01⟩ + |11⟩|00⟩)
   
   Grouping by f(x):
   = (1/2)(|00⟩ + |11⟩)|00⟩ + (1/2)(|01⟩ + |10⟩)|01⟩

4. H(q[0]); H(q[1]) on input register:
   H⊗2(|00⟩ + |11⟩) = H⊗2|00⟩ + H⊗2|11⟩
   
   H⊗2|00⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
   H⊗2|11⟩ = (1/2)(|00⟩ - |01⟩ - |10⟩ + |11⟩)
   
   H⊗2(|00⟩ + |11⟩) = (1/2)(2|00⟩ + 0|01⟩ + 0|10⟩ + 2|11⟩) = |00⟩ + |11⟩
   
   H⊗2(|01⟩ + |10⟩):
   H⊗2|01⟩ = (1/2)(|00⟩ - |01⟩ + |10⟩ - |11⟩)
   H⊗2|10⟩ = (1/2)(|00⟩ + |01⟩ - |10⟩ - |11⟩)
   H⊗2(|01⟩ + |10⟩) = (1/2)(2|00⟩ + 0|01⟩ + 0|10⟩ - 2|11⟩) = |00⟩ - |11⟩

   So after H⊗2:
   State = (1/2)(|00⟩ + |11⟩)|00⟩ + (1/2)(|00⟩ - |11⟩)|01⟩

5. H(q[0]); H(q[0]) = Identity on q[0], so no change.

6. Measure q[0] and q[1]:
   
   The input register state (tracing out out) is:
   (1/2)(|00⟩ + |11⟩)|00⟩_out + (1/2)(|00⟩ - |11⟩)|01⟩_out
   
   The probability of measuring |00⟩ on q[0],q[1]:
   |1/2 * 1|² + |1/2 * 1|² = 1/4 + 1/4 = 1/2
   
   The probability of measuring |11⟩ on q[0],q[1]:
   |1/2 * 1|² + |1/2 * (-1)|² = 1/4 + 1/4 = 1/2

So P(|00⟩) = 0.5, P(|11⟩) = 0.5. ✓

This makes sense because Simon's algorithm gives us y such that y·s = 0 mod 2. With s = 11, the valid y values are y = 00 and y = 10 (wait, let me recalculate).

y·s = y₀s₀ +

## isqTrain/949

- task_id: `isqTrain/949`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `hamiltonian_simulation`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3307`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the pauli_evolution pattern using q[1] -> q[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement a Pauli-Z evolution variant on a 2-qubit register, applying phase rotation to q[0] while q[1] remains idle.

**Qubits:** 2 qubits declared (q[0], q[1]); both are measured.

**State evolution:**
1. Initial: |00⟩
2. H(q[0]): → (|0⟩ + |1⟩)|0⟩/√2 = (|00⟩ + |10⟩)/√2
3. Rz(π/2, q[0]): Applies e^(-iπ/4) to |0⟩ and e^(iπ/4) to |1⟩ → e^(-iπ/4)(|00⟩ + e^(iπ/2)|10⟩)/√2 = e^(-iπ/4)(|00⟩ + i|10⟩)/√2
4. H(q[0]): Transforms (|0⟩ + i|1⟩)/√2 → ((1+i)|0⟩ + (1-i)|1⟩)/2, giving final state: ((1+i)|00⟩ + (1-i)|10⟩)/2

**Probabilities:** |(1+i)/2|² = 2/4 = 0.5 for |00⟩; |(1-i)/2|² = 2/4 = 0.5 for |10⟩. Since q[1] is never operated on, it stays |0⟩, so only |00⟩ and |10⟩ outcomes are possible with equal probability.

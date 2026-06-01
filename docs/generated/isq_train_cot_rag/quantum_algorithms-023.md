# ISQ training COT RAG corpus: quantum_algorithms shard 23

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/837

- task_id: `isqTrain/837`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4755`

### Prompt

Code this in isQ: implements a variant of the gfp_multiplication pattern using q[6] -> q[8]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement GF(3) multiplication (1 × 2 = 2) with an expanded 8-qubit register, where q[6] and q[7] are unused ground-state qubits.

**Qubits:** 8 total (q[0..7]); measuring q[4], q[5], q[6], q[7] (4 qubits).

**State evolution:**
1. Initial: |00000000⟩
2. X(q[0]) encodes a=1 (binary 01): |10000000⟩
3. X(q[3]) encodes b=2 (binary 10): |10010000⟩
4. CNOT(q[2], q[4]): control q[2]=|0⟩, no flip → |10010000⟩
5. CNOT(q[3], q[5]): control q[3]=|1⟩, flips q[5] → |

## isqTrain/3939

- task_id: `isqTrain/3939`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4952`

### Prompt

修复以下isQ程序中的错误：

```
import std;
// QAOA MaxCut p=1 on 3-node star graph
// gamma=0.500, beta=1.000
qbit q[3];

procedure main() {
    // Initial superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Cost unitary U_C(gamma)
    // Edge (0,1): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[1]);
    Rz(2.0 * 2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    // Edge (0,2): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[0], q[2]);
    // Mixer unitary U_M(beta)
    Rx(2.0 * 1.000, q[0]);
    Rx(2.0 * 1.000, q[1]);
    Rx(2.0 * 1.000, q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

**Bug:** In the cost unitary for edge (0,1), the Rz rotation has an extra factor of 2.0: `Rz(2.0 * 2.0 * 0.500, q[1])` computes angle 2.0 instead of the correct 1.0.

**Fix:** Change `Rz(2.0 * 2.0 * 0.500, q[1])` to `Rz(2.0 * 0.500, q[1])`, matching the correct decomposition of exp(-iγ Z₀Z₁) via CNOT-Rz(2γ)-CNOT.

**Corrected state evolution:**
1. **Init:** |000⟩
2. **H⊗3:** |+++⟩ = equal superposition of all 8 basis states
3. **U_C (edge 0,1):** CNOT₀₁ → Rz(1.0, q₁) → CNOT₀₁ applies phase e^{-iγ} when |q₀⊕q₁⟩=|1⟩, i.e., penalizing same-color assignments
4. **U_C (edge 0,2):** CNOT₀₂ → Rz(1.0, q₂) → CNOT₀₂ applies same phase penalty for edge (0,2)
5. **U_M:** Rx(2.0, qᵢ) on all qubits mixes computational basis states
6. **Result:** Cut states |011⟩ and |100⟩ (node 0 on one side, nodes 1,2 on other) are amplified to ~0.321 each, matching expected MaxCut solutions

## isqTrain/2979

- task_id: `isqTrain/2979`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1479`

### Prompt

Write an isQ program that applies a controlled-Hadamard gate. Set the control qubit to |1>, then apply controlled-H to the target. Measure all 2 qubits.

Requirements:
- Declare `qbit q[2];` at global scope.
- Measure all 2 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate a controlled-Hadamard gate where the control qubit is set to |1⟩, triggering H on the target.
2. **Qubits**: 2 qubits declared globally (`qbit q[2]`), both measured.
3. **State evolution**:
   - Initial state: |00⟩
   - After X(q[0]): |10⟩ (control flipped to |1⟩)
   - After ctrl H(q[0], q[1]): Since q[0] = |1⟩, H applies to q[1], transforming |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2, yielding (|10⟩ + |11⟩)/√2
4. **Probabilities**: Equal amplitude magnitudes give P(|10⟩) = P(|11⟩) = |1/√2|² = 0.5 each.

## isqTrain/4826

- task_id: `isqTrain/4826`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_import_qft`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4791`

### Prompt

用isQ实现applies QFT to a single qubit, demonstrating that 1-qubit QFT is equivalent to Hadamard. Import std and qft. Declare 1 global qubit. Apply qft(q). Measure the qubit. Expected: equal superposition (50/50).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that applying the Quantum Fourier Transform (QFT) to a single qubit prepares an equal superposition, equivalent to the Hadamard gate.
2. **Qubits**: 1 global qubit `q[0]`, which is measured.
3. **Steps**:
   - Initialize `q[0]` to |0⟩.
   - Apply `qft(q)`: For a single qubit, the QFT is exactly the Hadamard gate (H).
   - The quantum state becomes H|0⟩ = (|0⟩ + |1⟩)/√2 = |+⟩.
4. **Probabilities**: Measuring |+⟩ in the computational basis yields a 50% probability for |0⟩ and a 50% probability for |1⟩.

## isqTrain/1175

- task_id: `isqTrain/1175`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `146`

### Prompt

I need an isQ program to implements a variant of the fourier_checking pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this Fourier checking/forrelation variant circuit carefully.

The circuit uses 3 qubits q[0], q[1], q[2], but q[2] is never acted upon - it stays in |0⟩ and is just measured.

The circuit structure is H-f-H-g-H on q[0] and q[1].

Let me trace through the state evolution:

Initial state: |000⟩

After first H layer on q[0], q[1]:
|00⟩ → |++⟩ on q[0],q[1], so state is |+0+⟩ = (1/2)(|000⟩ + |010⟩ + |100⟩ + |110⟩) ⊗ |0⟩₂

Wait, q[2] is always |0⟩. Let me focus on q[0], q[1].

Initial: |00⟩
After H⊗H: |++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

Phase oracle f: T on q[0], S on q[1]
T applies phase e^(iπ/4) to |1⟩ component, S applies phase i to |1⟩ component.

So the state becomes:
(1/2)(|00⟩ + i·|01⟩ + e^(iπ/4)·|10⟩ + i·e^(iπ/4)·|11⟩)

After H⊗H:
H|0⟩ = |+⟩, H|1⟩ = |−⟩

For each basis state |ab⟩, H⊗H maps it to (1/2)(|00⟩ + (−1)^b|01⟩ + (−1)^a|10⟩ + (−1)^(a+b)|11⟩)

So the amplitude of |00⟩ after H⊗H:
(1/2)[1 + i + e^(iπ/4) + i·e^(iπ/4)] · (1/2)

Let me compute: 1 + i + e^(iπ/4) + i·e^(iπ/4)
= 1 + i + e^(iπ/4)(1 + i)
= 1 + i + (cos(π/4) + i·sin(π/4))(1 + i)
= 1 + i + (1/√2 + i/√2)(1 + i)
= 1 + i + (1/√2)(1 + i)²
= 1 + i + (1/√2)(1 + 2i − 1)
= 1 + i + (1/√2)(2i)
= 1 + i + i√2
= 1 + i(1 + √2)

Amplitude of |00⟩ = (1/4)[1 + i(1 + √2)]
|amplitude|² = (1/16)[1 + (1 + √2)²] = (1/16)[1 + 1 + 2√2 + 2] = (1/16)[4 + 2√2] = (4 + 2√2)/16 = (2 + √2)/8

Let me verify: (2 + √2)/8 = (2 + 1.4142)/8 = 3.4142/8 = 0.42677...

Hmm, but the predicted output for |000⟩ is 0.7285... That's much larger. Let me reconsider.

Wait, I need to be more careful. The expected measurement output includes q[2] which is never touched, so it's always |0⟩. The probabilities given are for the 3-qubit system where q[2] is the least significant bit (index 2 = lowest bit? or highest bit?).

Actually, the --probs output says "earlier measured qubit = higher bit". So M(q[0]) is the highest bit, M(q[1]) is middle, M(q[2]) is lowest. So |000⟩ means all three are 0.

Since q[2] is never modified, it's always in |0⟩. So effectively we're looking at a 2-qubit computation on q[0], q[1] with q[2] always 0.

But the predicted output for |000⟩ is 0.7285... Let me recalculate more carefully.

Actually, wait. Let me re-examine. The probability for |000⟩ is given as 0.7285..., and there's also probability for |010⟩, |100⟩, and |110⟩. Since q[2] is always |0⟩, these correspond to 2-qubit states |00⟩, |01⟩, |10⟩, |11⟩ on q[0

## isqTrain/3614

- task_id: `isqTrain/3614`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `1617`

### Prompt

Help me write isQ code that a 3-qubit Grover search for target state |011> using 2 Grover iterations for higher amplification. The circuit:
1. Initialize 3 qubits in superposition
2. Apply oracle+diffusion twice
3. Measure all qubits
Use `deriving gate` for oracle and diffusion procedures.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a 3-qubit Grover search targeting |011> with 2 iterations.

Let me trace through the circuit:

1. Initialize 3 qubits |000>
2. Apply H to all: |+⟩|+⟩|+⟩ = (1/√8)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)

3. First oracle marks |011>:
   - The oracle flips the phase of |011>. Since CZ with controls on q[0] and q[1] targeting q[2] would mark |110>, we need to flip q[0] first to convert |011> to |110>.
   - X(q[0]) converts |011> to |111>... wait, let me reconsider.
   
   Actually, let me think about the oracle more carefully:
   - X(q[0]) flips qubit 0
   - ctrl CZ(q[0], q[1], q[2]) applies Z to q[2] when q[0]=1 AND q[1]=1 (this is a controlled-controlled-Z or double-controlled-Z (ctrl @[c1, c2] Z(target)))
   - X(q[0]) flips qubit 0 back
   
   So the double-controlled-Z (ctrl @[c1, c2] Z(target)) applies a phase flip when q[0]=1, q[1]=1, q[2]=1, i.e., to state |111⟩.
   
   But we apply X(q[0]) first, so |abc⟩ becomes |(1-a)bc⟩. Then double-controlled-Z (ctrl @[c1, c2] Z(target)) marks when all are 1, so it marks |1(1-a)bc⟩... wait, that's not right.
   
   Let me think again:
   - Start with state |abc⟩ where a, b, c are the bits of q[0], q[1], q[2]
   - X(q[0]): |abc⟩ → |(1-a)bc⟩
   - double-controlled-Z (ctrl @[c1, c2] Z(target)) on q[0], q[1], q[2]: flips phase when q[0]=1, q[1]=1, q[2]=1, so when 1-a=1 (i.e., a=0), b=1, c=1, which is |011⟩
   - X(q[0]): flips q[0] back
   
   So the oracle correctly marks |011⟩ with a phase flip.

4. First diffusion:
   The diffusion operator reflects about the mean/average state. For 3 qubits, it's:
   - H on all
   - X on all  
   - double-controlled-Z (ctrl @[c1, c2] Z(target)) (which flips phase of |111⟩)
   - X on all
   - H on all
   
   This is equivalent to 2|s⟩⟨s| - I where |s⟩ = |+++⟩ is the uniform superposition.

5. After first iteration:
   The amplitude of |011⟩ is amplified from 1/√8 to about sin(3θ) where θ = arcsin(1/√8).
   
   Let me calculate: sin(θ) = 1/√8, so θ ≈ 20.7°
   After 1 iteration, the target amplitude is sin(3θ) ≈ sin(62.1°) ≈ 0.884
   The non-target amplitudes are sin(θ)cos(3θ)/... 
   
   Actually, let me use the exact formula. The initial amplitude of the target is 1/√8.
   After oracle: -1/√8 for target, 1/√8 for others
   After diffusion: the amplitude of the target becomes 2⟨a⟩ - (-1/√8) where ⟨a⟩ is the mean.
   
   Mean = (7/√8 - 1/√8)/8 = 6/(8√8) = 3/(4√8)
   New target amplitude = 2(3/(4√8)) - (-1/√8) = 6/(4√8) + 1/√8 = 3/(2√8) + 1/√8 = 5/(2√8) = 5/(2*2√2) = 5/(4√2)
   
   Hmm, let me redo this more carefully.
   
   Actually for Grover with N=8 items and 1 target:
   - Initial amplitudes: all 1/√8
   - After oracle: target is -1/√8, others are 1/√8
   - Mean: (7*1/√8 + 1*(-1/√8))/8 = (7-1)/(8√8) = 6/(8√8) = 3/(4√8)
   -

## isqTrain/3543

- task_id: `isqTrain/3543`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `ancilla_usage`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5788`

### Prompt

What does this isQ program output when measured?

```
import std;

qbit q[5];

procedure main() {
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[3]);
    CNOT(q[0], q[4]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 5 qubits to the ground state: |00000⟩.
2. It applies four CNOT gates, all controlled by q[0] targeting q[1], q[2], q[3], and q[4] sequentially.
3. Because the control qubit q[0] remains in the |0⟩ state (no preceding gates modify it), the control condition for the CNOT gates is never satisfied.
4. Thus, the target qubits are not flipped, and the quantum state remains completely unchanged throughout the circuit.
5. The final state before measurement is |00000⟩.

Predicted probability distribution:
- |00000⟩: 100%

### Reference answer

{'predicted_probs': {'00000': 1.0}, 'explanation': 'The output is |00000> with probability 1.0'}

## isqTrain/3438

- task_id: `isqTrain/3438`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `2272`

### Prompt

Write isQ code for the following quantum task: Quantum Phase Estimation (QPE) in isQ for the Z gate using 2 precision qubits.

The Z gate has eigenvalues +1 (for |0>) and -1 (for |1>).
For eigenstate |1>: phase = pi, so theta = 1/2 in units of 2*pi.
With 2 precision qubits, theta=0.5 maps to binary 0.10 = |10>.

QPE circuit:
1. Prepare target in |1> (eigenstate of Z)
2. H on precision qubits
3. Controlled-Z^(2^k) from each precision qubit
   - prec[0] controls Z^2 = I (skip)
   - prec[1] controls Z^1 = Z
4. Inverse QFT on precision register
5. Measure precision qubits only

Declare prec[2] and tgt[1]. Measure prec[0] and prec[1].
Expected: |10> (theta = 0.5).

### Chain-of-thought reasoning

Let me analyze this QPE circuit for the Z gate with 2 precision qubits.

1. Goal: Implement QPE to estimate the phase of Z gate for eigenstate |1>
2. Qubits: prec[0], prec[1] (precision), tgt[0] (target). Only prec qubits are measured.

Let me trace through the state evolution:

Initial state: |00>|0> = |000>

After X(tgt[0]): |00>|1>

After H(prec[0]) and H(prec[1]): (1/2)(|00> + |01> + |10> + |11>)|1>

Controlled operations:
- prec[0] controls Z^2 = I: no gate needed
- prec[1] controls Z^1 = Z: applies Z to target when prec[1] is |1>

After ctrl Z(prec[1], tgt[0]):
State becomes: (1/2)(|00>|1> + |01>(Z|1>) + |10>|1> + |11>(Z|1>))
= (1/2)(|00>|1> - |01>|1> + |10>|1> - |11>|1>)
= (1/2)(|00> - |01> + |10> - |11>)|1>

Now let me trace through the inverse QFT on 2 qubits.

The QFT for 2 qubits is:
|00> → (1/2)(|00> + |01> + |10> + |11>)
|01> → (1/2)(|00> + e^{iπ/2}|01> + e^{iπ}|10> + e^{i3π/2}|11>) = (1/2)(|00> + i|01> - |10> - i|11>)
|10> → (1/2)(|00> + e^{iπ}|01> + e^{i2π}|10> + e^{i3π}|11>) = (1/2)(|00> - |01> + |10> - |11>)
|11> → (1/2)(|00> + e^{i3π/2}|01> + e^{i3π}|10> + e^{i9π/2}|11>) = (1/2)(|00> - i|01> - |10> + i|11>)

So QFT maps:
|00> → (1/2)(|00> + |01> + |10> + |11>)
|10> → (1/2)(|00> - |01> + |10> - |11>)

And inverse QFT maps:
(1/2)(|00> + |01> + |10> + |11>) → |00>
(1/2)(|00> - |01> + |10> - |11>) → |10>

Our state before IQFT is: (1/2)(|00> - |01> + |10> - |11>)|1>

This should map to |10>|1> under IQFT.

Let me verify the IQFT implementation in the code:
1. Swap prec[0] and prec[1]
2. H(prec[0])
3. ctrl Rz(-π/2, prec[1], prec[0])
4. H(prec[1])

Let me trace through step by step.

State: (1/2)(|00> - |01> + |10> - |11>)|1>

In terms of computational basis:
= (1/2)|0>|0> - (1/2)|0>|1> + (1/2)|1>|0> - (1/2)|1>|1> (times |1> for target)

where first qubit is prec[1] and second is prec[0] (for this notation).

Wait, let me be more careful. Let me use |prec[1], prec[0]> notation.

State: (1/2)(|00> - |01> + |10> - |11>) where first bit is prec[1], second is prec[0].

Actually, let me use standard notation where |ab> means prec[1]=a, prec[0]=b.

State = (1/2)(|00> - |01> + |10> - |11>)|1>

After swap (CNOT prec[0],prec[1]; CNOT prec[1],prec[0]; CNOT prec[0],prec[1]):
Swap exchanges prec[0] and prec[1], so |ab> → |ba>.

State = (1/2)(|00> - |10> + |01> - |11>)|1>
= (

## isqTrain/1255

- task_id: `isqTrain/1255`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1205`

### Prompt

Help me write isQ code that implements the error_correction_syndrome pattern. Include explicit identity operations in the circuit (X-X pair before M(syndrome[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement 3-qubit bit-flip code syndrome extraction to detect a bit-flip error on data[1].

**Qubits:** 5 total (data[0-2], syndrome[0-1]); only syndrome[0] and syndrome[1] are measured.

**State evolution:**
1. `X(data[0])`: |00000⟩ → |10000⟩
2. `CNOT(d[0],d[1]); CNOT(d[0],d[2])`: → |11100⟩ (logical |1⟩ = |111⟩)
3. `X(data[1])` (error injection): → |10100⟩
4. `CNOT(d[0],s[0])`: data[0]=1 → flip s[0]: |10110⟩
5. `CNOT(d[1],s[0])`: data[1]=0 → no flip: |10110⟩; syndrome[0] = 1⊕0 = 1
6. `CNOT(d[1],s[1])`: data[1]=0 → no flip: |10110⟩
7. `CNOT(d[2],s[1])`: data[2]=1 → flip s[1]: |10111⟩; syndrome[1] = 0⊕1 = 1
8. `X(s[0]); X(s[0])`: identity pair (gate cancellation) — no state change

**Result:** Syndrome qubits are in |11⟩, correctly indicating error on data[1]. Probability: {|11⟩: 1.0}.

## isqTrain/2982

- task_id: `isqTrain/2982`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5165`

### Prompt

实现以下量子计算任务（使用isQ）：applies a controlled-Hadamard gate. Set the control qubit to |1>, then apply controlled-H to the target. Measure all 3 qubits.

Requirements:
- Declare `qbit q[3];` at global scope.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a controlled-Hadamard gate with q[0] as control and q[1] as target, setting up the control to activate the gate.
2. **Qubits**: 3 qubits declared (`q[3]`), all measured at the end.
3. **State evolution**:
   - Initialize: |000⟩
   - X(q[0]) flips control: |100⟩
   - ctrl H(q[0], q[1]) applies H to q[1] since q[0]=|1⟩: (|100⟩ + |110⟩)/√2
   - q[2] stays |0⟩ throughout (not operated on)
4. **Probabilities**: Each branch has amplitude 1/√2, giving 50% each for |100⟩ and |110⟩, matching the predicted output.

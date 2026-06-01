# ISQ training COT RAG corpus: quantum_algorithms shard 33

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1187

- task_id: `isqTrain/1187`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `33`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the phase_estimation pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this phase estimation circuit step by step.

The circuit implements phase estimation for the T gate. The T gate has eigenstate |1⟩ with eigenvalue e^(iπ/4), so the phase is π/4 = 1/8.

1. Goal: Estimate the phase of T gate's eigenstate |1⟩ using 3 ancilla qubits.

2. Qubits: 4 total (anc[3] for readout, target[1] for eigenstate). Measuring anc[0], anc[1], anc[2].

3. State evolution:
- Initial: |000⟩|1⟩
- After X(target): |000⟩|1⟩
- After H on all ancilla: (1/√8)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)|1⟩

Now controlled operations:
- anc[0] controls T: |1⟩ gets phase e^(iπ/4) when anc[0]=1
- anc[1] controls S = T²: |1⟩ gets phase e^(iπ/2) when anc[1]=1
- anc[2] controls Z = T⁴: |1⟩ gets phase e^(iπ) when anc[2]=1

So each ancilla qubit |k⟩ contributes phase e^(iπ·2^k/8) = e^(iπ·2^k/8).

Wait, let me recalculate:
- anc[0] (2^0 position): applies T, phase = π/4 per application = π·2^0/8
- anc[1] (2^1 position): applies T² = S, phase = 2π/4 = π/2 per application = π·2^1/8
- anc[2] (2^2 position): applies T⁴ = Z, phase = 4π/4 = π per application = π·2^2/8

So the state after controlled operations:
|ψ⟩ = (1/√8) Σ_{k=0}^{7} e^(i·θ_k)|k⟩|1⟩

where θ_k encodes the phase φ = π/4 = 1/8.

Actually, let me think about this more carefully. If the phase is φ = π/4, then:
- For anc[0] = bit 0 of ancilla register (LSB), we apply U^1 = T
- For anc[1] = bit 1, we apply U^2 = T² = S
- For anc[2] = bit 2, we apply U^4 = T⁴ = Z

Each ancilla qubit j in state |1⟩ adds phase 2^j · φ = 2^j · π/4.

So the state is:
|ψ⟩ = (1/√8)(|0⟩ + e^(iπ/4)|1⟩)(|0⟩ + e^(iπ/2)|1⟩)(|0⟩ + e^(iπ)|1⟩)|1⟩

= (1/√8)(|0⟩ + e^(iπ/4)|1⟩) ⊗ (|0⟩ + i|1⟩) ⊗ (|0⟩ - |1⟩)|1⟩

Now applying inverse QFT:

The QFT maps |k⟩ → (1/√N) Σ_j e^(2πijk/N)|j⟩
Inverse QFT maps (1/√N) Σ_j e^(2πiφj)|j⟩ → |⌊N·φ⌋⟩

Here N = 8, and the phase φ = 1/8 encoded in the ancilla register.

Wait, I need to be more careful. The phase estimation gives us φ/(2π) in binary.

The T gate has eigenvalue e^(i2πφ) where φ = 1/8 (since T|1⟩ = e^(iπ/4)|1⟩ and π/4 = 2π·1/8).

So φ = 1/8 = 0.001 in binary.

The inverse QFT on the state (1/√8) Σ_k e^(2πiφk)|k⟩ gives |2³·φ⟩ = |1⟩.

Wait, that would give |001⟩, not |100⟩.

Hmm, let me reconsider the qubit ordering. In the implementation, they measure anc[0], anc[1], anc[2] in that order. The --probs output says earlier measured qubit = higher bit.

So measuring M(anc[0]), M(anc[1]), M(anc[2]):
- anc[0] is the highest bit
- anc[2] is

## isqTrain/1359

- task_id: `isqTrain/1359`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `3599`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

oracle bool[1] xor_oracle(bool x[2]) {
    bool res[] = [x[0] != x[1]];
    return res;
}

qbit q[3];
qbit anc[1];

procedure main() {
    X(q[0]);
    xor_oracle(q, anc);
    M(q[0]); M(q[1]); M(q[2]); M(anc[0]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step analysis of an isQ quantum program, explaining the quantum state evolution and predicting the final probability distribution. The output must follow specific formatting constraints.

2.  **Analyze the isQ Program**:
    *   *Initial state*: 4 qubits `q[3]` and `anc[1]`. State is `|0000>` (assuming order `q[0], q[1], q[2], anc[0]`).
    *   *Gate 1*: `X(q[0])`. Flips `q[0]` to 1. State becomes `|1000>`.
    *   *Oracle*: `xor_oracle(q, anc)`. The oracle computes `x[0] != x[1]`.
        *   `q` has 3 qubits, but the oracle input `x[2]` only takes the first two qubits `q[0]` and `q[1]`.
        *   `anc` is the output qubit.
        *   Since `q[0]` is 1 and `q[1]` is 0, `1 != 0` is true (1).
        *   The oracle effectively performs an X gate on `anc[0]` because the result is 1.
        *   Wait, is it a standard phase oracle or a bit-flip oracle? The syntax `oracle bool[1] xor_oracle(bool x[2])` computing into `anc` means it applies X to the target if the boolean condition is true. Actually, typically it's implemented as a CNOT or Toffoli. Here, `x[0] != x[1]` for `|10>` evaluates to `1`, so `anc` is flipped by X.
        *   Let's trace carefully: State before oracle is `|1>_q0 |0>_q1 |0>_q2 |0>_anc`. The oracle evaluates `q[0] != q[1]` -> `1 != 0` -> `1`. Thus it flips `anc[0]`. State becomes `|1001>`.
    *   *Measurements*: `M(q[0]); M(q[1]); M(q[2]); M(anc[0]);` measures all qubits.
    *   *Bitstring mapping*: In isQ `--probs` mode, the bitstring index corresponds to the order of measurement. The earliest measured qubit is the highest bit. So `q[0]` is the most significant bit (bit 3), `q[1]` is bit 2, `q[2]` is bit 1, `anc[0]` is bit 0.
    *   `|q[0]=1, q[1]=0, q[2]=0, anc[0]=1>` = `|1001>` in binary = 9 in decimal.
    *   Probability of `|1001>` is 1.0.

3.  **Draft the Circuit Analysis**:
    *   *Initial state*: `|0000>` (for q[0], q[1], q[2], anc[0]).
    *   *Step 1*: `X(q[0])` applies an X gate to `q[0]`. State becomes `|1000>`.
    *   *Step 2*: `xor_oracle(q, anc)` evaluates the boolean condition `q[0] != q[1]`. Since `q[0]` is 1 and `q[1]` is 0, the condition is true. Thus, it flips `anc[0]` from 0 to 1. The state becomes `|1001>`.
    *   *Step 3*: Measurement of `q[0]`, `q[1]`, `q[2]`, `anc[0]` collapses the state. The bitstring is constructed with the earliest measured qubits as higher bits.
    *   *Result*: `|1001>` with probability 1.0.

4.  **Refine to meet constraints**:
    *   Concise: 3-8 lines for simple circuits.
    *   Format: Starts with "## Circuit Analysis".
    *   Ends with the predicted probability distribution: `Predicted probability distribution: {|1001>: 1.0}`.
    *   No code blocks.

5.  **Double check**: Is there any Hadamard? No. Any superposition? No. The circuit is entirely classical.
    Initial: `|0000>`
    X(q[0]) -> `|1000>`
    xor_oracle(q, anc) -> Since `q[0]`=1 and `q[1]`=0, `q[0]!=q

### Reference answer

{'predicted_probs': {'9': 1.0}, 'explanation': 'Parametric variant of isqEval/500. Dimension: qubit_variant: q[2] -> q[3].'}

## isqTrain/2036

- task_id: `isqTrain/2036`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `hamiltonian_simulation`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5618`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    Rz(1.57079632679490, q[0]);
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program**:
    *   Initialize a 1-qubit register `q[1]`. Initial state: $|0\rangle$.
    *   Apply `H(q[0])`: State becomes $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   Apply `Rz(1.57079632679490, q[0])`: The angle is $\pi/2$ ($90^\circ$). $R_z(\pi/2) = \begin{pmatrix} e^{-i\pi/4} & 0 \\ 0 & e^{i\pi/4} \end{pmatrix}$. State becomes $\frac{1}{\sqrt{2}}(e^{-i\pi/4}|0\rangle + e^{i\pi/4}|1\rangle)$. We can factor out $e^{-i\pi/4}$ to get $e^{-i\pi/4} \frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)$. Up to global phase, this is $|i+\rangle$ or related to $S|+\rangle$.
    *   Apply `H(q[0])`:
        $H (|0\rangle + i|1\rangle)/\sqrt{2} = (H|0\rangle + i H|1\rangle)/\sqrt{2} = (|+\rangle + i|-\rangle)/\sqrt{2}$.
        Recall $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$.
        $|+\rangle + i|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) + \frac{i}{\sqrt{2}}(|0\rangle-|1\rangle) = \frac{1+i}{\sqrt{2}}|0\rangle + \frac{1-i}{\sqrt{2}}|1\rangle$.
    *   Measurement:
        Probability of $|0\rangle$ is $| \frac{1+i}{\sqrt{2}} |^2 / (\text{norm}) = |\frac{1+i}{\sqrt{2}}|^2 \times \frac{1}{2} = 1 \times 0.5 = 0.5$.
        Probability of $|1\rangle$ is $| \frac{1-i}{\sqrt{2}} |^2 / (\text{norm}) = |\frac{1-i}{\sqrt{2}}|^2 \times \frac{1}{2} = 1 \times 0.5 = 0.5$.

2.  **Wait, let me double check the $HR_z(\pi/2)H$ sequence**:
    *   $H R_z(\theta) H = R_x(\theta)$.
    *   So $H R_z(\pi/2) H = R_x(\pi/2)$.
    *   $R_x(\pi/2)$ applied to $|0\rangle$ gives $\frac{1}{\sqrt{2}}|0\rangle - \frac{i}{\sqrt{2}}|1\rangle$.
    *   Probabilities are $|\pm \frac{1}{\sqrt{2}}|^2 = 0.5$ for both.
    *   Yes, probabilities are 0.5 and 0.5.

3.  **Draft the step-by-step reasoning**:
    *   Initial state: $|0\rangle$.
    *   Apply $H$: State becomes $|+\rangle = \frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$.
    *   Apply $R_z(\pi/2)$: Rotates phase around Z-axis by $\pi/2$. State becomes $\frac{1}{\sqrt{2}}|0\rangle + \frac{i}{\sqrt{2}}|1\rangle$ (ignoring global phase).
    *   Apply $H$: Transforms basis back to Z. $H(\frac{1}{\sqrt{2}}|0\rangle + \frac{i}{\sqrt{2}}|1\rangle) = \frac{1}{2}(1+i)|0\rangle + \frac{1}{2}(1-i)|1\rangle$.
    *   Measurement: Prob($|0\rangle$) = $|1/2(1+i)|^2 = 0.5$, Prob($|1\rangle$) = $|1/2(1-i)|^2 = 0.5$.

4.

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Single-qubit Z evolution on |+>: P(|0>)=0.5, P(|1>)=0.5.'}

## isqTrain/1274

- task_id: `isqTrain/1274`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1668`

### Prompt

I need an isQ program to implements a variant of the simon_algorithm pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
The circuit implements Simon's algorithm with period s=100 on a 5-qubit input register (q[0]-q[4]), where q[3]-q[4] remain untouched in |0⟩ throughout the computation.

1. **Initial state**: |00000⟩ (5 qubits, all ground state)
2. **After H on q[0], q[1], q[2]**: (1/√8)Σ|x₀x₁x₂⟩|00⟩ for xᵢ ∈ {0,1}, placing first 3 qubits in equal superposition while q[3], q[4] stay |0⟩
3. **After oracle f**: |ψ⟩ = (1/√8)Σ|x⟩|f(x)⟩|00⟩ where f(x) = f(x⊕100), entangling input with output
4. **After H on q[0], q[1], q[2]**: The Hadamard transform restricts measurements to y satisfying y·s = 0 mod 2; since s=100, only states with q[2]=0 are measured
5. **Final state before measurement**: Equal superposition of |y₀y₁0⟩|00⟩ for y₀,y₁ ∈ {0,1}, yielding states |00000⟩, |01000⟩, |10000⟩, |11000⟩
6. **Expected probabilities**: Each of the 4 allowed states has probability 1/4 = 0.25, as the oracle's symmetry over x[2] forces q[2] to always measure as 0, while q[0] and q[1] are uniformly random

## isqTrain/3828

- task_id: `isqTrain/3828`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4409`

### Prompt

Write isQ code for the following quantum task: a 1D quantum walk on 8 positions using 3 step(s). Use q[0] as the coin qubit and q[1..3] as the position register. Each step: Hadamard coin flip followed by controlled shifts.

### Chain-of-thought reasoning

Looking at this quantum walk problem, let me trace through the state evolution carefully.

**Initial State:** |0⟩₀|000⟩₁₂₃ (coin in |0⟩, position at 0)

**Step 1:**
1. H(q[0]): |+⟩₀|000⟩₁₂₃
2. Controlled shifts (X on q[1], q[2], q[3] when q[0]=|1⟩):
   - When coin is |0⟩: position stays at 000
   - When coin is |1⟩: position becomes 111 (7)
   - State: (|0⟩|000⟩ + |1⟩|111⟩)/√2

**Step 2:**
1. H(q[0]): (|+⟩|000⟩ + |−⟩|111⟩)/√2 = (|0⟩|000⟩ + |1⟩|000⟩ + |0⟩|111⟩ − |1⟩|111⟩)/2

2. Controlled shifts:
   - |0⟩|000⟩ → |0⟩|000⟩ (no shift)
   - |1⟩|000⟩ → |1⟩|111⟩ (shift by 7)
   - |0⟩|111⟩ → |0⟩|111⟩ (no shift)
   - |1⟩|111⟩ → |1⟩|000⟩ (shift by 7 wraps to 0... wait, 7+7=14 mod 8 = 6, not 0)

Wait, I need to reconsider. The shift operation here is: if coin is |1⟩, apply X to all three position qubits. This means the position value p gets mapped to p XOR 7 (bitwise XOR with 111).

So:
- Position 0 (000) → 0 XOR 7 = 7 (111)
- Position 7 (111) → 7 XOR 7 = 0 (000)

So it's a swap between positions 0 and 7.

**After Step 1:**
State: (|0⟩₀|000⟩₁₂₃ + |1⟩₀|111⟩₁₂₃)/√2

**Step 2:**
1. H(q[0]): (|0⟩ + |1⟩)|000⟩/2 + (|0⟩ − |1⟩)|111⟩/2

2. Controlled shifts:
   - |0⟩|000⟩ → |0⟩|000⟩
   - |1⟩|000⟩ → |1⟩|111⟩
   - |0⟩|111⟩ → |0⟩|111⟩
   - |1⟩|111⟩ → |1⟩|000⟩
   
   State: (|0⟩|000⟩ + |1⟩|111⟩ + |0⟩|111⟩ − |1⟩|000⟩)/2
        = ((|0⟩ − |1⟩)|000⟩ + (|0⟩ + |1⟩)|111⟩)/2
        = (|−⟩|000⟩ + |+⟩|111⟩)/√2

**Step 3:**
1. H(q[0]): (|1⟩|000⟩ + |0⟩|111⟩ + |0⟩|111⟩ + |1⟩|000⟩)/(2)
   
   Wait let me redo this. H|−⟩ = |1⟩, H|+⟩ = |0⟩.
   
   H(q[0]) on (|−⟩|000⟩ + |+⟩|111⟩)/√2:
   = (H|−⟩|000⟩ + H|+⟩|111⟩)/√2
   = (|1⟩|000⟩ + |0⟩|111⟩)/√2

2. Controlled shifts:
   - |1⟩|000⟩ → |1⟩|111⟩
   - |0⟩|111⟩ → |0⟩|111⟩
   
   Final state: (|1⟩|111⟩ + |0⟩|111⟩)/√2 = |+⟩|111⟩

Hmm, but The predicted output {|0111⟩: 0.5, |1111⟩: 0.5}, which would be |+⟩|111⟩.

The predicted output format has coin as the highest bit. So |0111⟩ means q[0]=0, q[1..3]=111, and |1111⟩ means q[0]=1, q[1..3]=111.

So the final state is (|0⟩ + |1⟩)/√2 ⊗ |111⟩ = |+⟩|111⟩.

This gives probabilities 0.5 for |0111⟩ and 0.5 for |1111⟩. ✓

Let me re-verify Step 3 more carefully.

After Step 2, state = (|

## isqTrain/2991

- task_id: `isqTrain/2991`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4140`

### Prompt

Implement a quantum circuit in isQ: implements a SWAP gate using three CNOT gates. Initialize the qubits to |11>, apply the SWAP, and measure both qubits.

Requirements:
- Declare `qbit q[2];` at global scope.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a swap operation (three-CNOT decomposition) using three CNOT gates, starting from |11⟩ and measuring both qubits.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initialize |00⟩ → Apply X to both: |11⟩
   - CNOT(q[0], q[1]): control q[0]=|1⟩, flips q[1]: |11⟩ → |10⟩
   - CNOT(q[1], q[0]): control q[1]=|0⟩, no flip: |10⟩ → |10⟩
   - CNOT(q[0], q[1]): control q[0]=|1⟩, flips q[1]: |10⟩ → |11⟩
4. **Expected probabilities**: swap (three-CNOT decomposition)(|11⟩) = |11⟩, so measuring yields {|11⟩: 1.0}.

## isqExpand/algo/42

- task_id: `isqExpand/algo/42`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `grover`, `3qubit`, `multi_solution`, `optimal_iterations`
- source: `isq_expansion`
- dataset_index: `4648`

### Prompt

Write an isQ program that implements Grover's algorithm on 3 qubits with two marked solutions: |101> and |110>. Apply one Grover iteration. With M=2 solutions out of N=8 states, the Grover angle is theta=pi/6, so a single iteration should achieve perfect success probability.

### Chain-of-thought reasoning

## Reasoning
Goal: 3-qubit Grover with 2 solutions: |101> (index 5) and |110> (index 6).

Oracle marks both:
- Mark |101>: q[0]=1, q[1]=0, q[2]=1. X(q[1]); CCZ; X(q[1]);
- Mark |110>: q[0]=1, q[1]=1, q[2]=0. X(q[2]); CCZ; X(q[2]);

For N=8, M=2 solutions:
theta = arcsin(sqrt(M/N)) = arcsin(sqrt(2/8)) = arcsin(1/2) = pi/6
After 1 iteration: P_total = sin^2((2*1+1)*pi/6) = sin^2(pi/2) = 1.0

Each marked state gets P = 0.5, all unmarked states get P = 0.
Expected probs: indices 5 and 6 each = 0.5, all others = 0.0.

## isqTrain/3479

- task_id: `isqTrain/3479`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5780`

### Prompt

实现以下量子计算任务（使用isQ）：Prepare a 6-qubit GHZ state (|000000> + |111111>)/sqrt(2) in isQ.
H(q[0]) then CNOT to all others.
Declare 6 qubits, measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a 6-qubit GHZ state (|000000⟩ + |111111⟩)/√2 using Hadamard and CNOT gates.

Six qubits are declared, and all six are measured at the end.

Step-by-step state evolution:
- Initial: |000000⟩
- H(q[0]): (|000000⟩ + |100000⟩)/√2 — creates superposition on q[0]
- CNOT(q[0], q[1]): (|000000⟩ + |110000⟩)/√2 — copies control to target
- CNOT(q[0], q[2]): (|000000⟩ + |111000⟩)/√2
- CNOT(q[0], q[3]): (|000000⟩ + |111100⟩)/√2
- CNOT(q[0], q[4]): (|000000⟩ + |111110⟩)/√2
- CNOT(q[0], q[5]): (|000000⟩ + |111111⟩)/√2 — final GHZ state

Each CNOT flips the target when the control q[0] is |1⟩, so all qubits become correlated. Measurement yields |000000⟩ or |111111⟩, each with probability 0.5.

## isqTrain/3933

- task_id: `isqTrain/3933`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `4573`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// QPE with 2-bit precision for phase 3*pi/4
// Unitary: Rz(theta) with eigenvalue e^{i*theta/2} on |1>
qbit q[3];

procedure main() {
    // Prepare eigenstate |1> on target qubit
    X(q[2]);
    // Hadamard on precision qubits
    H(q[0]); H(q[1]);
    // Controlled unitary applications
    ctrl Rz(2.0 * 3.14159265358979 * 3.0 / 4.0 * 1.0, q[0], q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 3.0 / 4.0 * 2.0, q[1], q[2]);
    // Inverse QFT on precision register
    // For 2 qubits: SWAP, then H + controlled-Rz†
    // BUG: missing gate here
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    H(q[1]);
    // Measure precision qubits
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

Let me analyze this quantum phase estimation (QPE) circuit carefully.

The task is a 2-bit QPE for phase 3π/4.

**Understanding the unitary and phase:**
- Unitary: Rz(θ) with eigenvalue e^{iθ/2} on |1⟩
- θ = 2π × 3/4 = 3π/2
- Eigenvalue: e^{iθ/2} = e^{i3π/4}
- So the phase φ = 3/4 (in units of 2π)
- In 2-bit precision: φ = 0.11₂ = 3/4

**Controlled unitaries:**
- For q[0]: controlled Rz(2π × 3/4 × 1) = controlled Rz(3π/2)
- For q[1]: controlled Rz(2π × 3/4 × 2) = controlled Rz(3π)

**Inverse QFT on 2 qubits:**
The QFT on 2 qubits is:
1. H(q[0])
2. CRz(π/2, q[1], q[0]) [controlled phase]
3. H(q[1])
4. swap (three-CNOT decomposition)(q[0], q[1])

So the inverse QFT is:
1. swap (three-CNOT decomposition)(q[0], q[1])
2. H(q[1])
3. CRz(-π/2, q[1], q[0]) [inverse controlled phase]
4. H(q[0])

Wait, let me be more careful. The QFT matrix for 2 qubits acts as:
QFT|00⟩ = |++⟩
QFT|01⟩ = (|0⟩ + e^{iπ/2}|1⟩)/√2 ⊗ (|0⟩ + e^{iπ/4}|1⟩)/√2 ... actually let me think about this differently.

The standard 2-qubit QFT circuit is:
1. H on q[0] (most significant)
2. Controlled-S (Rz(π/2)) with q[1] controlling q[0]
3. H on q[1]
4. swap (three-CNOT decomposition) q[0] and q[1]

Wait, let me reconsider the bit ordering. In standard QPE:
- q[0] is the least significant bit (gets applied U^1)
- q[1] is the most significant bit (gets applied U^2)

After phase kickback:
- q[0] picks up phase φ (least significant)
- q[1] picks up phase 2φ (most significant)

The QFT takes a computational basis state |k⟩ to a uniform superposition with phases.

For the inverse QFT on 2 qubits where q[0] is LSB and q[1] is MSB:

Standard QFT (MSB first approach):
1. H(q[1])  // on MSB
2. CRz(π/2, q[0], q[1])  // controlled by LSB on MSB
3. H(q[0])  // on LSB
4. swap (three-CNOT decomposition)(q[0], q[1])

Actually, I think the convention might differ. Let me think about what the corrected code does.

The corrected code for inverse QFT:

So the corrected inverse QFT is:
1. swap (three-CNOT decomposition)(q[0], q[1])
2. H(q[0])
3. CRz(-π/2, q[1], q[0])
4. H(q[1])

The buggy code has:

So the bug is: the swap operation (three-CNOT decomposition) is incomplete. A swap (three-CNOT decomposition) requires 3 CNOTs, but only 2 are present.

The buggy code has CNOT(q[1],q[0]) then CNOT(q[0],q[1]), which is NOT a swap (three-CNOT decomposition). The fix is to add CNOT(q[0],q[1]) at the beginning (or end), making it a

## isqTrain/3475

- task_id: `isqTrain/3475`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `interference`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `2883`

### Prompt

Help me write isQ code that Bernstein-Vazirani for secret string s=010 in isQ.
Declare 3 qubits + 1 ancilla. Measure input only.
Expected: |010>.

### Chain-of-thought reasoning

## Reasoning
Goal: Find secret string s=010 using Bernstein-Vazirani with 3 input qubits + 1 ancilla; only inputs are measured.

State evolution: |000>|0> → X(anc) → |000>|1> → H(anc) → |000>|-> → H⊗3(q) → (1/√8)Σx|x>|->.
Oracle CNOT(q[1],anc[0]) encodes s=010 via phase kickback: (-1)^(x·s)|x>|-> (only bit 1 of s is 1).
Final H⊗3(q) decodes the phase oracle: H⊗3Σx(-1)^(x·s)|x> = |s> = |010>.
Measuring q[0..2] yields |010> with probability 1.0; ancilla remains unmeasured in |->.

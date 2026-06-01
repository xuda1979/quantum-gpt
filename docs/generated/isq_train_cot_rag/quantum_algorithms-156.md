# ISQ training COT RAG corpus: quantum_algorithms shard 156

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/904

- task_id: `isqTrain/904`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4221`

### Prompt

Create an isQ quantum circuit that implements the bit_flip_oracle pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a bit-flip oracle for f(x) = x[0] XOR x[1] using the CNOT decomposition H-CZ-H, with input x = |10⟩ and ancilla in |+⟩.

2. **Qubits**: 3 qubits (q[0], q[1] for input, q[2] for output); all measured.

3. **State evolution**:
   - Initialize |000⟩ → X(q[0]) → |100⟩
   - H(q[2]) → |10+⟩
   - CZ(q[0], q[2]): control q[0]=|1⟩ applies Z to |+⟩ → |−⟩, state → |10−⟩
   - H(q[2]): |−⟩ → |1⟩, state → |101⟩
   - H(q[2]): |1⟩ → |−⟩, state → |10−⟩
   - CZ(q[1], q[2]): control q[1]=|0⟩, no effect → |10−⟩
   - H(q[2]): |−⟩ → |1⟩, state → |101⟩

4. **Expected probabilities**: Final state |101⟩ gives measurement probability {|101⟩: 1.0}, confirming f(1,0) = 1 XOR 0 = 1 flips the ancilla from |+⟩ to |−⟩ → |1⟩.

## isqTrain/25

- task_id: `isqTrain/25`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3511`

### Prompt

实现以下量子计算任务（使用isQ）：implements the qft_subcircuit pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program that implements a QFT subcircuit pattern with explicit identity operations (H-H pair before measurement).

Let me trace through the circuit:

1. Initial state: |000⟩
2. X(q[2]) → |100⟩ (flips q[2], which is the third qubit)
3. QFT3(q[0], q[1], q[2]) applied:
   - H(a) where a=q[0]: This creates superposition on q[0]
   - ctrl Rz(pi/2.0, b, a) where b=q[1], a=q[0]: controlled rotation
   - ctrl Rz(pi/4.0, c, a) where c=q[2], a=q[0]: controlled rotation
   - H(b) where b=q[1]: Hadamard on q[1]
   - ctrl Rz(pi/2.0, c, b) where c=q[2], b=q[1]: controlled rotation
   - H(c) where c=q[2]: Hadamard on q[2]
   - swap (three-CNOT decomposition) a and c: CNOT(a,c), CNOT(c,a), CNOT(a,c)
4. H(q[0]) followed by H(q[0]) = Identity (H-H pair)
5. Measurements on all qubits

Let me trace more carefully:

Starting state: |000⟩ (q[0], q[1], q[2])

After X(q[2]): |100⟩

Now qft3(q[0], q[1], q[2]) with a=q[0], b=q[1], c=q[2]:
State is |100⟩ (qubit ordering: q[0]q[1]q[2])

Wait, I need to be careful about the ordering. In the ket |q[2]q[1]q[0]⟩ or |q[0]q[1]q[2]⟩?

Let me use the convention where |q[0]q[1]q[2]⟩ so q[0] is the leftmost bit.

X(q[2]) on |000⟩ → |001⟩ (flipping the third qubit)

Hmm, this is getting confusing. Let me think about it differently.

The initial state is |000⟩ where we index as q[0] = first position, q[1] = second, q[2] = third.

So |q[2], q[1], q[0]⟩ = |000⟩ means all qubits are in |0⟩.

X(q[2]) flips q[2]: Now the state is |100⟩ in the ordering |q[2], q[1], q[0]⟩.

Actually, for QFT the standard approach is:
QFT maps |j⟩ → (1/√N) Σ_k e^(2πijk/N) |k⟩

For a 3-qubit system starting from |4⟩ = |100⟩ (in binary, q[2]=1, q[1]=0, q[0]=0):

QFT(|100⟩) would give a specific superposition.

Let me trace through the QFT3 circuit more carefully.

Starting with |100⟩ (q[2]=1, q[1]=0, q[0]=0):

In qft3(a=q[0], b=q[1], c=q[2]):

1. H(a) = H(q[0]): This applies H to q[0]. Since q[0]=0, we get (|0⟩+|1⟩)/√2 on q[0].
   State: (|000⟩ + |001⟩)/√2 = (|0⟩+|1⟩)/√2 ⊗ |00⟩

Wait, I'm getting confused with the ordering. Let me stick to |q[2]q[1]q[0]⟩ notation.

Initial: |100⟩ means q[2]=1, q[1]=0, q[0]=0

After H(q[0]):
|100⟩ → |1⟩⊗|0⟩⊗(|0⟩+|1⟩)/√2 = (|100⟩+|101⟩)/√2

2. ctrl Rz(π/2, b=q[1], a=q[0]): This is a controlled-Rz with q[1] as control and q[0] as target. 
   Rz(θ) = [[1,0],[0,e^(iθ)]]
   This applies Rz(π/2) to q[0] when q[1]=1.
   
   Current state: (|100⟩+|101⟩)/√2
   For |100⟩: q[1]=0, so nothing happens
   For |101⟩:

## isqTrain/4421

- task_id: `isqTrain/4421`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `isq_syntax_for_loop`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4047`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[2];

procedure main() {
    // Prepare initial state |10>
    X(q[0]);

    // qDrift for H = XX + ZZ on |10>
    // t = pi/4, lambda = 2, N = 4
    // tau = t*lambda/N = pi/4, rotation = 2*tau = pi/2
    // Sample sequence: ZZ, XX, ZZ, XX

    // Sample 1: ZZ term
    CNOT(q[0], q[1]);
    // Rz(pi/2) for the ZZ interaction
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);

    // Sample 2: XX term (H-basis change)
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    // Rz(pi/2) for XX in the Hadamard basis
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);

    // Sample 3: ZZ term
    CNOT(q[0], q[1]);
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);

    // Sample 4: XX term
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);

    // Measure both qubits
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ quantum program implementing a specific sequence of gates on 2 qubits.
    *   Task: Predict the probability distribution of measurement outcomes and explain the reasoning.
    *   Output format: "## Circuit Analysis" followed by a step-by-step explanation, ending with the predicted probability distribution.
    *   Constraints: Concise, use Dirac notation, no code blocks.

2.  **Analyze the Circuit:**
    *   Qubits: `q[0]`, `q[1]` initialized to |00>.
    *   `X(q[0])`: State becomes |10>.
    *   *Sample 1: ZZ term*
        *   `CNOT(q[0], q[1])`: |10> -> |11>.
        *   `Rz(pi/2, q[1])`: On |11>, `Rz(pi/2)` adds phase $e^{-i\pi/4}$ to $|1\rangle$ of $q_1$. Since both are 1, phase is $e^{-i\pi/4}$. Let's track state: $e^{-i\pi/4}|11\rangle$. Actually, $Rz(\theta) = e^{-i\theta/2}|0\rangle\langle 0| + e^{i\theta/2}|1\rangle\langle 1|$. So $Rz(\pi/2)$ applies $e^{i\pi/4}$ to $|1\rangle$ and $e^{-i\pi/4}$ to $|0\rangle$. State is $e^{i\pi/4}|11\rangle$.
        *   `CNOT(q[0], q[1])`: $q_1$ is flipped back if $q_0=1$. Since state is $e^{i\pi/4}|11\rangle$, it goes to $e^{i\pi/4}|10\rangle$.
    *   *Sample 2: XX term*
        *   `H(q[0]); H(q[1])`: Applied to $e^{i\pi/4}|10\rangle$. $q_0 \to |+\rangle$, $q_1 \to |-\rangle$. State: $e^{i\pi/4}|+\rangle|-\rangle$.
        *   `CNOT(q[0], q[1])`: CNOT on $|+\rangle|-\rangle$.
            $|+\rangle|-\rangle = \frac{1}{2}(|0\rangle+|1\rangle)(|0\rangle-|1\rangle) = \frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$.
            CNOT flips the second: $\frac{1}{2}(|01\rangle - |00\rangle + |11\rangle - |10\rangle) = - \frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle) = -|+\rangle|-\rangle$.
            So state becomes $-e^{i\pi/4}|+\rangle|-\rangle$.
        *   `Rz(pi/2, q[1])`: Applied to $|-\rangle$. $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
            $Rz(\pi/2)(|0\rangle - |1\rangle) = e^{-i\pi/4}|0\rangle - e^{i\pi/4}|1\rangle = e^{-i\pi/4}(|0\rangle - e^{i\pi/2}|1\rangle) = e^{-i\pi/4}(|0\rangle - i|1\rangle) = e^{-i\pi/4} e^{-i\pi/4} |1\rangle$? Wait.
            Let's use exact math. $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = \frac{1}{\sqrt{2}}\begin{pmatrix}1\\-1\end{pmatrix}$.
            $Rz(\pi/2) = \begin{pmatrix}e^{-i\pi/4} & 0 \\ 0 & e^{i\pi/4}\end{pmatrix}$.
            $Rz(\pi/2) |-\rangle = \frac{1}{\sqrt{2}} \begin{pmatrix}e^{-i\pi/4} \\ -e^{i\pi/4}\end{pmatrix} = \frac{e^{-i\pi/4}}

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|11>) = 1.0000.'}

## isqTrain/3924

- task_id: `isqTrain/3924`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3656`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// Grover search on 3 qubits targeting |011>, 2 iterations
qbit q[3];

// Oracle: mark target state |011>
unit grover_oracle(qbit q[3]) {
    X(q[0]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
} deriving gate

// Diffusion operator
unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    // BUG: missing gate here
    H(q[1]);
    H(q[2]);
} deriving gate

// Main: 2 Grover iterations for higher success probability
procedure main() {
    // Initialize superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Iteration 1
    grover_oracle(q);
    grover_diffusion(q);
    // Iteration 2
    grover_oracle(q);
    grover_diffusion(q);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug:** The `grover_diffusion` unit is missing `H(q[0])` after the X-CZ-X sequence. Only `H(q[1])` and `H(q[2])` are applied to restore the Hadamard basis, leaving `q[0]` in the X-basis and breaking the diffusion operator.

2. **Fix:** Add `H(q[0])` immediately after the `X(q[0]); X(q[1]); X(q[2]);` block (before the existing `H(q[1]); H(q[2]);`), completing the required `H^⊗3` that wraps the conditional phase flip in the diffusion operator.

3. **State evolution (corrected):** Initial `|000⟩` → `H^⊗3` → uniform `|+⟩^⊗3`. Each Grover iteration: oracle flips the phase of `|011⟩`, then diffusion reflects about the mean. After 2 iterations, amplitude of `|011⟩` ≈ 0.972, all others ≈ −0.088, yielding `P(|011⟩) ≈ 0.9453`.

## isqTrain/2863

- task_id: `isqTrain/2863`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2905`

### Prompt

Help me write isQ code that implements a approximate W state preparation. Apply the appropriate gates to 3 qubits and measure all of them.

Requirements:
- Declare `qbit q[3];` at global scope.
- Use `procedure main()` as entry point.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare an approximate W-state superposition on 3 qubits where measurement yields roughly equal probability across specific basis states.
2. **Qubits**: 3 qubits `q[0]`, `q[1]`, `q[2]`, all measured at the end.
3. **State evolution**:
   - Start: |000⟩
   - X(q[0]): |100⟩
   - H(q[0]): (|000⟩ + |100⟩)/√2
   - CNOT(q[0], q[1]): (|000⟩ + |110⟩)/√2
   - H(q[0]): (|000⟩ + |100⟩ + |010⟩ - |110⟩)/2
   - CNOT(q[0], q[2]): (|000⟩ + |101⟩ + |010⟩ - |111⟩)/2
   - CNOT(q[2], q[1]): (|000⟩ + |111⟩ + |010⟩ - |101⟩)/2
4. **Probabilities**: Each basis state has amplitude ±1/2, so |amplitude|² = 1/4 = 0.25 for |000⟩, |010⟩, |101⟩, |111⟩.

## isqTrain/4454

- task_id: `isqTrain/4454`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1593`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;

qbit q[3];
qbit a[1];

procedure my_oracle() {
    CNOT(q[0], a[0]);
    CNOT(q[1], a[0]);
}

procedure main() {
    // Prepare ancilla in |-> state
    X(a[0]); H(a[0]);
    // Apply Hadamard to query qubits
    H(q[0]); H(q[1]); H(q[2]);
    // Apply oracle
    my_oracle();
    // Second Hadamard layer
    H(q[0]); H(q[1]); H(q[2]);
    // Measure query qubits
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the request:**
    *   Task: Predict the probability distribution of measurement outcomes for the given isQ program.
    *   Format: Step-by-step reasoning using Dirac notation.
    *   Length constraints: 3-8 lines for simple, up to 15 for complex.
    *   Target Output format: "## Circuit Analysis" followed by the reasoning and ending with the predicted probability distribution.
    *   no code blocks.

2.  **Analyze the isQ program:**
    *   Qubits: `q[0], q[1], q[2]` (query), `a[0]` (ancilla).
    *   Initial state: $|0000\rangle$ (order: $q_0 q_1 q_2 a_0$). Let's use $q_2 q_1 q_0$ as query bits.
    *   Ancilla preparation: `X(a[0]); H(a[0]);` -> Puts ancilla in $|-\rangle$ state. State: $|000\rangle_q \otimes |-\rangle_a$.
    *   Query preparation: `H(q[0]); H(q[1]); H(q[2]);` -> Puts query in $|+++\rangle$. State: $|+++\rangle_q \otimes |-\rangle_a$.
    *   Oracle: `CNOT(q[0], a[0]); CNOT(q[1], a[0]);`. This calculates $f(x) = q_0 \oplus q_1$ into the ancilla. Because ancilla is in $|-\rangle$, this applies a phase kickback: $(-1)^{f(x)}|x\rangle|-\rangle$. The function $f(x) = 1$ if $q_0 \neq q_1$, else 0.
        *   So $|00\rangle \to |00\rangle$, $|01\rangle \to -|01\rangle$, $|10\rangle \to -|10\rangle$, $|11\rangle \to |11\rangle$.
        *   State after oracle: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)_{q_0,q_1} \to \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)_{q_0,q_1} = |--\rangle_{q_0,q_1}$.
        *   Wait, let's check: $H^{\otimes 2} |00\rangle \to |++\rangle$.
        *   Oracle applies $Z$ on $q_0 \oplus q_1$. Actually, phase oracle for XOR.
        *   $|--\rangle = \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$. Yes.
        *   $q_2$ is untouched: $|+\rangle_{q_2}$.
        *   Total state: $|--+\rangle_q \otimes |-\rangle_a$.
    *   Second Hadamard layer: `H(q[0]); H(q[1]); H(q[2]);`
        *   $H|-\rangle = |1\rangle$.
        *   $H|+\rangle = |0\rangle$.
        *   So query state becomes $|110\rangle_q$.
    *   Pre-measurement gate: `X(q[0]);` -> Flips $q_0$. State becomes $|100\rangle_q$. Wait, let me check bit ordering.
        *   Standard bitstring order is $q_2 q_1 q_0$. Measurement is `M(q[0]); M(q[1]); M(q[2]);`
        *   In isQ, `M` returns 0 or 1. "earlier measured qubit = higher bit" in the output probability map.
        *   So if `M(q[0])` is first, its outcome is the highest bit of the index. So the bitstring is $q_0 q_1 q_2$.
        *   Let's re-verify the state.
        *   $q_0 = 1$, $q_1 = 1$, $q_2 = 0$.
        *   Apply X to $q_0$ -> $q_0$ becomes 0.
        *   So the state just before measurement is $q_0=0, q_1=1, q_2=0$.
        *   Bitstring $q_0 q_1 q_2$ is 010.
        *   Therefore, outcome is

### Reference answer

{'predicted_probs': {'010': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|010>) = 1.0000.'}

## isqTrain/2724

- task_id: `isqTrain/2724`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4470`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];

procedure main(){
    H(q[0]);
    ctrl X(q[0],q[1]);

    int a = M(q[0]);
    int b = M(q[1]);
    print a - b;
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |00>.
2. Apply H gate to q[0]: the state becomes (|00> + |10>) / √2.
3. Apply CNOT (ctrl X) with q[0] as control and q[1] as target: the state becomes (|00> + |11>) / √2.
4. The system is now in a maximally entangled Bell state.
5. Measuring this state yields |00> with probability 0.5 and |11> with probability 0.5.

Predicted probability distribution: {'00': 0.5, '11': 0.5}

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3050

- task_id: `isqTrain/3050`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `2514`

### Prompt

Create an isQ quantum circuit that initializes 3 qubits to the state |001> using X gates and measures all.

Requirements:
- Declare `qbit q[3];` at global scope.
- Apply X to qubits that should be |1>.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Initialize a 3-qubit register to the computational basis state |001⟩ and measure all qubits.
Three qubits q[0], q[1], q[2] are used, all measured at the end.
Step-by-step evolution:
- Initial state: |000⟩
- Apply X(q[2]): flips q[2] from |0⟩ to |1⟩ → |001⟩
Final state is |001⟩ with certainty, so measurement yields outcome 001 with probability 1.0.

## isqTrain/4118

- task_id: `isqTrain/4118`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `626`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[2]);

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |000⟩

After X(q[0]) and X(q[2]):
State becomes |101⟩

Now the three CNOT gates: CNOT(q[0], q[2]), CNOT(q[2], q[0]), CNOT(q[0], q[2])

Starting with |101⟩:
- CNOT(q[0], q[2]): control=q[0]=1, so flip q[2]. q[2] was 1, becomes 0. State: |100⟩
- CNOT(q[2], q[0]): control=q[2]=0, no flip. State: |100⟩
- CNOT(q[0], q[2]): control=q[0]=1, so flip q[2]. q[2] was 0, becomes 1. State: |101⟩

So the three CNOTs bring us back to |101⟩. Actually, let me think about what these three CNOTs do as a unit. This is a swap operation (three-CNOT decomposition) decomposition! The three CNOTs in this order swap q[0] and q[2].

Wait, standard swap (three-CNOT decomposition) is CNOT(a,b), CNOT(b,a), CNOT(a,b). Here:
- CNOT(q[0], q[2]): target=q[2]
- CNOT(q[2], q[0]): target=q[0]
- CNOT(q[0], q[2]): target=q[2]

Starting from |101⟩:
After CNOT(q[0],q[2]): |100⟩
After CNOT(q[2],q[0]): q[2]=0, so no flip: |100⟩
After CNOT(q[0],q[2]): q[0]=1, flip q[2]: |101⟩

Hmm wait, that didn't swap. Let me reconsider. With |101⟩, q[0]=1, q[1]=0, q[2]=1.

The swap (three-CNOT decomposition) of q[0] and q[2] would give |101⟩ again since both are 1. So the state is still |101⟩.

Now H(q[2]):
H on q[2]: |1⟩ → |−⟩ = (|0⟩ − |1⟩)/√2
State: |10⟩⊗|−⟩ = (|100⟩ − |101⟩)/√2

ctrl Rz(-2π/4, q[2], q[1]) = ctrl Rz(-π/2, q[2], q[1]):
This is a controlled-Rz(-π/2) with q[2] as control and q[1] as target.

Rz(θ)|0⟩ = e^{-iθ/2}|0⟩
Rz(θ)|1⟩ = e^{iθ/2}|1⟩

Wait, let me be careful about the definition. Rz(θ) = [[1,0],[0,e^{iθ}]] typically, or it could be Rz(θ) = e^{-iθZ/2}.

In isQ, Rz(θ, q) is typically [[1,0],[0,e^{iθ}]].

So Rz(-π/2)|0⟩ = |0⟩ and Rz(-π/2)|1⟩ = e^{-iπ/2}|1⟩ = -i|1⟩.

The controlled-Rz(-π/2, q[2], q[1]): when q[2] is |1⟩, apply Rz(-π/2) to q[1].

State = (|100⟩ − |101⟩)/√2

When q[2]=|0⟩ (first term): no action on q[1]. Still |100⟩.
When q[2]=|1⟩ (second term): apply Rz(-π/2) to q[1]. q[1]=|0⟩, so Rz(-π/2)|0⟩ = |0⟩. Still |101⟩.

Hmm, so the state doesn't change since q[1]=|0⟩ in both cases.

Wait, actually Rz(-π/2)|0⟩ = |0⟩ since the top-left element is 1. So yes, no change.

State: (|100⟩ − |101⟩)/√2

H(q[1]):
H on q[1]:
|100⟩ → |1⟩|0⟩|0⟩ → |1⟩(|0⟩+|1⟩)/√2 |0⟩ = (|100⟩ + |110⟩)/√2
|101⟩ → |1⟩|0⟩|1⟩ → |1⟩(|0⟩+|1⟩)/√2 |1⟩ = (|101⟩ + |111⟩)/√2

State: [(|100⟩ +

### Reference answer

Uniform distribution across 8 states

## isqTrain/725

- task_id: `isqTrain/725`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1603`

### Prompt

Write isQ code for the following quantum task: implements a variant of the ripple_carry_adder pattern using q[6] -> q[7]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants to analyze a ripple carry adder circuit in isQ.
The circuit adds a=3 (binary 11) and b=1 (binary 01).
Wait, the code has `qbit q[7];`.
Initial states:
a0 = q[0] = |1> (via X)
a1 = q[1] = |1> (via X)
b0 = q[2] = |1> (via X)
b1 = q[3] = |0> (default)
carry0 = q[4] = |0> (default)
carry1 = q[5] = |0> (default)
q[6] = |0> (Wait, the code measures q[6] but never operates on it. Wait, there's a typo in the provided reference code or it's just measuring an unused qubit, making it 0).

Let's trace the state:
Initial: |0000000>
X(q[0]), X(q[1]), X(q[2]) -> |1101000> (q[0]=1, q[1]=1, q[2]=1, others 0)
Wait, let's look at the bit string:
q[0] = 1
q[1] = 1
q[2] = 1
q[3] = 0
q[4] = 0
q[5] = 0
q[6] = 0
State is |1 1 1 0 0 0 0> (q0 q1 q2 q3 q4 q5 q6)

Toffoli(q[0], q[2], q[4]): q[0]=1, q[2]=1 -> q[4] becomes 1.
State: |1 1 1 0 1 0 0>
CNOT(q[0], q[2]): q[0]=1 -> q[2] becomes 0.
State: |1 1 0 0 1 0 0>
Toffoli(q[1], q[3], q[5]): q[1]=1, q[3]=0 -> q[5] remains 0.
State: |1 1 0 0 1 0 0>
Toffoli(q[1], q[4], q[5]): q[1]=1, q[4]=1 -> q[5] becomes 1.
State: |1 1 0 0 1 1 0>
Toffoli(q[3], q[4], q[5]): q[3]=0, q[4]=1 -> q[5] remains 1.
State: |1 1 0 0 1 1 0>
CNOT(q[1], q[3]): q[1]=1 -> q[3] becomes 1.
State: |1 1 0 1 1 1 0>
CNOT(q[4], q[3]): q[4]=1 -> q[3] becomes 0.
State: |1 1 0 0 1 1 0>

Measurements:
M(q[2]) -> 0
M(q[3]) -> 0
M(q[5]) -> 1
M(q[6]) -> 0

The predicted measurement probability is {|0010>: 1.0}.
The measurement order is q[2], q[3], q[5], q[6].
Values:
q[2] = 0
q[3] = 0
q[5] = 1
q[6] = 0

In the bitstring, earlier measured qubit = higher bit.
So bitstring is:
q[2] is highest bit (bit 3)
q[3] is bit 2
q[5] is bit 1
q[6] is bit 0

Bitstring = (q2)(q3)(q5)(q6) = 0010.
Which matches the Expected measurement probabilities: {|0010>: 1.0}.

Reasoning structure:
1. Goal: Implement a ripple-carry adder to compute 3+1 using 7 qubits.
2. Qubits: 7 qubits (q[0..6]). Measured: q[2], q[3], q[5], q[6].
3. Step-by-step:
   - Initial state |0000000>. X gates on q[0], q[1], q[2] encode inputs a=3 (binary 11) and b=1 (binary 01). State becomes |1110000>.
   - Toffoli(q[0], q[2], q[4]) computes carry0 = 1 & 1 =

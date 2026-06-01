# ISQ training COT RAG corpus: quantum_algorithms shard 102

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2902

- task_id: `isqTrain/2902`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3208`

### Prompt

Write an isQ program that implementing the Deutsch-Jozsa algorithm for a constant oracle on 3 input qubits. The oracle always returns true.

Requirements:
- Use 3 input qubits and 1 ancilla.
- Declare qubits at global scope.
- Use `procedure main()` as entry point.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement Deutsch-Jozsa algorithm with a constant oracle (always true) on 3 input qubits to demonstrate that constant functions yield |000⟩ on input qubits.

**Qubits:** 4 total — q[0], q[1], q[2] (input) and anc[0] (ancilla); all measured.

**State evolution:**
1. Initial: |0000⟩ → X(anc[0]) → |0001⟩ → H(anc[0]) → |000⟩(|0⟩-|1⟩)/√2
2. H on all inputs: (1/2√2)Σ|x⟩(|0⟩-|1⟩)/√2 (uniform superposition over 8 basis states)
3. Constant oracle f_const always returns true → flips ancilla phase: -(1/2√2)Σ|x⟩(|0⟩-|1⟩)/√2
4. H on all inputs again: H⊗3 transforms uniform superposition back to -|000⟩(|0⟩-|1⟩)/√2

**Expected probabilities:** Input qubits collapse to |000⟩ with certainty (constant function signature), while ancilla remains in (|0⟩-|1⟩)/√2 giving {|0000⟩: 0.5, |0001⟩: 0.5}.

## isqTrain/4191

- task_id: `isqTrain/4191`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3351`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 1.000, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    Rz(2.0 * 1.000, q[2]);
    CNOT(q[0], q[2]);
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, precise step-by-step reasoning of an isQ quantum circuit, written as a quantum computing expert. The response must be in a specific format, ending with the probability distribution, and avoid certain elements like code blocks.

2.  **Analyze the Circuit:**
    *   `qbit q[3];`
    *   Initial state: $|000\rangle$
    *   `H(q[0]); H(q[1]); H(q[2]);` -> State becomes $|+++\rangle = \frac{1}{2\sqrt{2}} \sum_{x \in \{0,1\}^3} |x\rangle$.
    *   `CNOT(q[0], q[1]); Rz(2.0, q[1]); CNOT(q[0], q[1]);` -> This is a controlled-$R_z(2.0)$ gate. The angle is 2.0 (radians).
    *   `CNOT(q[0], q[2]); Rz(2.0, q[2]); CNOT(q[0], q[2]);` -> This is a controlled-$R_z(2.0)$ gate on `q[2]`.
    *   Let's analyze the combined phase kickback.
    *   For a basis state $|q_0 q_1 q_2\rangle$, the $CR_z(2.0)$ gates apply a phase of $e^{-i \cdot 2.0 / 2} = e^{-i}$ if the target is 1, and $e^{i \cdot 2.0 / 2} = e^{i}$ if the target is 0? Wait, $R_z(\theta) = e^{-i\theta/2}|0\rangle\langle0| + e^{i\theta/2}|1\rangle\langle1|$.
    *   Actually, $CNOT \cdot R_z(\theta) \cdot CNOT$ applies $R_z(-\theta)$ to the control qubit $q_0$ if the target ($q_1$ or $q_2$) is in the $|-\rangle$ state (which it isn't here directly, but let's look at the full state).
    *   Wait, standard phase kickback: $CNOT_{c,t} R_z(\theta)_t CNOT_{c,t} = |0\rangle\langle0|_c \otimes R_z(\theta)_t + |1\rangle\langle1|_c \otimes R_z(-\theta)_t$.
    *   So if control is 0, target gets $R_z(\theta)$. If control is 1, target gets $R_z(-\theta)$.
    *   So $q_0=0$: $q_1$ gets $R_z(2)$, $q_2$ gets $R_z(2)$.
    *   $q_0=1$: $q_1$ gets $R_z(-2)$, $q_2$ gets $R_z(-2)$.
    *   State after $H^{\otimes 3}$ is $\frac{1}{2\sqrt{2}} \sum |q_0 q_1 q_2\rangle$.
    *   Let's rewrite the state as $\frac{1}{\sqrt{2}}(|0\rangle_{q_0} + |1\rangle_{q_0}) \otimes |+\rangle_{q_1} |+\rangle_{q_2}$.
    *   Apply $CNOT \cdot R_z(2) \cdot CNOT$ to $q_0, q_1$:
        *   If $q_0=0$, $|+\rangle_{q_1} \to R_z(2)|+\rangle_{q_1} = \frac{1}{\sqrt{2}}(e^{-i}|0\rangle + e^{i}|1\rangle) = e^{-i} \frac{1}{\sqrt{2}}(|0\rangle + e^{i2}|1\rangle) = e^{-i} R_x(-2) |+\rangle$. No wait, $R_z(\theta)|+\rangle = \cos(\theta/2)|+\rangle + i\sin(\theta/2)|-\rangle$.
        *   Actually, it's easier to work with $R_z(\theta)|+\rangle = e^{-i\theta/2}|0\rangle + e^{i\theta/2}|1\rangle$. This is NOT an eigenstate of X.
    *   Let's look at the next gates: `Rx(2.0 * 0.500, q[0]); Rx(2.

### Reference answer

Uniform distribution across 8 states

## isqTrain/2964

- task_id: `isqTrain/2964`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2162`

### Prompt

帮我写一个isQ程序：applies 2 layer(s) of Hadamard + CNOT ring on 3 qubits. Each layer applies H to all qubits, then CNOT in a ring (q[i] -> q[(i+1)%3]).

Requirements:
- Declare `qbit q[3];` at global scope.
- Measure all 3 qubits.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit applies 2 layers of H+CNOT ring on 3 qubits. Let me trace through the state evolution.

Initial state: |000⟩

Layer 1:
- Apply H to all qubits: H|0⟩⊗H|0⟩⊗H|0⟩ = |+++⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

Actually, let me be more careful. |+⟩ = (|0⟩ + |1⟩)/√2, so:
|+++⟩ = (1/2√2)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

- CNOT(0,1): control=q[0], target=q[1]
- CNOT(1,2): control=q[1], target=q[2]
- CNOT(2,0): control=q[2], target=q[0]

Let me think about what happens when we apply these three CNOTs in sequence to |+++⟩.

|+++⟩ = (1/2√2) Σ_{x∈{0,1}^3} |x⟩

After CNOT(0,1): This maps |abc⟩ → |a, a⊕b, c⟩
So the state becomes (1/2√2) Σ |a, a⊕b, c⟩ where the sum is over a,b,c.

Actually, let me think in terms of the stabilizer formalism or just compute directly.

|+++⟩ can be written as |+⟩|+⟩|+⟩.

After CNOT(q[0], q[1]) on |+⟩|+⟩:
CNOT|++⟩ = CNOT(|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2
= (1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩)
= (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
= |++⟩

Interesting! CNOT|++⟩ = |++⟩. This is because |++⟩ is a +1 eigenstate of X⊗I and I⊗X, and CNOT maps X⊗I → X⊗X and I⊗X → I⊗X, so... wait, let me reconsider.

Actually, CNOT maps:
- X⊗I → X⊗X
- I⊗X → I⊗X

So if the input is |++⟩, which is stabilized by X⊗I and I⊗X, then after CNOT, it's stabilized by X⊗X and I⊗X. But wait, that's the same as the stabilizers of |++⟩? No...

The state |++⟩ is the unique state stabilized by X⊗I and I⊗X (both with +1 eigenvalue).

After CNOT, the stabilizers become X⊗X and I⊗X. The state stabilized by X⊗X and I⊗X with +1 eigenvalue is... well, X⊗X and I⊗X commute. The joint +1 eigenspace of I⊗X is spanned by |++⟩ and |--⟩. The joint +1 eigenspace of X⊗X is spanned by |++⟩ and |--⟩ as well (since X⊗X|++⟩ = |++⟩ and X⊗X|--⟩ = |--⟩). So the state after CNOT|++⟩ is indeed |++⟩.

Wait, but that's for 2 qubits. Let me consider all 3 qubits.

State after H⊗H⊗H on |000⟩ = |+++⟩.

Stabilizers: X⊗I⊗I, I⊗X⊗I, I⊗I⊗X (all with +1 eigenvalue)

After CNOT(q[0], q[1]) (control=0, target=1):
CNOT maps stabilizers by conjugation:
- X⊗I⊗I → X⊗X⊗I
- I⊗X⊗I → I⊗X⊗I  (target X unchanged when control is I... wait)

Actually, let me recall: CNOT conjugation rules:
- XI → XX (control X propagates to target)
- IX → IX (target X unchanged when control doesn't fire... no)

Wait, I need to be more careful. CNOT(c,t) conjugation:
- X_c I_t → X_c X_t
- I_c X_t → I_c X_t
- Z_c I_t → Z_c I_t  
- I_c Z_t → Z_c Z_t

For 3 qubits with CNOT(q[0], q[1]):
- X⊗I⊗I → X⊗X

## isqTrain/3889

- task_id: `isqTrain/3889`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3618`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// Grover search on 3 qubits targeting |101>
qbit q[3];

// Oracle: mark target state |101>
unit grover_oracle(qbit q[3]) {
    X(q[1]);
    ctrl CNOT(q[0], q[1], q[2]);
    X(q[1]);
} deriving gate

// Diffusion operator (inversion about mean)
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
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

// Main: 1 Grover iteration
procedure main() {
    // Initialize uniform superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Apply oracle + diffusion
    grover_oracle(q);
    grover_diffusion(q);
    // Measure all qubits
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze this Grover search circuit for the target state |101>.

**Understanding the Grover Oracle for |101>:**

The oracle should mark (flip the phase of) the target state |101>. The standard approach is:
1. Transform |101> to |111> using X gates on qubits that should be 0 (q[1] should be 0)
2. Apply a controlled-Z (or Toffoli-like phase flip) on |111>
3. Uncompute the X gates

Looking at the oracle:

The issue is `ctrl CNOT(q[0], q[1], q[2])`. 

In isQ, `ctrl CNOT(q[0], q[1], q[2])` means a controlled-CNOT, which is a Toffoli gate. A Toffoli gate flips the target qubit (q[2]) when both controls (q[0], q[1]) are |1>. This would change |111> to |110>, which is NOT what we want for an oracle. The oracle should only flip the phase, not change the computational state.

The fix is to use `ctrl CZ(q[0], q[1], q[2])` instead. A controlled-Z with two controls acts as a phase flip on |111> without changing the computational state.

Wait, let me reconsider. In isQ syntax, `ctrl CZ(q[0], q[1], q[2])` - this is a CZ gate with two control qubits. CZ already has one implicit control, so `ctrl CZ` would have two controls total. This applies a Z phase to q[2] when both q[0] and q[1] are |1>.

Actually, let me re-read the isQ syntax. The `ctrl` modifier adds control qubits. So `ctrl CZ(q[0], q[1], q[2])` means CZ(q[0], q[2]) controlled on q[1], or equivalently it's a multi-controlled Z operation.

With CZ(q[0], q[2]) controlled on q[1], this applies Z to q[2] when q[0]=1 AND q[1]=1. But we want the phase flip when all three are |1>.

Hmm, actually the standard way to do a 3-qubit phase flip on |111> is:
- Use a multi-controlled Z with all three qubits as controls/targets
- Or use a Z gate on one qubit controlled by the other two

In the diffusion operator, they use `ctrl CZ(q[0], q[1], q[2])` which seems to work correctly for the diffusion (inversion about mean).

Let me think about this differently. The controlled-CZ with two controls on three qubits effectively applies a phase of -1 to |111> only.

So the oracle should:
1. X(q[1]) to transform |101> → |111>
2. Apply multi-controlled Z to flip phase of |111>
3. X(q[1]) to uncompute

The bug is that step 2 uses `ctrl CNOT` instead of `ctrl CZ`. 

`ctrl CNOT(q[0], q[1], q[2])` is a Toffoli gate which flips q[2] when q[0]=q[1]=1. This changes |111> to |110>, which is wrong.

`ctrl CZ(q[0], q[1], q[2])` applies a Z phase flip to q[2] when q[0]=q[1]=1. This keeps |111> as -|111>, which is correct.

**State evolution of corrected circuit:**

Initial: |000>
After H on all: (1/2√2) Σ|x> (uniform superposition over all 8 states)

Oracle: marks |101> with -1 phase
→ (1/2√2)(|000>+|001>+|010>+|011>+|100>-|101>+|110>+|111>)

Diffusion: inverts about mean
Mean amplitude = (1/2√2)(7-1)/8 = 6/(8·2√2) = 3/(8√2)
Wait, let me recalculate.

The amplitudes are all 1/(2√2) except |101> which is -1/(2√2).

Mean = [7·1/(2√2) + (-1)/(2√2)] / 8 = 6/(8·2√2) = 6/(16√2) =

## isqExpand/algo/131

- task_id: `isqExpand/algo/131`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `1624`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[5];
procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    X(q[0]); X(q[3]);
    Toffoli(q[0], q[1], q[4]);
    H(q[3]); Toffoli(q[2], q[4], q[3]); H(q[3]);
    Toffoli(q[0], q[1], q[4]);
    X(q[0]); X(q[3]);
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    X(q[0]); X(q[1]); X(q[2]); X(q[3]);
    Toffoli(q[0], q[1], q[4]);
    H(q[3]); Toffoli(q[2], q[4], q[3]); H(q[3]);
    Toffoli(q[0], q[1], q[4]);
    X(q[0]); X(q[1]); X(q[2]); X(q[3]);
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
Oracle marks |0110> = index 6. X(q[0]),X(q[3]) flip zeros.
CCZ via ancilla: Toffoli(q0,q1,anc), H-Toffoli-H on (q2,anc,q3), Toffoli to uncompute.

1 iteration: P(|0110>) ~ 0.473, others ~ 0.035.
In 32-entry array (5 qubits): |0110,0> at index 12 with prob ~ 0.473.

### Reference answer

{'predicted_probs': [0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.47266, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0, 0.035156, 0.0], 'explanation': 'The oracle marks |0110> using the CCZ decomposition via ancilla. With 1 iteration on N=16: P(|0110>) = sin^2(3*theta) ~ 0.473 where theta = arcsin(1/4). Other 15 states each get ~ 0.035. The ancilla q[4] is always uncomputed to |0>.'}

## isqTrain/1138

- task_id: `isqTrain/1138`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1448`

### Prompt

帮我写一个isQ程序：implements a variant of the graph_state_preparation pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to generate reasoning for a graph state preparation circuit that:
1. Uses qubits q[3] to q[5] (which means q[3], q[4], q[5] - 3 qubits for the graph state)
2. Has an expanded qubit register with additional qubits in ground state
3. Implements a graph state variant

Analyzing the circuit requirements, it uses q[0], q[1], q[2] for a 3-qubit linear graph state with edges (0,1) and (1,2).

The new task asks for q[3] -> q[5], meaning the graph state is on qubits 3, 4, 5 with edges (3,4) and (4,5).

Let me trace through the circuit:
1. Start with all qubits in |0⟩
2. Apply H to q[3], q[4], q[5] → creates |+⟩|+⟩|+⟩ on those qubits
3. Apply CZ(q[3], q[4]) - controlled-Z between qubits 3 and 4
4. Apply CZ(q[4], q[5]) - controlled-Z between qubits 4 and 5
5. Apply H to q[3], q[4], q[5] before measurement (X-basis measurement)
6. Measure all qubits

The graph state on qubits 3, 4, 5 creates entanglement. After H gates before measurement, the outcomes should show correlations.

Since the task says "q[3] -> q[5]", I'll interpret this as using qubits q[3], q[4], q[5] for the graph state, with additional qubits (at least q[0], q[1], q[2], possibly more) left in |0⟩.

Actually, looking more carefully at "significantly expanded qubit register", the reference uses 5 qubits (q[0]-q[4]). If we're shifting to q[3]-q[5], we'd need at least 6 qubits, possibly more for "significantly expanded".

Let me think about what "significantly expanded" means. The base version uses 3 qubits for the graph state (q[0], q[1], q[2]) and has 5 total qubits. A "significantly expanded" version might have more total qubits.

I'll create a register with 8 qubits (q[0]-q[7]), use q[3], q[4], q[5] for the graph state, and leave others in |0⟩.

the predicted output would be:
- q[0], q[1], q[2], q[6], q[7] stay in |0⟩ → measure as 0
- q[3], q[4], q[5] form the graph state and after X-basis measurement give outcomes with equal probability for the graph state patterns

For a linear 3-qubit graph state measured in X basis, the outcomes should be correlated. Analyzing the predicted output {|00000>: 0.25, |01000>: 0.25, |10100>: 0.25, |11100>: 0.25}, these are for 5 qubits measured.

The predicted output format for --probs is "array indexed by measurement bitstring (earlier measured qubit = higher bit)". So for measuring q[0] through q[4] (or q[7]), the earlier measured qubits become higher bits.

Let me re-read: the reference measures M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]); and expects {|00000>: 0.25, |01000>: 0.25, |10100>: 0.25, |11100>: 0.25}.

So q[0] is the highest bit, q[4] is the lowest bit. The first 3 bits (q[0], q[1], q[2]) have the graph state correlations, and q[3], q[4] are 0.

For the new task using q[3]-q[5], if we measure all 8 qubits in order q[0] through q[7], the graph state correlations would be in positions 3, 4, 5 (bits 4, 3, 2 in the bitstring counting from MSB), and q[0], q[1], q[2], q[6], q[7] would be 0.

Hmm, but this is getting complex. Let me simplify and just generate the reasoning for what the circuit does.

The key points:
1. Goal: Prepare a 3-qubit linear graph state on q[3], q[4

## isqTrain/2965

- task_id: `isqTrain/2965`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `730`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[0]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[0]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis

**Operations applied:**
1. H on all 3 qubits (creates uniform superposition)
2. CNOT(q[0], q[1]), CNOT(q[1], q[2]), CNOT(q[2], q[0])
3. H on all 3 qubits again
4. CNOT(q[0], q[1]), CNOT(q[1], q[2]), CNOT(q[2], q[0])

**State evolution:**
1. Start: |000⟩
2. After H⊗3: |+++⟩ = (1/√8)Σ|x⟩ for all x

### Reference answer

{'predicted_probs': {'000': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/715

- task_id: `isqTrain/715`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3781`

### Prompt

Code this in isQ: implements a variant of the ripple_carry_adder pattern using q[5] -> q[6]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a 2-bit ripple carry adder variant with inputs a=1 (q[0]=1, q[1]=0) and b=1 (q[2]=1, q[3]=0), using q[4] as carry ancilla.

2. **Qubits**: 6-qubit register; measured qubits are q[2] (sum0), q[3] (sum1), q[5] (unused, stays |0⟩).

3. **State evolution**:
   - Initial: |000000⟩
   - X(q[0]), X(q[2]): |000010⟩ + |000100⟩ → |000110⟩ (encodes a₀=1, b₀=1)
   - Toffoli(q[0], q[2], q[4]): Since both controls are |1⟩, flips q[4] → |010110⟩ (carry₀ = 1)
   - CNOT(q[0], q[2]): q[0]=1, flips q[2]: 1→0 → |010010⟩ (sum₀ = a₀⊕b₀ =

## isqTrain/2913

- task_id: `isqTrain/2913`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5286`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
oracle bool[1] g(bool a[3]) {
    bool s[] = [true, true, false];
    bool ba[] = s & a;
    bool res[1];
    res[0] = ba[0] != ba[1] != ba[2];
    return res;
}
qbit q[3];
qbit anc[1];

procedure main() {
    // X(anc); // BUG: missing initialization
    H(anc);
    H(q);
    g(q, anc);
    H(q);
    for i in 0:3 {
        M(q[i]);
    }
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug**: The `X(anc);` gate is commented out in `main()`. For the Bernstein-Vazirani algorithm, the ancillary qubit must be in the state $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$ to achieve phase kickback. Without the X gate, the ancilla remains in $|0\rangle$, and applying H puts it in $|+\rangle$. The oracle then yields a state without the required phase shifts, and the final measurements will yield random results instead of the secret string.
2. **The fix**: Uncomment `X(anc);` so it executes before `H(anc);`. This initializes the ancilla to $|1\rangle$, allowing the subsequent H gate to correctly transform it into the $|-\rangle$ state.
3. **State evolution**: 
   - Start in $|000\rangle|0\rangle$. 
   - Apply `X(anc)` and then `H(anc)` and `H(q)` to get $|+++\rangle|-\rangle$.
   - The oracle applies a phase shift based on the secret string `[true, true, false]` (which corresponds to $|110\rangle$), resulting in $\sum (-1)^{s \cdot x}|x\rangle|-\rangle$.
   - Applying `H(q)` converts the phase-encoded state into the computational basis state $|110\rangle|-\rangle$.
   - Measuring the `q` register yields `110` with 100% probability.

## isqQA/quantum_algorithms/135_isq_implementation

- task_id: `isqQA/quantum_algorithms/135_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_implementation`, `algorithm`, `Swap测试`
- source: `qa_pipeline`
- dataset_index: `4103`

### Prompt

请编写完整的isQ语言代码来实现Swap测试算法，以估算两个单量子比特态的重叠度（内积的模方）。在代码中请包含详细的逐行注释说明其物理意义，并解释当无法直接使用内置SWAP门时，如何利用受控逻辑门构建等价的受控交换操作，以及该算法测量结果与态矢量重叠度之间的数学推导关系。

### Reference answer

<think>
首先，明确Swap测试的物理结构：需要1个辅助比特和2个目标态比特。在推导数学关系时，辅助比特经过H门和受控SWAP（CSWAP）操作后，会与目标态产生量子干涉。再次作用H门后，通过计算辅助比特处于|0⟩的态矢量概率幅，可得出测量概率 $P(0) = (1 + |\langle\psi|\phi\rangle|^2)/2$，进而反推出重叠度公式。

其次，处理isQ语言中无内置SWAP门限制的替代方案。由于SWAP操作可分解为三个CNOT门，将其整体受控化，即可等价替换为三个Toffoli门（CCX门），并将辅助比特作为高阶控制位。

最后，规划代码结构：在主程序中依次执行量子比特分配、初态制备、H门干预、基于CCX的受控交换逻辑、第二次H门干预及辅助比特测量。在编码时，将上述物理演化和门电路替换逻辑作为详细注释融入对应代码行中，确保严格契合题目要求。
</think>

Swap测试是量子计算中一个非常经典的算法，主要用于计算两个量子态之间的内积模方，即保真度。其核心思想是利用一个辅助量子比特控制的交换操作，通过量子干涉将状态的重叠信息转移到辅助比特的相位上，最后通过测量辅助比特的概率分布得到结果。假设辅助比特初态为|0⟩，待比较的两个态为|ψ⟩和|φ⟩。首先对辅助比特施加Hadamard门，使其进入(|0⟩+|1⟩)/√2的叠加态。接着执行受控SWAP操作：当辅助比特为|1⟩时，交换|ψ⟩和|φ⟩；为|0⟩时不交换。此时系统的状态变为 (|0⟩|ψ⟩|φ⟩ + |1⟩|φ⟩|ψ⟩)/√2。对辅助比特再次施加Hadamard门，系统状态演化为 0.5|0⟩(|ψ⟩|φ⟩ + |φ⟩|ψ⟩) + 0.5|1⟩(|ψ⟩|φ⟩ - |φ⟩|ψ⟩)。测量辅助比特得到|0⟩的概率为 P(0) = (1 + |⟨ψ|φ⟩|²) / 2。因此，通过多次射击测量计算P(0)，即可反推出两个态的重叠度 |⟨ψ|φ⟩|² = 2P(0) - 1。在isQ语言中，由于规定了禁止直接使用SWAP门，我们可通过三个Toffoli门（即双重受控X门）来等价实现受控SWAP操作：Toffoli(c, a, b) -> Toffoli(c, b, a) -> Toffoli(c, a, b)。以下为完整的isQ代码实现：

import std;

// 声明全局量子比特数组
// q[0] 为辅助比特，用于控制和最终测量
// q[1] 为第一个输入态 |psi>
// q[2] 为第二个输入态 |phi>
qbit q[3];

procedure main() {
    // 1. 制备待测试的量子态
    // 这里以任意旋转态为例，通过Ry门分别制备两个不同的量子态
    // 将 q[1] 绕Y轴旋转 pi/3，制备出特定的 |psi>
    Ry(pi/3, q[1]);
    // 将 q[2] 绕Y轴旋转 pi/2，制备出特定的 |phi>
    Ry(pi/2, q[2]);

    // 2. 开始 Swap 测试量子线路
    // 对辅助比特 q[0] 施加 Hadamard 门，进入均匀叠加态
    H(q[0]);

    // 3. 施加受控交换操作
    // 由于不能直接使用SWAP门，受控SWAP(c; a, b)可通过分解为三个Toffoli门实现
    // 第一个Toffoli：如果辅助位c为1，且a为1，则翻转b
    Toffoli(q[0], q[1], q[2]);
    // 第二个Toffoli：如果辅助位c为1，且b为1，则翻转a
    Toffoli(q[0], q[2], q[1]);
    // 第三个Toffoli：如果辅助位c为1，且a为1，则再次翻转b
    // 以上三步在控制位为1时，等效于交换了q[1]和q[2]的状态
    Toffoli(q[0], q[1], q[2]);

    // 4. 再次对辅助比特施加 Hadamard 门完成干涉
    H(q[0]);

    // 5. 测量辅助比特
    // 测量结果存储在经典寄存器变量 r 中
    // r 为 0 的概率 P(0) = (1 + |<psi|phi>|^2) / 2
    int r = M(q[0]);
}

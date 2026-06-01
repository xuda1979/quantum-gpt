# ISQ training COT RAG corpus: quantum_algorithms shard 36

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/137

- task_id: `isqTrain/137`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1709`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[3];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    X(q[0]); H(q[0]); // State = |->
    
    H(q[1]); CNOT(q[1], q[2]); // EPR
    
    CNOT(q[0], q[1]); H(q[0]); // Alice
    
    CNOT(q[1], q[2]); ctrl my_z(q[0], q[2]); // Bob
    
    H(q[2]); // Bob verifies by changing |-> to |1>
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output a circuit analysis for an isQ program.
    *   Format: Concise, precise step-by-step reasoning using Dirac notation.
    *   Starting string: "## Circuit Analysis"
    *   Ending: Predicted probability distribution.
    *   No code blocks.
    *   Length: 3-8 lines for simple, up to 15 for complex (this one is moderately complex - 3 qubits, quantum teleportation / state transfer variation).
    *   Input program: A 3-qubit circuit.
        *   `X(q[0]); H(q[0]);` -> $|-\rangle$
        *   `H(q[1]); CNOT(q[1], q[2]);` -> Bell pair $|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$
        *   `CNOT(q[0], q[1]); H(q[0]);` -> Alice's measurement basis for teleportation.
        *   `CNOT(q[1], q[2]); ctrl my_z(q[0], q[2]);` -> Bob's correction. Note `ctrl my_z` is a CZ gate. Wait, the correction is `CNOT(q[1], q[2])` followed by `ctrl my_z(q[0], q[2])`? Let's trace carefully.
        *   `H(q[2]);` -> Final H.
        *   Measurements on all qubits.

2.  **Step-by-Step State Evolution:**
    *   Initial: $|000\rangle$
    *   $X(q_0) H(q_0) \rightarrow |-\rangle_0 |00\rangle_{12}$
    *   $H(q_1) CNOT(q_1, q_2) \rightarrow |-\rangle_0 \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)_{12} = \frac{1}{\sqrt{2}} (|0\rangle_0|00\rangle_{12} - |1\rangle_0|00\rangle_{12} + |0\rangle_0|11\rangle_{12} - |1\rangle_0|11\rangle_{12})/\sqrt{2}$ -> actually, let's keep it factored for teleportation:
        $|-\rangle_0 |\Phi^+\rangle_{12}$
    *   $CNOT(q_0, q_1) H(q_0)$:
        $H_0 CNOT_{01} \frac{1}{2}(|0\rangle - |1\rangle)_0 \otimes (|00\rangle + |11\rangle)_{12}$
        Wait, what is the standard teleportation mapping?
        $|0\rangle |00\rangle \xrightarrow{CNOT_{01}} |0\rangle |00\rangle \xrightarrow{H_0} \frac{1}{\sqrt{2}}(|0\rangle+|1\rangle)|00\rangle$
        $|1\rangle |00\rangle \xrightarrow{CNOT_{01}} |1\rangle |10\rangle \xrightarrow{H_0} \frac{1}{\sqrt{2}}(|0\rangle-|1\rangle)|10\rangle$
        $|0\rangle |11\rangle \xrightarrow{CNOT_{01}} |0\rangle |11\rangle \xrightarrow{H_0} \frac{1}{\sqrt{2}}(|0\rangle+|1\rangle)|11\rangle$
        $|1\rangle |11\rangle \xrightarrow{CNOT_{01}} |1\rangle |01\rangle \xrightarrow{H_0} \frac{1}{\sqrt{2}}(|0\rangle-|1\rangle)|01\rangle$
        Combine for $|-\rangle = \frac{|0\rangle-|1\rangle}{\sqrt{2}}$:
        $\frac{1}{\sqrt{2}} ( \text{first} - \text{second} ) \otimes |00\rangle$ ... Wait, no. The state is $(|0\rangle - |1\rangle)/\sqrt{2} \otimes (|00\rangle + |11\rangle)/\sqrt{2}$.
        This equals $\frac{1}{2} [ |000\rangle + |011\rangle - |100\rangle - |111\rangle ]$.
        Apply $CNOT_{01}$: $\frac{1}{2} [ |000\rangle + |011\rangle - |110\rangle - |101\rangle ]$
        Apply $H_0

### Reference answer

{'predicted_probs': {'1': 0.25, '3': 0.25, '5': 0.25, '7': 0.25}, 'explanation': 'Parametric variant of isqHumanEval/48. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4195

- task_id: `isqTrain/4195`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `827`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    Rz(2.0 * 0.785, q[3]);
    CNOT(q[2], q[3]);
    CNOT(q[0], q[3]);
    Rz(2.0 * 0.785, q[3]);
    CNOT(q[0], q[3]);
    Rx(2.0 * 0.393, q[0]);
    Rx(2.0 * 0.393, q[1]);
    Rx(2.0 * 0.393, q[2]);
    Rx(2.0 * 0.393, q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit starts with 4 qubits all in |0⟩ state.

First, H gates are applied to all 4 qubits:
|ψ⟩ = |+⟩|+⟩|+⟩|+⟩ = (1/4)(|0000⟩ + |0001⟩ + |0010⟩ + |0011⟩ + |0100⟩ + |0101⟩ + |0110⟩ + |0111⟩ + |1000⟩ + |1001⟩ + |1010⟩ + |1011⟩ + |1100⟩ + |1101⟩ + |1110⟩ + |1111⟩)

Now let's track the CNOT-Rz-CNOT sequences. 

These are controlled-phase operations:
- CNOT(q[0], q[1]); Rz(2.0 * 0.785, q[1]); CNOT(q[0], q[1]) applies a phase to |11⟩ on q[0],q[1]
  
Wait, let me be more careful. The pattern CNOT(c, t); Rz(θ, t); CNOT(c, t) implements a controlled-Rz(θ) gate with a phase difference. Let me think about this more carefully.

Actually, CNOT(c,t); Rz(θ, t); CNOT(c,t) applies Rz(θ) on the target only when the control is |1⟩. But there's also a global phase from Rz.

Let me think of it differently. Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}).

The sequence CNOT(c,t); Rz(θ, t); CNOT(c,t):
- When control is |0⟩: nothing happens from CNOTs, and Rz(θ) applies to target → gives phase e^{-iθ/2} on |0⟩_t and e^{iθ/2} on |1⟩_t (with overall phase e^{-iθ/2}... wait no, Rz is diag(e^{-iθ/2}, e^{iθ/2}))

Actually, let me think about this in the computational basis more carefully.

The initial state after H on all qubits is an equal superposition of all 16 basis states.

Let me track what each block does:

Block 1: CNOT(q[0],q[1]); Rz(1.57, q[1]); CNOT(q[0],q[1])
This is equivalent to: when q[0]=1, apply Rz(1.57) to q[1]. 

CNOT(q[0],q[1]) flips q[1] when q[0]=1. Then Rz(1.57) = diag(e^{-i*0.785}, e^{i*0.785}) applies to q[1]. Then CNOT flips q[1] back when q[0]=1.

So for basis states where q[0]=0: CNOT does nothing, Rz applies directly to q[1], CNOT does nothing. The phase applied is e^{-i*0.785} if q[1]=0, e^{i*0.785} if q[1]=1.

For basis states where q[0]=1: CNOT flips q[1], then Rz applies (phase e^{-i*0.785} if q[1] was 1 and became 0, e^{i*0.785} if q[1] was 0 and became 1), then CNOT flips back. So phase is e^{-i*0.785} if original q[1]=1, e^{i*0.785} if original q[1]=0.

Wait, that's the opposite! When q[0]=1, the phase on q[1] is flipped compared to when q[0]=0.

So the net effect: 
- |q0 q1⟩ → phase factor that depends on q0 and q1
- When q0=0, q1=0: phase e^{-i*0.785}
- When q0=0, q1=1: phase e^{i*0.785}
- When q0=1, q1=0: phase e^{i*0.785} (flipped because CNOT flipped q1, Rz saw |1⟩, gave e^{i*0.785})
- When q0=1, q1=1: phase e^{-i*0.785} (flipped because CNOT flipped q1 to 0, Rz saw |0⟩, gave e^{-i*0.785})

So the relative phase between |q0 q1=0⟩ and |q0 q1=

### Reference answer

Uniform distribution across 8 states

## isqTrain/2624

- task_id: `isqTrain/2624`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `global_phase`, `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1250`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;

qbit q[2];

procedure main() {
    H(q[0]);
    X(q[1]);
    
    ctrl Rx(3.14159265, q[0], q[1]);
    
    H(q[0]);
    M(q[0]);
}

```

```isq
import std;

qbit q[2];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]);
    X(q[1]);
    
    ctrl Rx(3.14159265, q[0], q[1]);
    
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Determine if two isQ programs produce the same measurement probability distribution.
    *   Program A: Applies H to q[0], X to q[1], controlled-Rx(pi) (q[0] -> q[1]), H to q[0], measures q[0].
    *   Program B: Same as A but starts with `GPhase(0.0)`.
    *   Format Requirements: Output ONLY the analysis starting with "## Equivalence Analysis". End with a clear "Yes/No" verdict line. Use Dirac notation. Be concise (3-8 lines for simple).

2.  **Analyze Program A:**
    *   Initial state: |00>
    *   H(q[0]) -> |+0> = (|00> + |10>) / sqrt(2)
    *   X(q[1]) -> (|01> + |11>) / sqrt(2)
    *   ctrl Rx(pi, q[0], q[1]): When q[0] is |1>, apply Rx(pi) to q[1].
        *   Rx(pi) = e^{-i\pi X/2} = -iX. So it flips q[1] and adds a phase.
        *   Wait, Rx(pi) on |0> is -i|1>. Rx(pi) on |1> is -i|0>.
        *   State becomes: (|01> + (-i)|10>) / sqrt(2)
    *   H(q[0]): H on q[0].
        *   H|0> = |+>, H|1> = |->
        *   ( |1>(q[0])|1>(q[1]) + (-i)|->(q[0])|0>(q[1]) ) / sqrt(2)
        *   Actually, let's trace it carefully.
        *   State before last H: (1/sqrt(2)) (|01> - i |10>)
        *   Apply H on q[0]:
        *   H(1/sqrt(2) |01>) = (1/2) (|0> + |1>) |1> = (1/2) (|01> + |11>)
        *   H(-i/sqrt(2) |10>) = (-i/2) (|0> - |1>) |0> = (-i/2) (|00> - |10>)
        *   Wait, is the measurement only on q[0]? "M(q[0])"
        *   Yes, only q[0] is measured.
        *   Let's check probabilities for q[0]:
        *   Amplitude of |0>_0: 1/2 |1>_1 - i/2 |0>_1
        *   Amplitude of |1>_0: 1/2 |1>_1 + i/2 |0>_1
        *   P(q[0]=0) = || 1/2 |1> - i/2 |0> ||^2 = 1/4 + 1/4 = 1/2
        *   P(q[0]=1) = || 1/2 |1> + i/2 |0> ||^2 = 1/4 + 1/4 = 1/2

3.  **Analyze Program B:**
    *   `GPhase(0.0)` multiplies the entire quantum state by e^{i*0} = 1. It's the identity operation.
    *   The rest of the circuit is identical to Program A.
    *   Therefore, the final quantum state and measurement probabilities are identical.

4.  **Draft the Analysis (following the 5 steps):**
    *   1. *Program A summary:* Applies H, X, and a controlled-Rx($\pi$) gate, followed by a final H on $q[0]$ before measurement.
    *   2. *Program B summary:* Applies a trivial global phase `GPhase(0.0)` before executing the exact same sequence of gates as Program A.
    *   3. *Key difference:* Program B includes `GPhase(0.0)`, whereas Program A does not explicitly apply it.
    *   4. *Probabilities comparison:* `GPhase(0.0)` applies a phase factor of $e^{i0} = 1$, which is mathematically an identity operation. Thus, both programs yield the identical quantum state and the same 50/50 measurement probabilities on $q[0]$.
    *   5. *Verdict:* Equivalent: Yes

5.  **Refine and Format (Concise, 3-8 lines):**

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/3647

- task_id: `isqTrain/3647`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `1642`

### Prompt

Implement a quantum circuit in isQ: the 3-qubit inverse Quantum Fourier Transform (QFT†) on input |110>. Use bit-reversal swaps first, then apply inverse rotation stages with negative angles. Measure all qubits.

### Chain-of-thought reasoning

Let me analyze this task carefully.

The goal is to implement the 3-qubit inverse Quantum Fourier Transform (QFT†) on input |110>.

First, let me understand the initial state:
- We start with |000⟩
- After X(q[0]): |100⟩
- After X(q[1]): |110⟩

So the input to the inverse QFT is |110⟩.

Now, QFT maps |j⟩ → (1/√N) Σ_k e^(2πijk/N) |k⟩

For 3 qubits, N = 8.

The inverse QFT should take the Fourier basis state back to the computational basis state.

But wait, |110⟩ = |6⟩ in decimal. Let me think about what QFT(|6⟩) would be, and then QFT† should undo that.

Actually, let me reconsider. The inverse QFT acts on |110⟩ directly. The state |110⟩ in the Fourier basis is:
QFT†(|6⟩) = QFT†(|110⟩)

Wait, I need to think about this more carefully. The inverse QFT takes a state and maps it back from the Fourier basis to the computational basis.

QFT|j⟩ = (1/√8) Σ_k e^(2πijk/8) |k⟩

So QFT† maps (1/√8) Σ_k e^(2πijk/8) |k⟩ → |j⟩

But |110⟩ = |6⟩ is a computational basis state, not a Fourier basis state.

Let me compute QFT†(|6⟩):

QFT† = (1/√8) Σ_k e^(-2πijk/8) |k⟩⟨j|

Actually, let me think differently. 

QFT|k⟩ = (1/√8) Σ_j e^(2πijk/8) |j⟩

So QFT†(Σ_j α_j|j⟩) = Σ_k (1/√8) Σ_j α_j e^(-2πijk/8) |k⟩

For input |6⟩, α_j = δ_{j,6}:

QFT†(|6⟩) = (1/√8) Σ_k e^(-2πi·6·k/8) |k⟩
           = (1/√8) Σ_k e^(-πi·3k/2) |k⟩

Let me compute each term:
- k=0: e^0 = 1, |0⟩
- k=1: e^(-3πi/2) = e^(πi/2) = i, |1⟩
- k=2: e^(-3πi) = e^(πi) = -1, |2⟩
- k=3: e^(-9πi/2) = e^(-πi/2) = -i, |3⟩
- k=4: e^(-6πi) = 1, |4⟩
- k=5: e^(-15πi/2) = e^(πi/2) = i, |5⟩
- k=6: e^(-9πi) = -1, |6⟩
- k=7: e^(-21πi/2) = e^(-πi/2) = -i, |7⟩

So QFT†(|6⟩) = (1/√8)(|0⟩ + i|1⟩ - |2⟩ - i|3⟩ + |4⟩ + i|5⟩ - |6⟩ - i|7⟩)

The probabilities would all be |1/√8|² = 1/8 = 0.125.

This matches the predicted output!

Now let me trace through the code to verify:

Initial state: |000⟩

After X(q[0]): |100⟩
After X(q[1]): |110⟩

Now the inverse QFT with bit-reversal swaps:

The standard QFT circuit works as follows for 3 qubits q[0], q[1], q[2]:
- QFT applies H on q[0], then controlled rotations from q[1], q[2] to q[0]
- Then H on q[1], then controlled rotation from q[2] to q[1]
- Then H on q[2]
- Then bit-reversal swaps

For inverse QFT, we reverse the order:
1. Bit-reversal swaps first (swap q[0]↔q[2])
2. Then inverse rotation stages

Bit-reversal swaps:
CNOT(q[0], q[2]);
CNOT(q[2], q[0]);
CNOT(q[0], q[2]);

This swaps q[0] and q[2]. After swap, |110

## isqTrain/2077

- task_id: `isqTrain/2077`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `mid_circuit_measurement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3448`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    H(q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[0], q[1]);
    H(q[0]);
    M(q[0]); M(q[1]);
    CNOT(q[1], q[2]);
    CZ(q[0], q[2]);
    H(q[2]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

Initial state: |000⟩

1. H(q[0]): |0⟩ → |+⟩, state becomes |+00⟩ = (|000⟩ + |100⟩)/√2

2. H(q[1]): |0⟩ → |+⟩, state becomes (|+00⟩ + |1+0⟩)/√2 wait let me be more careful.

State after H(q[0]): (|000⟩ + |100⟩)/√2

3. H(q[1]): (|000⟩ + |100⟩)/√2 → (|0⟩+|1⟩)(|0⟩+|1⟩)|0⟩/2 = (|000⟩ + |010⟩ + |100⟩ + |110⟩)/2

4. CNOT(q[1], q[2]): This flips q[2] when q[1] is |1⟩.
(|000⟩ + |011⟩ + |100⟩ + |111⟩)/2

5. CNOT(q[0], q[1]): This flips q[1] when q[0] is |1⟩.
(|000⟩ + |011⟩ + |110⟩ + |101⟩)/2

6. H(q[0]): Apply H to q[0].
|000⟩ → |000⟩ + |100⟩ (H on first qubit)
|011⟩ → |011⟩ + |111⟩
|110⟩ → |010⟩ - |110⟩ (since |1⟩→|−⟩)
|101⟩ → |001⟩ - |101⟩

Wait, let me be more careful with H on q[0]:
H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2
H|1⟩ = |−⟩ = (|0⟩-|1⟩)/√2

So the state becomes:
(1/2)[(1/√2)(|000⟩+|100⟩) + (1/√2)(|011⟩+|111⟩) + (1/√2)(|010⟩-|110⟩) + (1/√2)(|001⟩-|101⟩)]

= (1/(2√2))[|000⟩+|100⟩+|011⟩+|111⟩+|010⟩-|110⟩+|001⟩-|101⟩]

Now, M(q[0]) and M(q[1]) are measurements. The circuit then continues with operations that depend on the measurement outcomes.

After measuring q[0] and q[1], we have classical bits. The remaining operations are:
- CNOT(q[1], q[2])
- CZ(q[0], q[2])
- H(q[2])
- M(q[2])

Let me trace through each possible measurement outcome.

After H(q[0]), the state is:
(1/(2√2))[|000⟩+|001⟩+|010⟩+|011⟩+|100⟩-|101⟩-|110⟩+|111⟩]

Let me re-derive. After step 5, the state is:
(|000⟩ + |011⟩ + |110⟩ + |101⟩)/2

Let me write this in terms of q[0], q[1], q[2]:
q[0]=0, q[1]=0, q[2]=0: amplitude 1/2
q[0]=0, q[1]=1, q[2]=1: amplitude 1/2
q[0]=1, q[1]=1, q[2]=0: amplitude 1/2
q[0]=1, q[1]=0, q[2]=1: amplitude 1/2

Now apply H(q[0]):
|q[0]q[1]q[2]⟩ where H acts on q[0]:

For |000⟩: H on q[0] → (|000⟩+|100⟩)/√2
For |011⟩: H on q[0] → (|011⟩+|111⟩)/√2
For |110⟩: H on q[0] → (|010⟩-|110⟩)/√2 (H|1⟩=(|0⟩-|1⟩)/√2, wait no)

Actually wait. H|1⟩ = (|0⟩ - |1⟩)/√2. So for |110⟩, applying H to q[0]:
|110⟩ → (|010⟩ - |110⟩)/√2

For |101⟩: applying H to q[0]:
|101⟩ → (|001⟩ - |101⟩)/√2

Total state:
(1/2)[1/√2(|000⟩+|100⟩) + 1/√2(|

### Reference answer

{'predicted_probs': {'000': 0.25, '010': 0.25, '100': 0.25, '110': 0.25}, 'explanation': 'Teleport |+> state and verify in X basis.'}

## isqTrain/870

- task_id: `isqTrain/870`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3186`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[3];

procedure main() {
    // Set inputs: a=1, b=0
    X(q[0]);
    // De Morgan: OR(a,b) = NOT(NOT(a) AND NOT(b))
    // Step 1: negate inputs
    X(q[0]); X(q[1]);
    // Step 2: Toffoli computes AND of negated inputs
    ctrl ctrl X(q[0], q[1], q[2]);
    // Step 3: restore original inputs
    X(q[0]); X(q[1]);
    // Step 4: negate the AND result to get OR
    X(q[2]);
    // Measure all qubits
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
- The circuit initializes 3 qubits to |000>. `X(q[0])` sets input a=1, resulting in |100>.
- The next two `X` gates negate both inputs, transforming the state to |011>.
- The Toffoli gate (`ctrl ctrl X`) computes the AND of the negated inputs. Since both controls are |1>, it flips the target q[2] to |1>, resulting in |111>.
- Two subsequent `X` gates restore the original inputs, changing the state to |101>.
- A final `X` gate on q[2] negates the AND result, completing the OR operation via De Morgan's laws, and leaving the final state exactly |101>.

Predicted probability distribution: {|101>: 1.0}

### Reference answer

{'predicted_probs': {'5': 1.0}, 'explanation': 'Parametric variant of isqEval/253. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1098

- task_id: `isqTrain/1098`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4645`

### Prompt

用isQ实现implements the bernstein_vazirani pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Bernstein-Vazirani to find hidden string s=101 using a single oracle query.

Qubits: 4 total (q[0-2] input, anc[0] ancilla); 3 measured (q[0-2]).

State evolution:
1. Initial: |000⟩|0⟩
2. X(anc[0]); H(anc[0]): |000⟩|−⟩
3. H(q[0,1,2]): |+++⟩|−⟩ = (1/2√2)Σ_x|x⟩|−⟩
4. Oracle f applies phase (-1)^(x₀⊕x₂): (1/2√2)Σ_x(-1)^(x₀⊕x₂)|x⟩|−⟩
5. H(q[0,1,2]) decodes phase pattern → |101⟩|−⟩
6. H-H on q[0] is identity (gate cancellation demo), state unchanged: |101⟩|−⟩

Expected probabilities: Measuring q[0,1,2] yields |101⟩ with probability 1.0 since the algorithm perfectly decodes s from the oracle's phase structure.

## isqTrain/3715

- task_id: `isqTrain/3715`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `22`

### Prompt

实现以下量子计算任务（使用isQ）：QAOA (p=1) for the MaxCut problem on a 3-node path graph with edges [(0, 1), (1, 2)]. Use parameters gamma=1.000 and beta=0.500. The circuit:
1. Initialize all qubits in superposition
2. Apply cost unitary: for each edge, use CNOT-Rz-CNOT
3. Apply mixer: Rx(2*beta) on each qubit
4. Measure all 3 qubits

### Chain-of-thought reasoning

Let me analyze this QAOA circuit step by step.

1. Goal: Implement QAOA (p=1) for MaxCut on a 3-node path graph with edges [(0,1), (1,2)].

2. Qubits: 3 qubits q[0], q[1], q[2], all measured.

3. State evolution:

Initial state: |000⟩

After H on all qubits: |+++⟩ = (1/2√2)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

Cost unitary for edge (0,1): CNOT(q[0], q[1]), Rz(2γ, q[1]), CNOT(q[0], q[1])
This implements exp(-iγ Z₀Z₁)

Cost unitary for edge (1,2): CNOT(q[1], q[2]), Rz(2γ, q[2]), CNOT(q[1], q[2])
This implements exp(-iγ Z₁Z₂)

The cost unitary applies phase exp(-iγ) when Z_i Z_j = +1 (same parity) and exp(+iγ) when Z_i Z_j = -1 (different parity).

For each basis state |q₀q₁q₂⟩, the phase from the cost unitary is:
- Edge (0,1): exp(-iγ(-1)^(q₀⊕q₁)) 
- Edge (1,2): exp(-iγ(-1)^(q₁⊕q₂))

Wait, let me reconsider. The Rz(2γ) gate applies exp(-iγ) to |0⟩ and exp(+iγ) to |1⟩.

Actually, the CNOT-Rz(2γ)-CNOT sequence:
- When q₀=0, q₁ unchanged, Rz(2γ) on q₁
- When q₀=1, q₁ flipped, then Rz(2γ), then flip back

The net effect: exp(-iγ Z₀Z₁) - this gives:
- exp(+iγ) when q₀=q₁
- exp(-iγ) when q₀≠q₁

Wait, let me be more careful. exp(-iγ Z⊗Z) = exp(-iγ) when both same, exp(+iγ) when different? No.

Z⊗Z has eigenvalue +1 when both same (|00⟩ or |11⟩), eigenvalue -1 when different (|01⟩ or |10⟩).

So exp(-iγ Z⊗Z) gives:
- exp(-iγ) for |00⟩, |11⟩
- exp(+iγ) for |01⟩, |10⟩

Hmm, but the CNOT-Rz-CNOT implementation: let me verify.

CNOT(0,1) flips q[1] when q[0]=|1⟩.
Rz(2γ, q[1]) applies phase exp(-iγ) to |0⟩ and exp(+iγ) to |1⟩ on q[1].
CNOT(0,1) flips back.

Starting with |00⟩: CNOT gives |00⟩, Rz gives exp(-iγ)|00⟩, CNOT gives exp(-iγ)|00⟩
Starting with |01⟩: CNOT gives |01⟩, Rz gives exp(+iγ)|01⟩, CNOT gives exp(+iγ)|01⟩
Starting with |10⟩: CNOT gives |11⟩, Rz gives exp(+iγ)|11⟩, CNOT gives exp(+iγ)|10⟩
Starting with |11⟩: CNOT gives |10⟩, Rz gives exp(-iγ)|10⟩, CNOT gives exp(-iγ)|11⟩

So the phase is:
- exp(-iγ) for |00⟩, |11⟩ (same parity)
- exp(+iγ) for |01⟩, |10⟩ (different parity)

This matches exp(-iγ Z₀Z₁).

Now for the full circuit with γ=1.0, β=0.5:

After H⊗3: |ψ₁⟩ = |+++⟩

After cost unitary:
Each basis state |q₀q₁q₂⟩ picks up phase exp(-iγ[(-1)^(q₀⊕q₁) + (-1)^(q₁⊕q₂)])

Wait, I need to be more careful. Let me compute for each state:

For |000⟩: q₀=q₁, q₁=q₂ → exp(-iγ) × exp(-iγ) = exp(-2iγ)
For |001⟩: q₀=q₁, q₁≠q₂ → exp(-iγ) × exp(+iγ) = 1
For |

## isqTrain/3581

- task_id: `isqTrain/3581`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `665`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 4-qubit Ising chain, 2 Trotter steps.

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug identification:**
The bug is in Trotter step 1, line 7. The first CNOT for the ZZ interaction on pair (0,1) has reversed arguments: `CNOT(q[1], q[0])` instead of `CNOT(q[0], q[1])`. The CNOT-Rz-CNOT pattern for a ZZ interaction requires consistent control-target ordering: the same qubit must be control in both CNOTs, with Rz applied to the target. The buggy line makes q[1] the control and q[0] the target, while the second CNOT uses q[0] as control and q[1] as target — breaking the pattern.

**2. Fix:**
Change `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])` in the first ZZ interaction block of Trotter step 1. This ensures the standard decomposition: CNOT(c,t) → Rz(θ, t) → CNOT(c,t), which applies `exp(-iθ/2) * CZ(θ)` correctly on the pair.

**3. State evolution (corrected circuit):**
- Initial: |0000⟩
- After ZZ on (0,1): CNOT(q[0],q[1]) leaves |0000⟩; Rz(0.4,q[1]) adds no phase to |0⟩; CNOT(q[0],q[1]) restores → still |0000⟩
- Same for ZZ on (1,2) and (2,3): |0000⟩ is an eigenstate of ZZ, so no change
- After Rx(0.2) on all qubits: each qubit rotates to cos(0.1)|0⟩ - i·sin(0.1)|1⟩, creating a product state with small |1⟩ amplitudes
- Trotter step 2 repeats ZZ and Rx, mixing amplitudes via ZZ interactions while Rx further rotates
- Final measurement yields dominant |0000⟩ (~0.865) with small probabilities for single-excitation states (~0.

## isqTrain/1134

- task_id: `isqTrain/1134`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `interference`
- source: `isq_train_cot`
- dataset_index: `153`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

// SWAP test to compare two quantum states
qbit q[3];

procedure main() {
    // q[0] = ancilla, q[1] = state A, q[2] = state B
    // Both states are |0> (identical)
    // Hadamard on ancilla
    H(q[0]);
    // Controlled-SWAP (Fredkin gate)
    ctrl SWAP(q[0], q[1], q[2]);
    // Hadamard to interfere
    H(q[0]);
    // Identical states always yield |0> on ancilla
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Operations applied: Hadamard on q[0], controlled-swap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)) with q[0] as control and q[1], q[2] as targets, Hadamard on q[0], and measurement on q[0].
2. Initial state is |000>. The first Hadamard gate on the ancilla puts it into a superposition, evolving the state to (|000> + |100>) / √2.
3. The controlled-swap operation (three-CNOT decomposition) exchanges q[1] and q[2] when q[0] is |1>. Since both target qubits are in the |0> state, the swap leaves the state unchanged: (|000> + |100>) / √2.
4. The final Hadamard gate on q[0] constructively interferes with the |0> amplitude and destructively interferes with the |1> amplitude, resulting in the exact state |000>.
5. Measuring q[0] guarantees the |0> outcome, confirming the two quantum states being compared are identical.

Predicted probability distribution: {|0>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqEval/438. Dimension: predict probabilities for reference circuit.'}

# ISQ training COT RAG corpus: quantum_simulation shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2598

- task_id: `isqTrain/2598`
- task_type: `code_equivalence`
- category: `quantum_simulation`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_arrays`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1181`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;

qbit q[2]; 

procedure ZZ_evolve(double theta, qbit a, qbit b) {
    CNOT(a, b);
    Rz(theta, b);
    CNOT(a, b);
}

procedure main() {
    H(q[0]); H(q[1]);
    ZZ_evolve(pi/2.0, q[0], q[1]);
    
    M(q[0]); M(q[1]);
}

```

vs.

```isq
import std;

qbit q[2]; 

procedure ZZ_evolve(double theta, qbit a, qbit b) {
    CNOT(a, b);
    Rz(theta, b);
    CNOT(a, b);
}

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]); H(q[1]);
    ZZ_evolve(pi/2.0, q[0], q[1]);
    
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Applies H to q[0] and q[1], initializing them to the |+>|+> state. It then applies a ZZ evolution gate `ZZ_evolve(pi/2.0, q[0], q[1])`, which entangles the qubits. Finally, it measures both qubits.
2. **Program B**: Applies the exact same sequence of gates as Program A: H gates followed by the `ZZ_evolve` gate, and then measurement.
3. **Key difference**: Program B contains an additional `GPhase(0.0)` gate before the H gates.
4. **Measurement probabilities**: `GPhase(0.0)` applies a global phase of $e^{i(0.0)} = 1$. Since this is an identity operation with no phase shift, the quantum state remains entirely unchanged. Therefore, the measurement probability distribution is identical.
5. **Verdict**: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1969

- task_id: `isqTrain/1969`
- task_type: `output_prediction`
- category: `quantum_simulation`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5147`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];
procedure XY_evolve(double theta, qbit a, qbit b) {
    H(a); H(b);
    S(a); S(b);
    H(a);
    CNOT(a, b);
    Ry(-theta/2.0, a);
    Ry(-theta/2.0, b);
    CNOT(a, b);
    H(a);
    inv S(a); inv S(b);
    H(a); H(b);
}
procedure main() {
    X(q[0]);
    XY_evolve(pi/2.0, q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ program and predict the probability distribution of measurement outcomes.

The program applies an X gate to q[0], then calls `XY_evolve(pi/2.0, q[0], q[1])`.
Initial state: |00>
After X(q[0]): |10>

Let's trace `XY_evolve(theta, a, b)` where theta = pi/2.
The gates are:
H(a); H(b); S(a); S(b); H(a); CNOT(a, b); Ry(-theta/2, a); Ry(-theta/2, b); CNOT(a, b); H(a); inv S(a); inv S(b); H(a); H(b);

Wait, what does this sequence do?
Let's simplify it.
Let's denote a = q[0], b = q[1].
1. H(a); H(b) -> state is H_{a} \otimes H_{b} | \psi \rangle
2. S(a); S(b)
3. H(a) -> actually, H S H = Rz(pi/2) up to a phase. Wait, H S H = [[1, 1], [1, -1]] [[1, 0], [0, i]] [[1, 1], [1, -1]] / 2 = [[1+i, 1-i], [1-i, 1+i]] / 2.
Let's re-evaluate:
HS = [[1, 1], [1, -1]] / sqrt(2) * [[1, 0], [0, i]] = [[1, i], [1, -i]] / sqrt(2)
HSH = [[1, i], [1, -i]] / sqrt(2) * [[1, 1], [1, -1]] / sqrt(2) = [[1+i, 1-i], [1-i, 1+i]] / 2.
Wait, S = Rz(pi/2).
H S H = H Rz(pi/2) H = Rx(pi/2) up to phase. Wait, H Z H = X. So H Rz(theta) H = Rx(theta).
Actually, Rz(theta) = exp(-i theta Z / 2) = cos(theta/2) I - i sin(theta/2) Z.
So H Rz(theta) H = cos(theta/2) I - i sin(theta/2) X = Rx(theta).
Thus, H S H = Rx(pi/2) = X2P.

Let's look at the gates on b: H(b) S(b). The inverse at the end is inv S(b) H(b).
Wait, H(a) S(a) H(a) = Rx(pi/2). So H(b) S(b) at the beginning doesn't have an H after it.
Let's write the whole unitary:
U_xy = H_a H_b S_a S_b H_a CNOT_{ab} Ry_a(-th/2) Ry_b(-th/2) CNOT_{ab} H_a S^\dagger_a S^\dagger_b H_a H_b
Wait, inv S(a) inv S(b) H(a) H(b).
Wait, the order is:
H(a); H(b);
S(a); S(b);
H(a);
This means H(a) * S(a) * H(a) on qubit a. So it's Rx(pi/2) on a.
On qubit b, it's S(b) * H(b).
So the first part is: (Rx(pi/2) \otimes (S H))_{ab}
Then CNOT(a, b).
Then Ry(-th/2, a) Ry(-th/2, b) = Ry(-th/2) \otimes Ry(-th/2).
Then CNOT(a, b).
Then H(a); inv S(a); inv S(b); H(a); H(b).
Let's see: H(a) S^\dagger(a) = H(a) S^\dagger(a). Then H(a) is applied again?
Wait, the program says:
H(a);
inv S(a); inv S(b);
H(a); H(b);

Let's read the sequence carefully:
H(a); H(b); -> H \otimes H
S(a); S(b); -> S \otimes S
H(a); -> H \otimes I
So first part is (H S H) \otimes (S H) = Rx(pi/2) \otimes (S H).
Last part:
CNOT(a, b)
Ry(-th/2) \otimes Ry(-th/2)
CNOT(a, b)
H(a); -> I \otimes I ? No, H(a).
inv S(a); inv S(b); -> S^\dagger \otimes S^\dagger
H

### Reference answer

{'predicted_probs': {'00': 0.125, '01': 0.0214, '10': 0.7286, '11': 0.125}, 'explanation': 'XY parameterizable step equivalent'}

## isqTrain/1967

- task_id: `isqTrain/1967`
- task_type: `output_prediction`
- category: `quantum_simulation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5472`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];
procedure main() {
    double gamma = pi/4.0;
    double beta = pi/8.0;
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(-2.0 * gamma, q[1]);
    CNOT(q[0], q[1]);
    Rx(2.0 * beta, q[0]);
    Rx(2.0 * beta, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step analysis of an isQ quantum program to predict the probability distribution of measurement outcomes.
2.  **Analyze the isQ Code**:
    *   `qbit q[2];` -> 2 qubits initialized to $|00\rangle$.
    *   `double gamma = pi/4.0; double beta = pi/8.0;`
    *   `H(q[0]); H(q[1]);` -> Applies Hadamard to both. State becomes $|++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   `CNOT(q[0], q[1]);` -> Control=q[0], Target=q[1].
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to |01\rangle$
        *   $|10\rangle \to |11\rangle$
        *   $|11\rangle \to |10\rangle$
        *   State: $\frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + |10\rangle)$
    *   `Rz(-2.0 * gamma, q[1]);` -> $R_z(-\pi/2)$ on q[1]. $R_z(\theta) = e^{-i\theta/2}|0\rangle\langle0| + e^{i\theta/2}|1\rangle\langle1|$.
        *   For $\theta = -\pi/2$, phase shifts are $e^{i\pi/4}$ for $|0\rangle$ and $e^{-i\pi/4}$ for $|1\rangle$.
        *   State: $\frac{1}{2}(e^{i\pi/4}|00\rangle + e^{-i\pi/4}|01\rangle + e^{-i\pi/4}|11\rangle + e^{i\pi/4}|10\rangle)$
    *   `CNOT(q[0], q[1]);` -> Same as above, uncomputes the basis but phases are entangled.
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to |01\rangle$
        *   $|11\rangle \to |10\rangle$
        *   $|10\rangle \to |11\rangle$
        *   State: $\frac{1}{2}(e^{i\pi/4}|00\rangle + e^{-i\pi/4}|01\rangle + e^{-i\pi/4}|10\rangle + e^{i\pi/4}|11\rangle)$
        *   Notice this is $\frac{1}{2}(e^{i\pi/4}(|00\rangle + |11\rangle) + e^{-i\pi/4}(|01\rangle + |10\rangle))$.
        *   This can be factored by global phase $e^{-i\pi/4}$ as $e^{i\pi/2}\frac{1}{2}(|00\rangle + |11\rangle) + \frac{1}{2}(|01\rangle + |10\rangle)$.
        *   Or rewritten as $\frac{1}{2}(e^{i\pi/4}|0\rangle|0\rangle + e^{-i\pi/4}|0\rangle|1\rangle + e^{-i\pi/4}|1\rangle|0\rangle + e^{i\pi/4}|1\rangle|1\rangle)$.
        *   Wait, let's group by q[0]:
            *   $|0\rangle_0 \otimes \frac{1}{2}(e^{i\pi/4}|0\rangle_1 + e^{-i\pi/4}|1\rangle_1)$
            *   $|1\rangle_0 \otimes \frac{1}{2}(e^{-i\pi/4}|0\rangle_1 + e^{i\pi/4}|1\rangle_1)$
        *   Actually, the whole thing is $R_z(\pi/2)$ on q[0] applied to $|++\rangle$? No.
        *   Let's re-evaluate carefully.
        *   Initial: $|00\rangle$
        *   H,H: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
        *   CNOT(0,1): $\frac{1}{2}(|00\rangle + |01\r

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': '2-qubit QAOA layer'}

## isqTrain/466

- task_id: `isqTrain/466`
- task_type: `code_generation`
- category: `quantum_simulation`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1704`

### Prompt

I need an isQ program to implements the gate_decomposition pattern. Include explicit identity operations in the circuit (H-H pair before M(anc[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program that implements a swap (three-CNOT decomposition) test with gate decomposition patterns and explicit identity operations (H-H pairs).

Let me analyze the circuit:

1. **Goal**: Implement a swap (three-CNOT decomposition) test to compare |0⟩ and |1⟩ states, with explicit H-H pairs demonstrating gate cancellation awareness.

2. **Qubits needed**: 
   - anc[1]: ancilla qubit for the swap (three-CNOT decomposition) test
   - state1[1]: first state qubit (initialized to |0⟩)
   - state2[1]: second state qubit (initialized to |1⟩ via X gate)
   - Only anc[0] is measured

3. **Step-by-step state evolution**:

Initial state: |000⟩ (anc, state1, state2)

After X(state2[0]): |001⟩

After H(anc[0]): (|0⟩ + |1⟩)/√2 ⊗ |01⟩ = (|001⟩ + |101⟩)/√2

Cswap (three-CNOT decomposition) decomposition:
- CNOT(state2, state1): swaps the two state qubits when they're different
  - |001⟩ → |011⟩
  - |101⟩ → |111⟩
  State: (|011⟩ + |111⟩)/√2

- Toffoli(anc, state1, state2): controlled-swap (three-CNOT decomposition) when anc is |1⟩
  - |011⟩ stays |011⟩
  - |111⟩ → |101⟩
  State: (|011⟩ + |101⟩)/√2

- CNOT(state2, state1):
  - |011⟩ → |001⟩
  - |101⟩ → |111⟩
  State: (|001⟩ + |111⟩)/√2

Wait, let me reconsider. The Cswap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)) swaps state1 and state2 when anc is |1⟩.

Standard decomposition of Cswap (three-CNOT decomposition) using CNOTs and Toffoli:
Cswap (three-CNOT decomposition)(c, a, b) = CNOT(b, a) → Toffoli(c, a, b) → CNOT(b, a)

Let me redo this more carefully:

Initial state: |000⟩ (anc=0, state1=0, state2=0)

After X(state2): |001⟩ (state2 = |1⟩)

After H(anc): (|0⟩ + |1⟩)/√2 ⊗ |01⟩ = (|001⟩ + |101⟩)/√2

Now Cswap (three-CNOT decomposition) (controlled by anc, swaps state1 and state2):

Step 1: CNOT(state2, state1)
- |001⟩ → |011⟩ (state1 becomes 1 because state2 is 1)
- |101⟩ → |111⟩
State: (|011⟩ + |111⟩)/√2

Step 2: Toffoli(anc, state1, state2)
- This flips state2 when both anc AND state1 are |1⟩
- |011⟩: anc=0, so no flip → |011⟩
- |111⟩: anc=1, state1=1, so flip state2 → |110⟩
State: (|011⟩ + |110⟩)/√2

Step 3: CNOT(state2, state1)
- |011⟩: state2=1, so flip state1 → |001⟩
- |110⟩: state2=0, so no flip → |110⟩
State: (|001⟩ + |110⟩)/√2

After H(anc):
- |001⟩ → (|001⟩ + |101⟩)/√2
- |110⟩ → (|110⟩ - |010⟩)/√2

Total: (|001⟩ + |101⟩ + |110⟩ - |010⟩)/2

Now H-H-H on anc:
- H∘H = I, so H∘H∘H = H

After first H(anc):
- |001⟩ → (|001⟩ + |101⟩)/√2
- |110⟩ → (|110⟩ - |010⟩)/√2

After second H(anc): back to before first H
State: (|001⟩ + |110⟩)/√2

After third H(anc):
- |001⟩ → (|001⟩ + |101⟩)/√2
- |110⟩ → (|110⟩ - |010⟩)/√2

Final state: (|001⟩ + |101⟩ + |110⟩ - |010⟩)/2

Let's trace out state1 and state2 to get ancilla state:
- anc=0 terms: |001⟩, |010⟩ → coefficients 1/2 and -1/2
- anc=1 terms: |

## isqTrain/470

- task_id: `isqTrain/470`
- task_type: `output_prediction`
- category: `quantum_simulation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5717`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

qbit q[2]; // control, target

procedure CRX_decomp(double theta, qbit c, qbit t) {
    // CRx(theta) decomposition
    Rz(pi/2.0, t);
    Ry(theta/2.0, t);
    CNOT(c, t);
    Ry(-theta/2.0, t);
    CNOT(c, t);
    Rz(-pi/2.0, t);
}

procedure main() {
    X(q[0]);
    CRX_decomp(pi/2.0, q[0], q[1]);
    
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ program**:
    *   2 qubits: `q[0]` (control), `q[1]` (target).
    *   Initial state: `|00>`.
    *   `X(q[0])`: Flips `q[0]` to `|1>`. State becomes `|10>`.
    *   `CRX_decomp(pi/2.0, q[0], q[1])`: Applies a Controlled-Rx gate with angle $\pi/2$. Let's verify the decomposition.
        *   `Rz(pi/2, t)`
        *   `Ry(pi/4, t)`
        *   `CNOT(c, t)`
        *   `Ry(-pi/4, t)`
        *   `CNOT(c, t)`
        *   `Rz(-pi/2, t)`
        Wait, let's trace this or recognize it. The standard CRx decomposition is:
        $Ry(\theta/2) \cdot CNOT \cdot Ry(-\theta/2) \cdot CNOT$ is actually $CRx(\theta)$ (up to global phase or single qubit corrections). Let's check the exact effect.
        Actually, $CRx(\theta)$ when control is |1> applies $Rx(\theta)$ on target.
        $Rx(\theta) = e^{-i\theta/2 X} = \cos(\theta/2) I - i \sin(\theta/2) X$.
        Here $\theta = \pi/2$.
        So $Rx(\pi/2) = \frac{1}{\sqrt{2}} I - i \frac{1}{\sqrt{2}} X = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -i \\ -i & 1 \end{pmatrix}$.
        Wait, standard $Rx(\pi/2)$ matrix is $\begin{pmatrix} \cos(\pi/4) & -i\sin(\pi/4) \\ -i\sin(\pi/4) & \cos(\pi/4) \end{pmatrix} = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -i \\ -i & 1 \end{pmatrix}$.
        Since the control is $|1\rangle$, the target `q[1]` (initially $|0\rangle$) will undergo $Rx(\pi/2)$.
        State of target: $Rx(\pi/2)|0\rangle = \cos(\pi/4)|0\rangle - i\sin(\pi/4)|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$.
        Therefore, the 2-qubit state becomes $|1\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle) = \frac{1}{\sqrt{2}} (|10\rangle - i|11\rangle)$.
    *   Let's double check the `CRX_decomp` to ensure it is exactly $CRx(\pi/2)$ without weird phase shifts that aren't relative.
        The state $\frac{1}{\sqrt{2}}(|10\rangle - i|11\rangle)$ has probabilities 0.5 for $|10\rangle$ and 0.5 for $|11\rangle$. The prompt asks for probability distribution. Expected outcome is `{|10>: 0.5, |11>: 0.5}`.

2.  **Step-by-step evolution**:
    *   **Initial state**: $|00\rangle$
    *   **After X(q[0])**: $X \otimes I |00\rangle = |10\rangle$
    *   **Apply CRX_decomp(pi/2, q[0], q[1])**:
        *   Because the control `q[0]` is in state $|1\rangle$, the CNOT gates effectively act as X gates on the target `q[1]` when the target is active, but more simply, we can just track the target's state under the effective single-qubit unitary conditioned on the control being 1.
        *   Wait, let's trace exactly to be safe:
        *   State is $|1\rangle_c |0\rangle_t$.
        *   $Rz(\pi/2)|0\rangle = |0\rangle$
        *   $Ry(\pi/4)|0\rangle = \cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle$
        *   CNOT(c, t): Since $c=|1\r

### Reference answer

{'predicted_probs': {'2': 0.5, '3': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/133. Dimension: predict probabilities for reference circuit.'}

## isqTrain/461

- task_id: `isqTrain/461`
- task_type: `code_generation`
- category: `quantum_simulation`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3005`

### Prompt

Create an isQ quantum circuit that implements a variant of the gate_decomposition pattern using state2[1] -> state2[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the isQ quantum program shown In the implementation. Let me analyze this circuit:

1. **Goal**: This is a swap (three-CNOT decomposition) test circuit that compares two quantum states, in this case |0⟩ and |1⟩.

2. **Qubits**:
   - `anc[0]` - ancilla qubit for the swap (three-CNOT decomposition) test (measured)
   - `state1[0]` - holds one state
   - `state2[0], state2[1]` - expanded register (2 qubits), but only state2[0] is used

3. **State evolution**:
   - Initial: |000⟩ (anc, state1[0], state2[0])
   - After X(state2[0]): |010⟩ - prepares |1⟩ on state2[0]
   - After H(anc[0]): (|0⟩+|1⟩)/√2 ⊗ |10⟩ = (|010⟩+|110⟩)/√2
   - Cswap (three-CNOT decomposition) implementation:
     - First CNOT(state2[0], state1[0]): swaps information, state becomes (|110⟩+|010⟩)/√2... wait, let me be more careful
     
Let me trace through more carefully:

Initial state: |anc⟩|state1⟩|state2⟩ = |000⟩

After X(state2[0]): |010⟩

After H(anc[0]): (1/√2)(|010⟩ + |110⟩)

Now the Cswap (three-CNOT decomposition) part:
- CNOT(state2[0], state1[0]): If state2[0]=1, flip state1[0]
  - |010⟩ → |010⟩ (state2[0]=0, no flip)
  - |110⟩ → |100⟩ (state2[0]=1, flip state1[0])
  - Result: (1/√2)(|010⟩ + |100⟩)

- Toffoli(anc[0], state1[0], state2[0]): If anc=1 AND state1=1, flip state2
  - |010⟩ → |010⟩ (anc=0)
  - |100⟩ → |110⟩ (anc=1, state1=0, no flip)
  
Wait, that's not right. Let me re-check. In the Toffoli, the first two are controls and the third is the target.
- For |010⟩: anc=0, so no flip → |010⟩
- For |100⟩: anc=1, state1[0]=0, so no flip → |100⟩

Hmm, that doesn't seem like a proper Cswap (three-CNOT decomposition). Let me think about this Cswap (three-CNOT decomposition) decomposition again.

Actually, looking at the code more carefully:

This is actually implementing a controlled-swap (three-CNOT decomposition) where anc is the control. The standard decomposition of Cswap (three-CNOT decomposition) uses:
1. CNOT(target2, target1) - swaps in one direction
2. Toffoli(control, target1, target2) - conditional swap
3. CNOT(target2, target1) - completes the swap

Let me trace again:

Initial for this part: (1/√2)(|010⟩ + |110⟩) where order is anc, state1, state2

After CNOT(state2[0], state1[0]): 
- |010⟩: state2=0, no flip state1 → |010⟩
- |110⟩: state2=1, flip state1 → |100⟩
Result: (1/√2)(|010⟩ + |100⟩)

After Toffoli(anc[0], state1[0], state2[0]):
- |010⟩: anc=0, no action → |010⟩
- |100⟩: anc=1, state1=0, no action → |100⟩
Result: (1/√2)(|010⟩ + |100⟩)

Hmm, this doesn't seem right. Let me look up the Cswap (three-CNOT decomposition) decomposition again.

Actually, I think I may have the decomposition wrong. Let me think about what a proper Cswap (three-CNOT decomposition)(c; a, b) does:
- If c=1, swap a and b
- If c=0, do nothing

The standard decomposition is:
1. CNOT(b, a)
2. Toffoli(c, a, b)
3. CNOT(b, a)

Let's verify with c=anc, a=state1, b=state2:

If anc=0:
- Start with |0⟩|ψ⟩|φ⟩
-

## isqTrain/1966

- task_id: `isqTrain/1966`
- task_type: `output_prediction`
- category: `quantum_simulation`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4216`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];
procedure XX_evolve(double theta, qbit a, qbit b) {
    H(a); H(b);
    CNOT(a, b);
    Rz(theta, b);
    CNOT(a, b);
    H(a); H(b);
}
procedure main() {
    X(q[0]);
    XX_evolve(pi/4.0, q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, step-by-step analysis of an isQ quantum program, predicting its measurement probability distribution. The output must be strictly in the specified format, starting with "## Circuit Analysis" and ending with the probability distribution.

2.  **Analyze the isQ Code:**
    *   `qbit q[2];`: Two qubits initialized to $|00\rangle$.
    *   `main`:
        *   `X(q[0]);`: Apply X gate to qubit 0. State becomes $|10\rangle$ (where $q_0$ is the left bit/higher bit if considered standard, but isQ uses little-endian or standard notation? Let's trace carefully. isQ usually refers to `q[0]` as the 0th qubit. If measured as `M(q[0]); M(q[1]);`, standard bitstring is $q_0 q_1$ or $q_1 q_0$. Let's look at the predicted output: `{'01': 0.1464, '10': 0.8536}`. If $q[0]$ is the higher bit, `M(q[0])` is bit 1, `M(q[1])` is bit 0.
    *   `XX_evolve`:
        *   `H(a); H(b);`: H on $q_0$, H on $q_1$.
        *   `CNOT(a, b);`: CNOT($q_0$, $q_1$)
        *   `Rz(theta, b);`: Rz($\pi/4$, $q_1$)
        *   `CNOT(a, b);`: CNOT($q_0$, $q_1$)
        *   `H(a); H(b);`: H on $q_0$, H on $q_1$

3.  **Step-by-Step State Evolution:**
    *   Initial: $|00\rangle$
    *   `X(q[0])`: $|10\rangle$
    *   `H(q[0])`, `H(q[1])`:
        *   $|10\rangle \xrightarrow{H_0} \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$ -- Wait, H on |1> is $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. Let me use exact math.
        *   $|1\rangle_0 |0\rangle_1 \xrightarrow{H_0} \frac{|0\rangle - |1\rangle}{\sqrt{2}} |0\rangle_1 \xrightarrow{H_1} \frac{(|0\rangle - |1\rangle)}{\sqrt{2}} \frac{(|0\rangle + |1\rangle)}{\sqrt{2}} = \frac{1}{2} (|00\rangle + |01\rangle - |10\rangle - |11\rangle)$
    *   `CNOT(q[0], q[1])`:
        *   $\frac{1}{2} (|00\rangle + |01\rangle - |11\rangle - |10\rangle)$
        *   $= \frac{1}{2} (|00\rangle + |01\rangle - |10\rangle - |11\rangle)$ (since CNOT flips $q_1$ when $q_0$ is 1. So $|10\rangle \to |11\rangle$ and $|11\rangle \to |10\rangle$)
    *   `Rz(\pi/4, q[1])`:
        *   Rz applies $e^{-i\theta/2}$ to $|0\rangle$ and $e^{i\theta/2}$ to $|1\rangle$ for the target qubit.
        *   Wait, standard isQ Rz gate: $R_z(\theta) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\theta} \end{pmatrix}$ or $e^{-i\theta/2}|0\rangle\langle0| + e^{i\theta/2}|1\rangle\langle1|$? Usually $R_z(\theta) = |0\rangle\langle0| + e^{i\theta}|1\rangle\langle1|$. Let's assume $|1\rangle \to e^{i\theta}|1\rangle$ up to global phase. Let's check standard isQ. Standard isQ Rz applies $e^{-i\theta Z/2} = \begin{pmatrix} e^{-

### Reference answer

{'predicted_probs': {'01': 0.1464, '10': 0.8536}, 'explanation': 'XX interaction'}

## isqTrain/2602

- task_id: `isqTrain/2602`
- task_type: `code_equivalence`
- category: `quantum_simulation`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_arrays`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4600`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;

qbit q[2]; 

procedure XY_evolve(double theta, qbit a, qbit b) {
    // XY interaction = iSWAP ^ (2 * theta / pi)
    // Decomposed using basic gates
    H(a); H(b);
    S(a); S(b);
    H(a);
    CNOT(a, b);
    Ry(-theta/2.0, a);
    Ry(-theta/2.0, b);
    CNOT(a, b);
    H(a);
    inv S(a); inv S(b);
    H(a); H(b);
}

procedure main() {
    X(q[0]);
    XY_evolve(pi/2.0, q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

Program B:
```isq
import std;

qbit q[2]; 

procedure XY_evolve(double theta, qbit a, qbit b) {
    // XY interaction = iSWAP ^ (2 * theta / pi)
    // Decomposed using basic gates
    H(a); H(b);
    S(a); S(b);
    H(a);
    CNOT(a, b);
    Ry(-theta/2.0, a);
    Ry(-theta/2.0, b);
    CNOT(a, b);
    H(a);
    inv S(a); inv S(b);
    H(a); H(b);
}

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[0]);
    XY_evolve(pi/2.0, q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A:** Initializes |00⟩, applies X(q[0]) to get |10⟩, then applies XY_evolve(π/2) (an XY interaction equivalent to iSWAP (custom gate)) on q[0] and q[1], followed by measurement of both qubits.

2. **Program B:** Same as Program A, but inserts `GPhase(0.0)` before the X gate. This applies a global phase factor of e^(i·0) = 1, which is the identity.

3. **Key difference:** Program B contains the additional `GPhase(0.0)` operation. However, GPhase(0.0) multiplies the entire quantum state by 1 (no phase shift), making it a trivial no-op.

4. **Measurement probabilities:** Both programs produce identical quantum states before measurement. Even a nonzero global phase would not affect measurement probabilities, but here the phase is exactly zero, so there is zero difference.

5. **Verdict: Equivalent: Yes**

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/462

- task_id: `isqTrain/462`
- task_type: `code_generation`
- category: `quantum_simulation`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1879`

### Prompt

Write an isQ program that implements a variant of the gate_decomposition pattern using anc[1] -> anc[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The task asks me to generate a reasoning section for the provided isQ program that implements a variant of gate_decomposition pattern using anc[1] -> anc[3].

Let me analyze the given isQ code:

1. **Goal**: This circuit implements a swap (three-CNOT decomposition) test to compare |0⟩ and |1⟩ states

2. **Qubits**: 
   - `anc[3]` - ancilla qubits (3 qubits, anc[0], anc[1], anc[2])
   - `state1[1]` - first state qubit
   - `state2[1]` - second state qubit
   - Total: 5 qubits
   - Measured: anc[0], anc[1], anc[2] (3 qubits measured)

3. **Step-by-step evolution**:
   - Initial state: |00000⟩ (anc[0], anc[1], anc[2], state1[0], state2[0])
   - `X(state2[0])`: Flips state2[0] to |1⟩ → |00001⟩
   - Now state1 = |0⟩ and state2 = |1⟩
   - `H(anc[0])`: Creates superposition on anc[0] → (|0⟩ + |1⟩)/√2 ⊗ |00⟩ ⊗ |0⟩ ⊗ |1⟩ = (|00001⟩ + |10001⟩)/√2
   - Cswap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)) - controlled by anc[0], swaps state1 and state2:
     - `CNOT(state2[0], state1[0])`: state1 ⊕ state2 → |00011⟩ or |10011⟩ (state1 becomes 1)
     - `Toffoli(anc[0], state1[0], state2[0])`: If anc[0]=1 AND state1[0]=1, flip state2[0]
       - For |00011⟩: anc[0]=0, no flip → |00011⟩
       - For |10011⟩: anc[0]=1 AND state1[0]=1, flip state2[0] → |10001⟩
     - `CNOT(state2[0], state1[0])`: Uncompute state1
       - For |00011⟩: state1 ⊕ state2 = 1 ⊕ 1 = 0 → |00001⟩
       - For |10001⟩: state1 ⊕ state2 = 1 ⊕ 0 = 1 → ... wait, let me recalculate
     
   Let me be more careful. The Cswap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) gate swaps the target qubits when the control is |1⟩.
   
   Starting after H(anc[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ ⊗ |0⟩ ⊗ |0⟩ ⊗ |1⟩
   
   But wait, I had 5 qubits: anc[0], anc[1], anc[2], state1[0], state2[0]
   
   Let me label them as: q0=anc[0], q1=anc[1], q2=anc[2], q3=state1[0], q4=state2[0]
   
   Initial: |00000⟩
   X(q4): |00001⟩ - now state1=|0⟩, state2=|1⟩
   H(q0): (|00001⟩ + |10001⟩)/√2
   
   Cswap (three-CNOT decomposition) implementation:
   - CNOT(q4, q3): q3 ← q3 ⊕ q4
     - |00001⟩ → q3=0⊕1=1 → |00011⟩
     - |10001⟩ → q3=0⊕1=1 → |10011⟩
   
   - Toffoli(q0, q3, q4): If q0=1 AND q3=1, flip q4
     - |00011⟩: q0=0, no flip → |00011⟩
     - |10011⟩: q0=1 AND q3=1, flip q4: 1→0 → |10001⟩
   
   - CNOT(q4, q3): q3 ← q3 ⊕ q4
     - |00011⟩: q3=1⊕1=0 → |00001⟩
     - |10001⟩: q3=1⊕0=1 → |10011⟩
   
   Hmm, this doesn't seem right. The Cswap (three-CNOT decomposition) should swap state1 and state2 when anc[0]=|1⟩.
   
   Let me think again about the Cswap (three-CNOT decomposition) decomposition. A controlled-swap operation (three-CNOT decomposition) (Cswap (three-CNOT decomposition)) with control c

## isqTrain/463

- task_id: `isqTrain/463`
- task_type: `code_generation`
- category: `quantum_simulation`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_multi_register`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4186`

### Prompt

用isQ实现implements a variant of the gate_decomposition pattern using state1[1] -> state1[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this task. I need to write a reasoning section for an isQ program that implements a variant of the gate_decomposition pattern using state1[1] -> state1[3]. The circuit should use a significantly expanded qubit register.

Analyzing the circuit requirements:
- It uses `qbit anc[1]`, `qbit state1[3]`, `qbit state2[1]`
- The swap (three-CNOT decomposition) test is comparing |0> and |1>
- It applies X to state2[0] to create |1>
- Then performs a swap (three-CNOT decomposition) test using anc as the control qubit

The task asks for "state1[1] -> state1[3]", meaning we need to expand state1 from size 1 to size 3 (actually, Analyzing the, it's already state1[3]).

Wait, let me re-read. The reference shows state1[3] already. The task says "using state1[1] -> state1[3]" which means expanding from 1 qubit to 3 qubits for state1.

The implementation already has state1[3] with 3 qubits. The additional qubits (state1[1] and state1[2]) are left in the ground state |0>.

Let me trace through the circuit:

1. Initial state: |0>_anc ⊗ |000>_state1 ⊗ |0>_state2 = |00000>

2. After X(state2[0]): |0>_anc ⊗ |000>_state1 ⊗ |1>_state2

3. After H(anc[0]): (|0> + |1>)/√2 ⊗ |000> ⊗ |1>

4. The Cswap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) is built using:
   - CNOT(state2[0], state1[0]) - flips state1[0] if state2[0]=1
   - Toffoli(anc[0], state1[0], state2[0]) - flips state2[0] if anc[0]=1 AND state1[0]=1
   - CNOT(state2[0], state1[0]) - flips state1[0] if state2[0]=1
   
   This implements a controlled-swap (three-CNOT decomposition) with anc[0] as control, swapping state1[0] and state2[0].

5. After the Cswap (three-CNOT decomposition), when anc[0]=|1>, the states of state1[0] and state2[0] are swapped.

6. After the final H(anc[0]), we get interference.

Let me trace more carefully:

Initial: |0>_anc |000>_state1 |0>_state2

After X(state2[0]): |0>_anc |000>_state1 |1>_state2

After H(anc[0]): (|0> + |1>)/√2 |000> |1>
= (|0,000,1> + |1,000,1>)/√2

Now the Cswap (three-CNOT decomposition):
When anc=0: no swap, so state1[0]=|0>, state2[0]=|1>
When anc=1: swap state1[0] and state2[0], so state1[0]=|1>, state2[0]=|0>

After Cswap (three-CNOT decomposition): (|0,000,1> + |1,100,0>)/√2

Wait, I need to track the order of qubits more carefully. Let me use the order: anc, state1[0], state1[1], state1[2], state2[0]

After X(state2[0]): |0,0,0,0,1>

After H(anc[0]): (|0,0,0,0,1> + |1,0,0,0,1>)/√2

Now the Cswap (three-CNOT decomposition) sequence:
1. CNOT(state2[0], state1[0]): control=state2[0], target=state1[0]
   - When state2[0]=1, flip state1[0]
   - |0,0,0,0,1> → |0,1,0,0,1>
   - |1,0,0,0,1> → |1,1,0,0,1>
   So: (|0,1,0,0,1> + |1,1,0,0,1>)/√2

2. Toffoli(anc[0], state1[0], state2[0]): flip state2[0] when anc=1 AND state1[0]=1
   - |0,1,0,0,1> → |0,1,0,0,1> (anc=

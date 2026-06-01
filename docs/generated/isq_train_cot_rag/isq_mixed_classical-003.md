# ISQ training COT RAG corpus: isq_mixed_classical shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1976

- task_id: `isqTrain/1976`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4895`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[1];
procedure main() {
    X2P(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit, q[0], in the ground state |0>.
2. The `X2P` gate applies an Rx(π/2) rotation to the qubit.
3. The quantum state evolves from |0> to (1/√2)|0> - (i/√2)|1>.
4. Measuring this superposition state in the computational basis yields equal probabilities for both outcomes.

Predicted probability distribution: {'0': 0.5, '1': 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'X2P gate (= Rx(π/2)) creates equal superposition. P(|0⟩) ≈ P(|1⟩) ≈ 0.5.'}

## isqTrain/519

- task_id: `isqTrain/519`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1939`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    S(q[0]);
    S(q[0]);
    H(q[0]);
    M(q[0]); // + -> SS -> - -> H -> 1. Should be 100% 1
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The qubit q[0] is initialized to the basis state |0>.
2. The first H gate creates an equal superposition: H|0> = |+> = (1/√2)(|0> + |1>).
3. The two consecutive S gates apply a phase of i twice to the |1> component, equivalent to a Z gate (S² = Z): Z|+> = |-> = (1/√2)(|0> - |1>).
4. The final H gate transforms the |-> state back to a basis state: H|-> = |1>.
5. The circuit deterministically prepares the |1> state.

Predicted probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/150. Dimension: predict probabilities for reference circuit.'}

## isqTrain/431

- task_id: `isqTrain/431`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_if_else`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `1198`

### Prompt

Write an isQ program that implements a variant of the gate_decomposition pattern using c[1] -> c[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The task asks me to write a reasoning section for an isQ program that:
1. Implements a variant of the gate_decomposition pattern using c[1] -> c[3]
2. Uses a significantly expanded qubit register compared to the base version
3. Additional qubits should be left in the ground state
4. Expected measurement probabilities: {|0001>: 0.5, |1001>: 0.5}
5. Number of qubits measured: 4

Analyzing the circuit requirements:
- It has c[3], q[1] - so 4 qubits total
- It applies H to c[0], creating superposition
- Measures c[0], c[1], c[2] (c[1] and c[2] are in |0> state)
- If x==1 (c[0] was |1>), applies X to q[0]
- Measures q[0]

Wait, The implementation already measures 4 qubits: c[0], c[1], c[2], q[0]. And the predicted outputs are |0001> and |1001>.

But the task says "variant using c[1] -> c[3]" and "significantly expanded qubit register". This seems like I need to modify the reference to use a different control qubit and have more qubits.

Let me re-read: "Write an isQ program that implements a variant of the gate_decomposition pattern using c[1] -> c[3]."

Hmm, this could mean:
1. Use c[1] instead of c[0] for the Hadamard
2. Or use c[3] as part of the circuit
3. Or expand the register

The "significantly expanded qubit register" suggests we need more qubits than the reference (which has 4). Perhaps c[6] or c[8] with some qubits too.

But the expected measurement probabilities are still {|0001>: 0.5, |1001>: 0.5} with 4 qubits measured. So the additional qubits remain unmeasured and in ground state.

Actually, looking more carefully at the predicted output: |0001> and |1001>. This is 4 bits. The highest bit changes (0 or 1), and the last bit is always 1.

In the reference:
- c[0] is measured first (highest bit in measurement string)
- c[1], c[2] are measured (should be 0)
- q[0] is measured last (lowest bit)

After H(c[0]): superposition of |0> and |1>
If c[0] measures as 1, X is applied to q[0], flipping it to |1>
If c[0] measures as 0, q[0] stays |0>

Wait, but The predicted output q[0] is always 1 (|0001> and |1001>). That means q[0] ends up as |1> regardless of the measurement of c[0].

Let me re-analyze the:

Actually, q[0] starts in |0>. If x==1, X flips it to |1>. If x==0, it stays |0>.

So the predicted outputs should be:
- |0000> with prob 0.5 (when x=0: c[0]=0, c[1]=0, c[2]=0, q[0]=0)
- |1001> with prob 0.5 (when x=1: c[0]=1, c[1]=0, c[2]=0, q[0]=1)

But the expected given is {|0001>: 0.5, |1001>: 0.5}. This suggests q[0] is always |1>.

Hmm, perhaps there's an initial X on q[0] that I'm missing, or the "variant" changes something.

Actually wait - the task is asking me to generate REASONING for a program, not the program itself. The program should match the predicted output.

Let me reconsider: if the expected is {|0001>: 0.5, |1001>: 0.5}, then:
- c[0] can be 0 or 1 with equal probability (from H gate)
- c[1], c[2] should be 0 (ground state)
- q[0] should be 1 always

So maybe the variant applies H to a different qubit (like c[3] instead of c[0]), and we need to adjust accordingly.

Let me think about what "

## isqTrain/2611

- task_id: `isqTrain/2611`
- task_type: `code_equivalence`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `entanglement`, `global_phase`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `795`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[1];
procedure main() {
    // U3 for H is U3(pi/2, 0, pi) -> wait, H is U3(pi/2, 0, pi)
    U3(pi/2.0, 0.0, pi, q[0]);
    M(q[0]); // should be 50/50
}

```

Version B:
```isq
import std;
qbit q[1];
procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // U3 for H is U3(pi/2, 0, pi) -> wait, H is U3(pi/2, 0, pi)
    U3(pi/2.0, 0.0, pi, q[0]);
    M(q[0]); // should be 50/50
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes a qubit in |0> and applies the gate `U3(pi/2, 0, pi)`, which is exactly equivalent to the Hadamard (H) gate. This maps the state to |+>, resulting in a 50/50 measurement probability.
2. **Program B** performs the exact same operations, applying the Hadamard gate via `U3(pi/2, 0, pi)` to a |0> qubit.
3. The only difference is the addition of `GPhase(0.0)` in Program B. A global phase of 0 radians corresponds to a multiplication by $e^{i0} = 1$, which acts as an identity operation.
4. The measurement probability distributions are exactly the same because `GPhase(0.0)` introduces no observable change to the quantum state.
5. Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/2609

- task_id: `isqTrain/2609`
- task_type: `code_equivalence`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `global_phase`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1946`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[1];
procedure main() {
    X2P(q[0]);
    M(q[0]); // Rx(pi/2) -> 50/50
}

```

程序B：
```isq
import std;
qbit q[1];
procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X2P(q[0]);
    M(q[0]); // Rx(pi/2) -> 50/50
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A** initializes $q[0]$ to $|0\rangle$ and applies the `X2P` gate, which corresponds to an $R_x(\pi/2)$ rotation. This evolves the state to $\frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$, resulting in a 50/50 measurement probability distribution.
2. **Program B** initializes $q[0]$ to $|0\rangle$, applies `GPhase(0.0)`, and then applies the exact same `X2P` gate.
3. The only difference between the two programs is the `GPhase(0.0)` operation in Program B, which applies a global phase factor of $e^{i0} = 1$.
4. The `GPhase(0.0)` gate is mathematically an identity operation, leaving the quantum state completely unchanged. Both programs produce the identical state $\frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$ right before measurement.
5. Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/449

- task_id: `isqTrain/449`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3502`

### Prompt

实现以下量子计算任务（使用isQ）：implements the phase_kickback pattern with modified rotation parameters (pi2_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Looking at this problem, I need to understand what's being asked and explain the phase kickback circuit with modified rotation parameters.

the predicted output probabilities are:
- |10>: 0.8535533905932738
- |11>: 0.1464466094067262

Let me think about what circuit would produce these probabilities.

The implementation is an Iterative Phase Estimation (IPE) circuit for phase 1/4 of the S gate. But the predicted output don't match The implementation (which would give |10> with probability 1 for eigenstate |1> of S).

Wait, the task says "phase_kickback pattern with modified rotation parameters (pi2_to_pi4)". This suggests we need to change pi/2 angles to pi/4 angles.

Looking at the predicted output:
- P(|10>) = 0.8535533905932738 ≈ (1 + 1/√2)/2 ≈ cos²(π/8)
- P(|11>) = 0.1464466094067262 ≈ (1 - 1/√2)/2 ≈ sin²(π/8)

These look like probabilities from a rotation of π/4 (or π/8 in some context).

Let me think about a simpler phase kickback circuit:

1. Start with ancilla in |+> and target in |1> (eigenstate of some unitary)
2. Apply controlled-U
3. Measure ancilla in X basis

For a phase kickback with controlled-Rz(θ):
- ancilla |0>, target |1>
- H on ancilla → (|0> + |1>)/√2 ⊗ |1>
- CNOT or controlled-Rz: if controlled-Rz(π/4), this gives (|0>|1> + e^(iπ/4)|1>|1>)/√2
- H on ancilla: results in measurement probabilities depending on the phase

Actually, let me reconsider. the predicted output suggest a simpler 2-qubit circuit.

For a phase kickback demonstration:
- ancilla |0>, u |0>
- X(u) to make u = |1>
- H(ancilla) → |+>|1>
- controlled-S on (ancilla, u) → (|0>|1> + i|1>|1>)/√2 = (|0> + i|1>)/√2 ⊗ |1>
- H(ancilla) → measurement gives P(0) = |1+i|²/4 = (1+cos(π/2))/2 = 1/2... hmm

Let me think about pi2_to_pi4 modification. The S gate has phase π/2, T gate has phase π/4. So we might replace S with T.

With controlled-T instead of controlled-S:
- |+>|1> → (|0> + e^(iπ/4)|1>)/√2 ⊗ |1>
- H on ancilla:
  - |0> → (|0> + |1>)/√2
  - |1> → (|0> - |1>)/√2
  - Result: (1/√2)[(|0>+|1>)/√2 + e^(iπ/4)(|0>-|1>)/√2]
  - = (1/2)[(1+e^(iπ/4))|0> + (1-e^(iπ/4))|1>]
  - P(|0>anc) = |1+e^(iπ/4)|²/4 = (1 + cos(π/4))/2 ≈ 0.8536
  - P(|1>anc) = |1-e^(iπ/4)|²/4 = (1 - cos(π/4))/2 ≈ 0.1464

Yes! These match the predicted output.

So the circuit is:
1. X(u[0]) - prepare eigenstate |1>
2. H(anc0[0]) - put ancilla in superposition
3. ctrl T(anc0[0], u[0]) - phase kickback with T gate (π/4 phase)
4. H(anc0[0]) - measure in X basis
5. M(anc0[0]) and M(u[0])

Wait, but measuring u[0] which is in |1> state... The measurement results should be:
- anc0=1, u=0 → |10> (in the output format where earlier measured = higher bit)
- anc0=1, u=1 → |11>

Actually Let me verify the output format. "--probs output: array indexed by measurement bitstring

## isqTrain/454

- task_id: `isqTrain/454`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `825`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

qbit q[1]; 

procedure main() {
    // Using a while loop to perform classical setup before quantum operations.
    // e.g., Finding gcd of 15 and 10 to prepare Rz(pi/gcd) state.
    int a = 15;
    int b = 10;
    while (b != 0) {
        int temp = b;
        a = a % b;
        b = temp;
        
        // Swap a and b if needed (mod assigns remainder to a directly)
        // Actually a % b makes a the remainder. So next iter b=a_old%b_old, a=temp
        temp = a;
        a = b;
        b = temp;
    }
    // a is GCD = 5
    // Apply Rz(pi/a)
    X(q[0]);
    H(q[0]);
    // Apply phase
    Rz(pi / a, q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ Program:**
    *   Classical part:
        *   `a = 15`, `b = 10`
        *   Loop:
            *   Iter 1: `temp = 10`, `a = 15 % 10 = 5`, `b = 10`. Then swap: `temp = 5`, `a = 10`, `b = 5`.
            *   Iter 2: `temp = 5`, `a = 10 % 5 = 0`, `b = 5`. Then swap: `temp = 0`, `a = 5`, `b = 0`.
        *   Loop ends. `a = 5`.
    *   Quantum part:
        *   Start with `q[0]` in `|0>`.
        *   `X(q[0])`: Applies Pauli-X gate. State becomes `|1>`.
        *   `H(q[0])`: Applies Hadamard gate. State becomes `|-> = 1/sqrt(2) (|0> - |1>)`.
        *   `Rz(pi / a, q[0])` where `a = 5`. `Rz(pi/5, q[0])`.
            *   Wait, $R_z(\theta) = e^{-i\theta/2} |0\rangle\langle 0| + e^{i\theta/2} |1\rangle\langle 1|$.
            *   Or standard definition: $|0\rangle \to |0\rangle$, $|1\rangle \to e^{i\theta} |1\rangle$.
            *   Let's check standard isQ convention. It usually maps $|0\rangle \to |0\rangle$, $|1\rangle \to e^{i\theta} |1\rangle$.
            *   State before Rz: $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
            *   After Rz($\pi/5$): $\frac{1}{\sqrt{2}}(|0\rangle - e^{i\pi/5} |1\rangle)$. (Up to global phase).
            *   Actually, global phase doesn't matter for probabilities, but relative phase does. Let's trace it carefully.
            *   State: $|\psi\rangle = \frac{1}{\sqrt{2}}|0\rangle - \frac{e^{i\pi/5}}{\sqrt{2}}|1\rangle$.
        *   `H(q[0])`: Applies Hadamard again.
            *   $H|\psi\rangle = \frac{1}{\sqrt{2}} (H|0\rangle - e^{i\pi/5} H|1\rangle)$
            *   $= \frac{1}{\sqrt{2}} (\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) - \frac{e^{i\pi/5}}{\sqrt{2}}(|0\rangle - |1\rangle))$
            *   $= \frac{1}{2} [ (1 - e^{i\pi/5})|0\rangle + (1 + e^{i\pi/5})|1\rangle ]$.
    *   Measurement: Probabilities of `|0>` and `|1>`.
        *   $P(0) = \frac{1}{4} |1 - e^{i\pi/5}|^2 = \frac{1}{4} (1 - e^{i\pi/5})(1 - e^{-i\pi/5}) = \frac{1}{4} (2 - e^{i\pi/5} - e^{-i\pi/5}) = \frac{1}{4} (2 - 2\cos(\pi/5)) = \frac{1}{2} (1 - \cos(\pi/5)) = \sin^2(\pi/10)$.
        *   $P(1) = \frac{1}{4} |1 + e^{i\pi/5}|^2 = \frac{1}{4} (2 + 2\cos(\pi/5)) = \frac{1}{2} (1 + \cos(\pi/5)) = \cos^2(\pi/10)$.

2.  **Calculate the numerical values:**
    *   $\pi/10$ radians = 18 degrees.
    *   $\cos(18^\circ) = \frac{\sqrt{10 + 2\sqrt{5}}}{4}$.
    *   $\cos^2(18^\circ) = \frac

### Reference answer

{'predicted_probs': {'0': 0.09549150281252623, '1': 0.9045084971874736}, 'explanation': 'Parametric variant of isqHumanEval/130. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1959

- task_id: `isqTrain/1959`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3267`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[1];
procedure main() {
    int a = 15;
    int b = 10;
    while (b != 0) {
        int temp = b;
        a = a % b;
        b = temp;
        temp = a;
        a = b;
        b = temp;
    }
    X(q[0]);
    H(q[0]);
    Rz(pi / a, q[0]);
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Classical Logic Evaluation**: The `while` loop calculates the greatest common divisor (GCD) of 15 and 10. The variables update as follows: a=15, b=10 -> a=5, b=0. Thus, the loop terminates with `a = 5`. The quantum operation `Rz(pi / a, q[0])` becomes `Rz(pi / 5, q[0])`.
2. **Initial State**: The qubit `q[0]` starts in the state $|0\rangle$.
3. **X Gate**: Flips the qubit to $|1\rangle$.
4. **H Gate**: Puts the qubit into the $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$ state.
5. **Rz(pi / 5) Gate**: Applies a phase shift, evolving the state to $\frac{1}{\sqrt{2}}(e^{-i\pi/10}|0\rangle - e^{i\pi/10}|1\rangle)$.
6. **H Gate**: Transforms the state into $\frac{1}{\sqrt{2}}(e^{-i\pi/10} - e^{i\pi/10})|0\rangle + \frac{1}{\sqrt{2}}(e^{-i\pi/10} + e^{i\pi/10})|1\rangle$. This simplifies to $-i\sin(\frac{\pi}{10})|0\rangle + \cos(\frac{\pi}{10})|1\rangle$.
7

### Reference answer

{'predicted_probs': {'0': 0.0955, '1': 0.9045}, 'explanation': 'While loop state prep'}

## isqTrain/1977

- task_id: `isqTrain/1977`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1628`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[1];
procedure main() {
    Y2P(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with one qubit, q[0], in the initial state |0>.
2. The Y2P gate, which corresponds to an Ry(pi/2) rotation, is applied to q[0].
3. This operation rotates the state around the Y-axis, evolving the state to (1/sqrt(2))|0> + (1/sqrt(2))|1>.
4. Measuring this equal superposition state in the computational basis yields an equal chance of collapsing to either basis state.

Predicted probability distribution: {'0': 0.5, '1': 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Y2P gate (= Ry(π/2)) creates equal superposition. P(|0⟩) ≈ P(|1⟩) ≈ 0.5.'}

## isqTrain/513

- task_id: `isqTrain/513`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1320`

### Prompt

实现以下量子计算任务（使用isQ）：implements the bell_state_preparation pattern with modified rotation parameters (pi2_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply a modified U3 gate with parameters (π/3, 0, π) to a single qubit and measure it.
2. One qubit is needed (q[0]), and it is measured at the end.
3. State evolution: |0⟩ → U3(π/3, 0, π) → cos(π/6)|0⟩ + sin(π/6)|1⟩ = (√3/2)|0⟩ + (1/2)|1⟩.
4. Expected probabilities: P(|0⟩) = |√3/2|² = 0.75, P(|1⟩) = |1/2|² = 0.25, matching the given output.

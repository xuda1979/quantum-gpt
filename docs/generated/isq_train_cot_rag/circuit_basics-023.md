# ISQ training COT RAG corpus: circuit_basics shard 23

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1612

- task_id: `isqTrain/1612`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1449`

### Prompt

Code this in isQ: Apply Ry(pi*2/8) to each of 3 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Ry(π/4) to each of 3 qubits initialized to |0⟩, then measure all.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Initial state: |000⟩
   - Ry(π/4) on |0⟩ yields cos(π/8)|0⟩ + sin(π/8)|1⟩ for each qubit
   - Final state: [cos(π/8)|0⟩ + sin(π/8)|1⟩]⊗3
4. **Probabilities**: Each qubit independently yields |0⟩ with probability cos²(π/8) ≈ 0.8536 and |1⟩ with probability sin²(π/8) ≈ 0.1464. For bitstring b₂b₁b₀: P(b₂b₁b₀) = cos²(π/8)^(3-hamming(b)) × sin²(π/8)^hamming(b), where hamming(b) counts 1s.

## isqTrain/1596

- task_id: `isqTrain/1596`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1017`

### Prompt

Code this in isQ: Put 4 qubits in superposition, measure only q[3].

### Chain-of-thought reasoning

## Reasoning
Goal: Create superposition on 4 qubits, measure only q[3].
Qubits: 4 allocated (q[0]-q[3]), only q[3] measured.
State evolution: |0000⟩ → H(q[0])|+000⟩ → H(q[1])|++00⟩ → H(q[2])|+++0⟩ → H(q[3])|++++⟩
Final state: (1/4)Σᵢ∈{0..15} |i⟩, equal superposition of all 16 basis states.
Measuring only q[3] traces out q[0..2], giving P(|0⟩) = P(|1⟩) = 8/16 = 0.5.

## isqTrain/1803

- task_id: `isqTrain/1803`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4060`

### Prompt

请用isQ语言编写一个量子电路：Apply Rx(pi*5/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply an Rx(5π/6) rotation to a |0> state and measure the resulting qubit.
This requires 1 qubit, initialized to |0>, which is measured at the end.
The initial state is |ψ₀⟩ = |0⟩.
Applying the Rx(5π/6) gate transforms the state to |ψ₁⟩ = cos(5π/12)|0⟩ - i·sin(5π/12)|1⟩.
Measurement probabilities are determined by the squared magnitudes of the state amplitudes.
Thus, P(|0⟩) = cos²(5π/12) ≈ 0.06698 and P(|1⟩) = sin²(5π/12) ≈ 0.93301.

## isqTrain/1473

- task_id: `isqTrain/1473`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4860`

### Prompt

Create an isQ quantum circuit that Rotate a qubit from |0> by Ry(5pi/6) and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply an Ry(5π/6) rotation to a single qubit initially in |0⟩, then measure it.
Qubits: 1 qubit is needed, and it is measured.
State evolution: Starting from |0⟩, applying Ry(5π/6) gives Ry(5π/6)|0⟩ = cos(5π/12)|0⟩ + sin(5π/12)|1⟩.
Since cos(5π/12) ≈ 0.2588 and sin(5π/12) ≈ 0.9659, we get P(|0⟩) = cos²(5π/12) ≈ 0.067 and P(|1⟩) = sin²(5π/12) ≈ 0.933.

## isqTrain/2471

- task_id: `isqTrain/2471`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `global_phase`, `superposition`
- source: `isq_train_cot`
- dataset_index: `994`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[1];
procedure main() {
    M(q[0]);
}

```

Circuit 2:
```isq
import std;
qbit q[1];
procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Initializes qubit q[0] in state |0> and immediately measures it.
2. **Program B**: Initializes qubit q[0] in state |0>, applies a GPhase(0.0) gate, and measures it. 
3. **Key difference**: Program B explicitly applies a global phase gate with an angle of 0.0, which multiplies the state by $e^{i0} = 1$ (the identity operation).
4. **Probability equivalence**: The states in both programs remain exactly |0> right before measurement. Thus, the probability of measuring 0 is 100% in both cases.
5. **Verdict**: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/4667

- task_id: `isqTrain/4667`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `70`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]);
}

```

Program B:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

The user wants to compare two isQ programs and determine if they produce the same measurement probability distribution.

Program A:
X(q[1]);        // |01>
CNOT(q[0], q[1]); // |01>
CNOT(q[1], q[0]); // |10>
CNOT(q[0], q[1]); // |10>
X(q[0]);        // |00>

Program B:
X(q[1]);        // |01>
CNOT(q[1], q[0]); // |11>
CNOT(q[0], q[1]); // |10>
CNOT(q[1], q[0]); // |00>

Let's trace Program A:
Initial: |00>
X(q[1]): |01>
CNOT(q[0], q[1]): control=0, target=1. |01> -> |01>
CNOT(q[1], q[0]): control=1, target=0. |01> -> |10>
CNOT(q[0], q[1]): control=0, target=1. |10> -> |10>
X(q[0]): |10> -> |00>
Measurement probabilities: P(00) = 100%, P(01) = 0, P(10) = 0, P(11) = 0.
Wait, earlier measured qubit = higher bit?
M(q[0]) is measured first, then M(q[1]).
So |00> means q[0]=0, q[1]=0. bitstring is 00.
Wait, let's recheck the earlier measured qubit bit ordering.
"earlier measured qubit = higher bit" -> M(q[0]) corresponds to the higher bit.
So q[0]=0, q[1]=0 is 00.
If q[0]=1, q[1]=0 it's 10.

Let's trace Program B:
Initial: |00>
X(q[1]): |01>
CNOT(q[1], q[0]): control=1, target=0. |01> -> |11>
CNOT(q[0], q[1]): control=0, target=1. |11> -> |10>
CNOT(q[1], q[0]): control=1, target=0. |10> -> |00>
Measurement probabilities: P(00) = 100%, P(01) = 0, P(10) = 0, P(11) = 0.

Wait, both end up at |00> ?
Let me re-evaluate!
Wait, CNOT(q[1], q[0]) in Program A:
Wait, in Program A, the sequence of CNOTs is:
CNOT(q[0], q[1])
CNOT(q[1], q[0])
CNOT(q[0], q[1])
This is exactly a swap operation (three-CNOT decomposition)!
Wait.
CNOT(q[0], q[1]) on |01> gives |01>.
CNOT(q[1], q[0]) on |01> gives |10>.
CNOT(q[0], q[1]) on |10> gives |10>.
So it leaves |01> as |10>? No, swap (three-CNOT decomposition)(01) = 10.
So the state becomes |10>.
Then X(q[0]) flips q[0]: |10> -> |00>.

Let me re-read Program B CNOTs:
CNOT(q[1], q[0])
CNOT(q[0], q[1])
CNOT(q[1], q[0])
This is also a swap operation (three-CNOT decomposition)!
Wait, CNOT(1,0) CNOT(0,1) CNOT(1,0) is swap (three-CNOT decomposition).
Applied to |01>:
CNOT(1,0) on |01>: q[1] is control, q[0] is target. |01> -> |11>.
CNOT(0,1) on |11>: q[0] is control, q[1] is target. |11> -> |10>.
CNOT(1,0) on |10>: q[1] is control, q[0] is target. |10> -> |10>.
So both programs A and B apply swap (three-CNOT decomposition) to |01>, yielding |10>.
Wait, Program A then applies X(q[0]).
So Program A yields |00>.
Program B yields |10>.
The measurement distributions are different! P(00)=1 vs P(10)=1.
So they are NOT equivalent.
The predicted output: "Equivalent: False. Explanation: After adding X gate to Program A, the programs produce different probability distributions."

Let's write down the analysis.
Program A: Starts in |00>, X(q[1]) -> |01>. The three CNOTs form a swap operation (three-CNOT decomposition), transforming |01> -> |10

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'00': 1.0}, 'probs_b': {'10': 1.0}}

## isqTrain/1593

- task_id: `isqTrain/1593`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1998`

### Prompt

Create an isQ quantum circuit that Put 4 qubits in superposition, measure only q[0].

### Chain-of-thought reasoning

## Reasoning
The goal is to prepare a 4-qubit uniform superposition and measure only the first qubit.
The circuit requires 4 qubits, but only q[0] is measured.
Starting in the initial state |0000>, applying a Hadamard gate to each qubit evolves the state to |++++>. 
Since the resulting state is a separable product state, q[0] exists independently in the |+> = (1/√2)(|0> + |1>) state.
Consequently, measuring q[0] yields a 50% probability for |0> and a 50% probability for |1>.

## isqTrain/1718

- task_id: `isqTrain/1718`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3033`

### Prompt

Create an isQ quantum circuit that Apply Rz(pi/4) then H to |0>. Measure.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a concise step-by-step reasoning section for a specific quantum circuit (Rz(pi/4) then H on |0>, then measure).
    *   Format constraints: Start with "## Reasoning", NO code blocks, NO isQ code, use Dirac notation, strict length limits (3-8 lines).
    *   Circuit details:
        *   Initial state: $|0\rangle$
        *   Gate 1: $R_z(\pi/4)$
        *   Gate 2: $H$
        *   Measurement: 1 qubit

2.  **Analyze the Quantum Circuit:**
    *   Initial state: $|0\rangle$ (ignoring global phase so far). Actually, strictly speaking, $|0\rangle$ is an eigenvector of $R_z$, so it adds a global phase $e^{-i\pi/8}$. Let's write out the full math to be exact.
        $R_z(\pi/4) |0\rangle = e^{-i\pi/8} |0\rangle$.
    *   Apply H:
        $H e^{-i\pi/8} |0\rangle = e^{-i\pi/8} \frac{1}{\sqrt{2}} (|0\rangle + |1\rangle) = e^{-i\pi/8} |+\rangle$.
    *   Measurement:
        Probability of $|0\rangle$ is $|e^{-i\pi/8} \frac{1}{\sqrt{2}}|^2 = 1/2$.
        Probability of $|1\rangle$ is $|e^{-i\pi/8} \frac{1}{\sqrt{2}}|^2 = 1/2$.

3.  **Draft the Reasoning Steps (adhering to constraints):**
    *   *Goal*: Apply a rotation Rz(pi/4) and Hadamard gate to an initial |0> state and measure.
    *   *Qubits*: Requires 1 qubit, which is measured.
    *   *Evolution*:
        *   Start with $|0\rangle$.
        *   Apply $R_z(\pi/4)$: $R_z(\pi/4)|0\rangle = e^{-i\pi/8}|0\rangle$.
        *   Apply H: $H e^{-i\pi/8}|0\rangle = e^{-i\pi/8} \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   *Probabilities*: The global phase $e^{-i\pi/8}$ doesn't affect probabilities, so the state is effectively $|+\rangle$. Thus, measurement yields |0> and |1> with equal 50% probability.

4.  **Refine and Format (checking line count):**
    *   Line 1: Goal: Apply Rz(pi/4) and Hadamard gates to a |0> state and measure the output.
    *   Line 2: Qubits: 1 qubit is required, and it is measured at the end.
    *   Line 3: Evolution: Initialize to $|0\rangle$.
    *   Line 4: Applying $R_z(\pi/4)$ yields $e^{-i\pi/8}|0\rangle$, adding a global phase.
    *   Line 5: Applying the Hadamard gate transforms this to $e^{-i\pi/8}\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   Line 6: Probabilities: The global phase has no physical effect, leaving the state identical to $|+\rangle$.
    *   Line 7: Therefore, measuring yields $|0\rangle$ and $|1\rangle$ with an equal probability of 50%.

    Wait, constraint says: "Output ONLY the reasoning section, starting with '## Reasoning'".
    Wait, the prompt implies I must generate exactly what is inside the reasoning block, formatted nicely.
    Total lines: ~7. Fits perfectly within the 3-8 lines rule.

5.  **Final Polish:**
    ## Reasoning
    Goal: Apply an Rz rotation and Hadamard gate to a |0> state, then measure.
    Qubits: 1 qubit is used and measured.
    State evolution:
    1. Initialize to |0>.
    2. Apply Rz(pi/4), which adds a global phase: Rz(pi/4)|0> = e^(-i*pi/8)|0>.
    3. Apply H: H e^(-i*pi/8)|0> = e^(-i*pi/

## isqTrain/4653

- task_id: `isqTrain/4653`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `superposition`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3355`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Z(q[0]);
    H(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with a qubit in the initial state |0> and applies a sequence of four gates: Hadamard (H), Pauli-Z (Z), Hadamard (H), and Pauli-X (X).
2. Initial state: |0>.
3. Apply H: evolves to |+> = (1/sqrt(2))(|0> + |1>).
4. Apply Z: flips the phase of |1>, evolving the state to |-> = (1/sqrt(2))(|0> - |1>).
5. Apply H again: maps |-> back to |1>.
6. Apply X: flips |1> to |0>, resulting in the final state |0> before measurement.

Predicted probability distribution: {|0>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 1.0000.'}

## isqTrain/4395

- task_id: `isqTrain/4395`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1515`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[1];

procedure main() {
    // Two Hadamards cancel out: HH = I
    H(q[0]);
    H(q[0]);
    // Measure (returns |0> deterministically)
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes qubit q[0] to |0>, applies two consecutive Hadamard gates (H), then applies a Pauli-X gate (X).
2. Initial state: |0>
3. After the first H gate, the state becomes |+> = (|0> + |1>)/√2.
4. The second H gate cancels the first (H^2 = I), returning the state to |0>.
5. The X gate flips the qubit from |0> to |1>.
6. The final state before measurement is |1>.

Predicted probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|1>) = 1.0000.'}

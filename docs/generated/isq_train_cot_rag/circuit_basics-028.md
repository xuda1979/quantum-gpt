# ISQ training COT RAG corpus: circuit_basics shard 28

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1754

- task_id: `isqTrain/1754`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2871`

### Prompt

用isQ实现Start with |100000> on 6 qubits and apply a CNOT chain (q[0]->q[1], q[1]->q[2], ...). All qubits should end up as |1>.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task type: `code_generation` (Reasoning for a specific isQ quantum program).
    *   Prompt/Goal: Start with $|100000\rangle$ on 6 qubits, apply a CNOT chain (q[0]->q[1], q[1]->q[2], etc.). All qubits end up as $|1\rangle$.
    *   predicted output: ONLY the reasoning section, starting with "## Reasoning".
    *   Constraints: 3-8 lines (simple circuit), up to 15 lines (complex). Concise, precise step-by-step reasoning using Dirac notation.

2.  **Analyze the Circuit & State Evolution:**
    *   Initial state: $|000000\rangle$
    *   Apply X to q[0]: $|100000\rangle$
    *   CNOT(q[0], q[1]): Control is 1, so target flips. State becomes $|110000\rangle$.
    *   CNOT(q[1], q[2]): Control is 1, so target flips. State becomes $|111000\rangle$.
    *   CNOT(q[2], q[3]): Control is 1, target flips. State becomes $|111100\rangle$.
    *   CNOT(q[3], q[4]): Control is 1, target flips. State becomes $|111110\rangle$.
    *   CNOT(q[4], q[5]): Control is 1, target flips. State becomes $|111111\rangle$.
    *   Measurement of all 6 qubits: probability of $|111111\rangle$ is 1.0.

3.  **Draft the Reasoning (incorporating rules):**
    *   *Goal*: Propagate an initial $|1\rangle$ state across a 6-qubit chain using sequential CNOT gates.
    *   *Qubits*: 6 qubits initialized to $|0\rangle$, all are measured.
    *   *Evolution*: X(q[0]) changes $|000000\rangle$ to $|100000\rangle$.
    *   CNOT(q[0], q[1]) flips q[1] to $|1\rangle$, yielding $|110000\rangle$.
    *   CNOT(q[1], q[2]) flips q[2] to $|1\rangle$, yielding $|111000\rangle$.
    *   CNOT(q[2], q[3]) flips q[3] to $|1\rangle$, yielding $|111100\rangle$.
    *   CNOT(q[3], q[4]) flips q[4] to $|1\rangle$, yielding $|111110\rangle$.
    *   CNOT(q[4], q[5]) flips q[5] to $|1\rangle$, yielding $|111111\rangle$.
    *   *Probabilities*: The final deterministic state $|111111\rangle$ results in a 100% measurement probability for the bitstring $|111111\rangle$.

4.  **Refine and Condense:**
    *   ## Reasoning
    *   The goal is to propagate an initial $|1\rangle$ state across a 6-qubit chain using a sequence of CNOT gates.
    *   6 qubits are needed, starting in $|000000\rangle$, and all 6 are measured at the end.
    *   An X gate on q[0] initializes the state to $|100000\rangle$.
    *   CNOT(q[0], q[1]) flips q[1] to $|1\rangle$, evolving the state to $|110000\rangle$.
    *   CNOT(q[1], q[2]) yields $|111000\rangle$, and CNOT(q[2], q[3]) yields $|111100\rangle$.
    *   CNOT(q[3], q[4]) yields $|111110\rangle$, and finally CNOT(q[4], q[5]) flips the last qubit to $|1\rangle$, giving $|111111\rangle$.
    *   Since the final state is deterministically $|111111\rangle$, the expected measurement probability is exactly 1.0 for this bitstring.

5.  **Check constraints:**
    *   Output ONLY the reasoning section, starting with "## Reasoning"? Yes.
    *   No isQ code blocks? Yes.
    *   Dirac notation used? Yes.
    *   Concise (3-8 lines)? Yes, it's 7 lines. Perfect.
    *   Accurate? Yes.

6.  **Final Polish:** Just

## isqTrain/4668

- task_id: `isqTrain/4668`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4173`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

Second program:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

**Program A:** Applies X(q[1]) to reach |01⟩, then three CNOTs. Tracing: |01⟩ → CNOT(q[0],q[1]) → |01⟩ → CNOT(q[1],q[0]) → |11⟩ → CNOT(q[0],q[1]) → |10⟩. The final state is |10⟩, yielding measurement bitstring 10 with probability 1.

**Program B:** Applies X(q[1]) to reach |01⟩, then three CNOTs in different order. Tracing: |01⟩ → CNOT(q[1],q[0]) → |11⟩ → CNOT(q[0],q[1]) → |10⟩ → CNOT(q[1],q[0]) → |10⟩. Then H(q[0]) transforms |10⟩ → (1/√2)(|00⟩ − |10⟩), yielding 50% |00⟩ and 50% |10⟩.

**Key difference:** Program B applies an additional H(q[0]) gate after the CNOT sequence, placing q[0] into superposition and changing the measurement distribution from deterministic to probabilistic.

**Conclusion:** Program A always measures 10 (probability 1). Program B measures 00 and 10 each with probability 0.5. The distributions are different.

**Verdict: Not equivalent**

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'10': 1.0}, 'probs_b': {'00': 0.5, '10': 0.5}}

## isqTrain/4681

- task_id: `isqTrain/4681`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3338`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    CNOT(q[0], q[1]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |00>.
2. X gates on q[0] and q[1] flip both qubits, evolving the state to |11>.
3. CNOT(q[0], q[1]) flips the target q[1] because the control q[0] is |1>, changing the state to |10>.
4. The final X(q[0]) gate flips the first qubit back to |0>, resulting in the final state |00>.
5. Measurements M(q[0]) and M(q[1]) deterministically find both qubits in the 0 state.

Predicted probability distribution: {|00>: 1.0}

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 1.0000.'}

## isqTrain/1821

- task_id: `isqTrain/1821`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1645`

### Prompt

请用isQ语言编写一个量子电路：Apply Ry(pi*11/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
The goal is to prepare a quantum state by applying a Y-rotation of $11\pi/6$ to the initial $|0\rangle$ state and measure it.
One qubit is required to apply the rotation, and it is subsequently measured.
The initial state is $|0\rangle$. Applying $R_y(11\pi/6)$ transforms the state to $\cos(11\pi/12)|0\rangle + \sin(11\pi/12)|1\rangle$.
The probability of measuring $|0\rangle$ is $\cos^2(11\pi/12) \approx 0.9330$.
The probability of measuring $|1\rangle$ is $\sin^2(11\pi/12) \approx 0.0670$.

## isqTrain/1811

- task_id: `isqTrain/1811`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5694`

### Prompt

Code this in isQ: Apply Ry(pi*1/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Rotate the |0> state around the Y-axis by an angle of pi/6 and measure the resulting state.
2. **Qubits**: 1 qubit is required, which is measured at the end of the circuit.
3. **State Evolution**:
   - Initialize the qubit in the ground state: |psi> = |0>.
   - Apply the Ry(pi/6) gate, which performs a Y-rotation to yield |psi> = cos(pi/12)|0> + sin(pi/12)|1>.
4. **Probabilities**: Measuring the state gives the probability P(|0>) = cos²(pi/12) ≈ 0.933 and P(|1>) = sin²(pi/12) ≈ 0.067.

## isqTrain/1566

- task_id: `isqTrain/1566`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3007`

### Prompt

用isQ实现Apply the gate sequence H-X-Z to |0> and measure.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a reasoning section for an isQ quantum program that applies H, X, and Z to |0> and measures it.
    *   Gate sequence: H, X, Z on |0>.
    *   Qubits: 1.
    *   predicted output: "## Reasoning" section, 3-8 lines, Dirac notation, step-by-step state evolution, explanation of expected probabilities.
    *   Constraints: No code, only reasoning, concise.

2.  **Analyze the Quantum Circuit:**
    *   Initial state: $|0\rangle$
    *   Apply H: $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = |+\rangle$
    *   Apply X: $X|+\rangle = \frac{1}{\sqrt{2}}(X|0\rangle + X|1\rangle) = \frac{1}{\sqrt{2}}(|1\rangle + |0\rangle) = |+\rangle$
    *   Apply Z: $Z|+\rangle = \frac{1}{\sqrt{2}}(Z|0\rangle + Z|1\rangle) = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |-\rangle$
    *   Final state: $|-\rangle$
    *   Measurement probabilities: $|\langle 0|-\rangle|^2 = 0.5$, $|\langle 1|-\rangle|^2 = 0.5$.

3.  **Draft the Reasoning:**
    *   *Line 1:* The goal is to apply the H-X-Z gate sequence to the initial state |0> and measure the result.
    *   *Line 2:* One qubit is required, initialized to |0>, and it is measured.
    *   *Line 3:* The initial state |0> transforms to |+> after H, stays as |+> after X (since X leaves |+> unchanged up to global phase, or rather, X is a bit flip: $X(1/\sqrt{2}(|0\rangle+|1\rangle)) = 1/\sqrt{2}(|1\rangle+|0\rangle) = |+\rangle$), and becomes |-> after Z.
    *   *Line 4:* The final state is |->, which has an equal probability of collapsing to |0> or |1>.
    *   *Line 5:* Thus, the measurement probabilities are P(|0>) = 0.5 and P(|1>) = 0.5.

4.  **Refine to meet length and style constraints (3-8 lines):**
    ## Reasoning
    1. The goal is to apply the gate sequence H, X, and Z to an initial |0> state and measure the resulting qubit.
    2. This requires a single qubit, which is initialized to |0> and measured at the end.
    3. The state |0> evolves through the gates as follows: |0> ->[H] |+> ->[X] |+> ->[Z] |->.
    4. The X gate flips the computational basis states, leaving the superposition |+> unchanged.
    5. The Z gate flips the phase of |1>, converting |+> to |->.
    6. The final state |-> is an equal superposition, resulting in a 50/50 measurement split.
    7. Consequently, the expected measurement probabilities are 0.5 for |0> and 0.5 for |1>.

5.  **Final Polish (Concise and precise):**
    ## Reasoning
    * Goal: Apply the H, X, and Z gates to a single |0> qubit and measure it.
    * Qubits: 1 qubit is needed, starting in |0>, which is measured.
    * State evolution:
      - Initial: |0>
      - H gate: |0> -> |+> = 1/sqrt(2)(|0> + |1>)
      - X gate: |+> -> X(1/sqrt(2)(|0> + |1>)) = 1/sqrt(2)(|1> + |0>) = |+>
      - Z gate: |+> -> Z(1/sqrt(2)(|0> + |1>)) = 1/sqrt(2)(|0> - |1>) = |->
    * Probabilities: The final state |-> is in an equal superposition of |0> and |1>, giving P(|0>) = 0.5 and P(|1>) =

## isqTrain/4726

- task_id: `isqTrain/4726`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5656`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]);
}

```

vs.

```isq
import std;
qbit q[2];

procedure main() {
    X(q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A initializes two qubits to |00>, applies two X gates to q[0] (which cancel out, leaving it as |0>), resulting in a final state of |00> before measurement.
2. Program B initializes two qubits to |00>, applies a single X gate to q[1], resulting in a final state of |01> before measurement.
3. The key difference is the final quantum state prior to measurement: Program A leaves the system in |00>, while Program B leaves it in |01>.
4. The measurement probabilities are different: Program A yields 100% probability for |00>, whereas Program B yields 100% probability for |01>.
5. Verdict: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'00': 1.0}, 'probs_b': {'01': 1.0}}

## isqTrain/4752

- task_id: `isqTrain/4752`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `1849`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    H(q[1]);
    CNOT(q[0], q[1]);
    H(q[1]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]);
}

```

vs.

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A:**
    *   Initial state: |00>
    *   `X(q[0]); X(q[1]);` -> |11>
    *   `H(q[1]);` -> 1/sqrt(2) (|10> - |11>)
    *   `CNOT(q[0], q[1]);` -> control=q[0], target=q[1]. Control is |1>, so target flips. -> 1/sqrt(2) (|11> - |10>) = 1/sqrt(2) (-|10> + |11>)
    *   `H(q[1]);` -> apply H to q[1]. q[1] is |0> -> 1/sqrt(2)(|0>+|1>), |1> -> 1/sqrt(2)(|0>-|1>). So: 1/sqrt(2) [ -1/sqrt(2)(|0>+|1>) + 1/sqrt(2)(|0>-|1>) ] = 1/2 [ -|10> - |11> + |10> - |11> ] = -|11>. (Up to global phase).
    *   `X(q[0]);` -> flips q[0] from |1> to |0>. State becomes |01> (ignoring global phase).
    *   Measurement: q[0] measures 0, q[1] measures 1. Probabilities: P(01) = 100%.

2.  **Analyze Program B:**
    *   Initial state: |00>
    *   `X(q[0]); X(q[1]);` -> |11>
    *   `CNOT(q[0], q[1]);` -> control=q[0]=|1>, so target flips. |11> -> |10>.
    *   Measurement: q[0] measures 1, q[1] measures 0. Probabilities: P(10) = 100%.

3.  **Compare and Contrast:**
    *   Program A yields state |01> before measurement. P(01) = 1.
    *   Program B yields state |10> before measurement. P(10) = 1.
    *   The additional `H(q[1]); CNOT(q[0], q[1]); H(q[1]); X(q[0]);` in Program A transform |11> to |01>, whereas Program B just has `CNOT` which transforms |11> to |10>.
    *   Specifically, `H` on target, `CNOT`, `H` on target is equivalent to a CNOT with reversed control and target (since CNOT is symmetric up to Hadamards on target/control). Wait, CNOT(c, t) = H_t CNOT(t, c) H_t. Here c=q[0], t=q[1]. So H(q[1]) CNOT(q[0], q[1]) H(q[1]) = CNOT(q[1], q[0]) but control is q[1], target q[0].
    Let's check: CNOT(q[1], q[0]) on |11> -> q[1] is 1, so q[0] flips -> |01>.
    Then `X(q[0])` on |01> -> |11>. Wait, let me recalculate the H - CNOT - H part.
    State before H: |11>
    H on q[1]: 1/sqrt(2)(|10> - |11>)
    CNOT(c0, t1): |10> -> |11>, |11> -> |10>
    So it becomes 1/sqrt(2)(|11> - |10>) = -1/sqrt(2)(|10> - |11>)
    H on q[1]: -|11>. (calculated earlier).
    Yes, state is -|11> (global phase).
    Then X on q[0]: X on |1> is |0>. So state is -|01> -> |01>.
    Wait, if state is |01>, probability of measuring q[0]=0, q[1]=1 (which is bitstring 01) is 100%.
    Wait, what does Program B give?
    |00> -> X, X -> |11>
    CNOT(0, 1) -> |10>
    Prob of bitstring 10 is 100%.
    So Program A measures '01' (P=1), Program B measures '10' (P=1). They are definitely not equivalent.

4.  **Draft the Explanation:**
    *   Program A: Starts with |00>, applies X to both qubits yielding |11>. Then applies H to

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'01': 1.0}, 'probs_b': {'10': 1.0}}

## isqTrain/643

- task_id: `isqTrain/643`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `316`

### Prompt

实现以下量子计算任务（使用isQ）：implements the measurement_order_test pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a quantum circuit that implements CNOT using the decomposition H-CZ-H on the target qubit.

Let me trace through the circuit:
1. Start with |00⟩
2. H(q[0]) → (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
3. H(q[1]) → (|0⟩ + |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

Wait, let me re-read. The circuit is:
- H(q[0])
- H(q[1])
- CZ(q[0], q[1])
- H(q[1])
- M(q[1])
- M(q[0])

Wait, the decomposition is CNOT → H CZ H. So CNOT(control, target) = H(target) then CZ(control, target) then H(target).

So this circuit is:
1. H(q[0]) - put q[0] in superposition
2. H(q[1]) - first H of CNOT decomposition
3. CZ(q[0], q[1]) - CZ part of CNOT decomposition
4. H(q[1]) - second H of CNOT decomposition

So effectively: CNOT(q[0], q[1]) after H(q[0])

Let me trace:
1. |00⟩
2. H(q[0]): (|00⟩ + |10⟩)/√2
3. H(q[1]): (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
4. CZ(q[0], q[1]): CZ applies Z to q[1] when q[0]=|1⟩
   - |00⟩ stays |00⟩
   - |01⟩ stays |01⟩
   - |10⟩ → -|10⟩... wait no, CZ applies Z to the TARGET when control is |1⟩
   
   Wait, CZ(q[0], q[1]) means q[0] is control, q[1] is target. When q[0]=|1⟩, apply Z to q[1].
   
   Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩
   
   So:
   - |00⟩ → |00⟩
   - |01⟩ → |01⟩
   - |10⟩ → |10⟩
   - |11⟩ → -|11⟩
   
   State: (|00⟩ + |01⟩ + |10⟩ - |11⟩)/2

5. H(q[1]): Apply H to q[1]
   H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2
   H|1⟩ = |−⟩ = (|0⟩ - |1⟩)/√2
   
   For each term:
   - |0⟩⊗|0⟩ → |0⟩⊗(|0⟩+|1⟩)/√2
   - |0⟩⊗|1⟩ → |0⟩⊗(|0⟩-|1⟩)/√2
   - |1⟩⊗|0⟩ → |1⟩⊗(|0⟩+|1⟩)/√2
   - |1⟩⊗|1⟩ → |1⟩⊗(|0⟩-|1⟩)/√2
   
   So state becomes:
   (|0⟩⊗(|0⟩+|1⟩)/√2 + |0⟩⊗(|0⟩-|1⟩)/√2 + |1⟩⊗(|0⟩+|1⟩)/√2 - |1⟩⊗(|0⟩-|1⟩)/√2) / 2
   
   = (|0⟩⊗[(|0⟩+|1⟩)+(|0⟩-|1⟩)]/√2 + |1⟩⊗[(|0⟩+|1⟩)-(|0⟩-|1⟩)]/√2) / 2
   
   = (|0⟩⊗[2|0⟩]/√2 + |1⟩⊗[2|1⟩]/√2) / 2
   
   = (|00⟩/√2 + |11⟩/√2) / 2 × 2
   
   Wait let me redo this more carefully.
   
   = (1/2)[(1/√2)(|00⟩+|01⟩) + (1/√2)(|00⟩-|01⟩) + (1/√2)(|10⟩+|11⟩) - (1/√2)(|10⟩-|11⟩)]
   
   = (1/2)(1/√2)[|00⟩+|01⟩+|00⟩-|01⟩+

## isqTrain/1613

- task_id: `isqTrain/1613`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3256`

### Prompt

Help me write isQ code that Apply Ry(pi*3/8) to each of 3 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply an Ry(3π/8) rotation to each of 3 qubits independently, then measure all.

**Qubits:** 3 qubits (q[0], q[1], q[2]), all measured.

**State evolution:**
1. Initial state: |000⟩
2. Ry(3π/8) on q[0]: |0⟩ → cos(3π/16)|0⟩ + sin(3π/16)|1⟩
3. Ry(3π/8) on q[1]: same independent rotation on second qubit
4. Ry(3π/8) on q[2]: same independent rotation on third qubit
5. Final state: (cos(3π/16)|0⟩ + sin(3π/16)|1⟩)⊗³

**Probabilities:** Each qubit has P(0) = cos²(3π/16) ≈ 0.6913 and P(1) = sin²(3π/16) ≈ 0.3087. Since rotations are independent, the 8 outcome probabilities are products of these (e.g., P(000) = cos⁶(3π/16), P(111) = sin⁶(3π/16)).

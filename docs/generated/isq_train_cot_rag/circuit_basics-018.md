# ISQ training COT RAG corpus: circuit_basics shard 18

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1559

- task_id: `isqTrain/1559`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2740`

### Prompt

I need an isQ program to Apply H then T to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare a single qubit in a superposition state, apply a T gate, and measure the resulting state.
2. **Qubits:** 1 qubit (`q[0]`) is allocated and measured.
3. **State evolution:**
   - Start in the initial state: `|0>`
   - Apply the Hadamard gate `H`: `|0>` -> `|+> = (1/sqrt(2))(|0> + |1>)`
   - Apply the T gate (phase gate): `|+> -> (1/sqrt(2))(|0> + exp(i*pi/4)|1>)`
4. **Measurement probabilities:** The probability of measuring `|0>` is `|1/sqrt(2)|^2 = 0.5`, and the probability of measuring `|1>` is `|exp(i*pi/4)/sqrt(2)|^2 = 0.5`. The global phase introduced by T does not affect the measurement probabilities.

## isqTrain/4713

- task_id: `isqTrain/4713`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4422`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]);
}

```

程序B：
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[1], q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** applies an X gate to q[0] (state |10>), followed by a CNOT with q[0] as control and q[1] as target (state |11>), and finally applies another X gate to q[0] (state |01>).
2. **Program B** applies an X gate to q[0] (state |10>), followed by a CNOT with q[1] as control and q[0] as target, which does nothing since q[1] is |0> (state remains |10>).
3. **The key difference** is the extra X gate in Program A and the reversed control/target roles of the CNOT gate in Program B.
4. **The measurement probabilities are different** because Program A ends in the state |01>, yielding a 100% probability of measuring 01, while Program B ends in the state |10>, yielding a 100% probability of measuring 10.
5. **Verdict**: No (Not Equivalent)

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'01': 1.0}, 'probs_b': {'10': 1.0}}

## isqTrain/4696

- task_id: `isqTrain/4696`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2703`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    H(q[1]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial state**: The 2-qubit system starts in the ground state $|00\rangle$.
2

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.2500, P(|01>) = 0.2500, P(|10>) = 0.2500, P(|11>) = 0.2500.'}

## isqTrain/4702

- task_id: `isqTrain/4702`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5675`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    T(q[0]);
    T(q[0]);
    H(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

vs.

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    S(q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A**:
    *   Initial state: $|0\rangle$
    *   Apply H: $(H)|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = |+\rangle$
    *   Apply T: $(T)|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/4}|1\rangle)$
    *   Apply T: $(T^2)|+\rangle = (S)|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/2}|1\rangle) = \frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)$
    *   Apply H: $H \cdot S |+\rangle$. Note that $H S H = R_x(\pi/2) = \frac{1}{2}\begin{pmatrix} 1+i & 1-i \\ 1-i & 1+i \end{pmatrix}$ up to global phase, or we can just trace the state.
        Let's trace the state:
        $H \frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle) = \frac{1}{\sqrt{2}} (\frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) + \frac{i}{\sqrt{2}}(|0\rangle-|1\rangle)) = \frac{1}{2} ((1+i)|0\rangle + (1-i)|1\rangle)$
    *   Apply X: $X \frac{1}{2} ((1+i)|0\rangle + (1-i)|1\rangle) = \frac{1}{2} ((1-i)|0\rangle + (1+i)|1\rangle)$
    *   Probability of $|0\rangle$: $|\frac{1-i}{2}|^2 = \frac{1+1}{4} = 0.5$
    *   Probability of $|1\rangle$: $|\frac{1+i}{2}|^2 = \frac{1+1}{4} = 0.5$
    *   Wait, let's double check. $H S H$ is a rotation around X axis. So $X H S H = X R_x$ is also a rotation. The probabilities are indeed 0.5 for both. But the question is whether they produce the *same* probability distribution as Program B.

2.  **Analyze Program B**:
    *   Initial state: $|0\rangle$
    *   Apply H: $|+\rangle$
    *   Apply S: $\frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)$
    *   Apply H: $\frac{1}{2} ((1+i)|0\rangle + (1-i)|1\rangle)$
    *   Probability of $|0\rangle$: $|1+i|^2 / 4 = 2/4 = 0.5$
    *   Probability of $|1\rangle$: $|1-i|^2 / 4 = 2/4 = 0.5$

3.  **Compare**:
    *   Both programs result in exactly 50% probability of measuring $|0\rangle$ and 50% probability of measuring $|1\rangle$.
    *   Program A adds an X gate at the end, which swaps the amplitudes of $|0\rangle$ and $|1\rangle$. Since the magnitudes of the amplitudes were equal before the X gate, they remain equal after.
    *   Wait, the prompt says: "predicted output: Equivalent: True. Explanation: After adding X gate to Program A, the programs produce the same probability distributions." Wait, the prompt actually says "After adding X gate to Program A, the programs produce the same probability distributions." Is this a hint? It means without X, it's identical to Program B. With X, it's the same *probability distribution* because the magnitudes are just swapped, but they are equal. Let's trace it carefully.
    *   Program B applies H, S, H.
    *   Program A applies H, T, T, H, X.
    *   Since T^2 = S, H, T, T, H is the same as H, S, H.
    *   State after H, S, H is $\frac{1}{2}((1+i)|0\rangle + (1-i)|1\rangle)$.
    *   Program B probabilities: P(0) = 0.5, P(1) = 0.5.
    *

### Reference answer

{'equivalent': True, 'explanation': 'After adding X gate to Program A, the programs produce the same probability distributions.', 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1760

- task_id: `isqTrain/1760`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4523`

### Prompt

用isQ实现Apply Ry(pi/3) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Ry(π/3) to a single qubit initialized to |0⟩, then measure it.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Initial state: |ψ⟩ = |0⟩
   - After Ry(π/3): |ψ⟩ = cos(π/6)|0⟩ + sin(π/6)|1⟩ = (√3/2)|0⟩ + (1/2)|1⟩
4. **Expected probabilities**: P(|0⟩) = (√3/2)² = 3/4 = 0.75; P(|1⟩) = (1/2)² = 1/4 = 0.25.

## isqTrain/4751

- task_id: `isqTrain/4751`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `2764`

### Prompt

这两个isQ程序是等价的吗？

程序A：
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

程序B：
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    H(q[1]);
    CNOT(q[0], q[1]);
    H(q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

Let me trace through both programs step by step.

**Program A:**
1. Initial state: |00>
2. X(q[0]): |10>
3. X(q[1]): |11>
4. CNOT(q[0], q[1]): control=q[0]=1, so flip q[1] → |10>
5. Measure: always get |10>

**Program B:**
1. Initial state: |00>
2. X(q[0]): |10>
3. X(q[1]): |11>
4. H(q[1]): H on q[1] of |11> → |1> ⊗ H|1> = |1> ⊗ |-> = (|10> - |11>)/√2
5. CNOT(q[0], q[1]): control=q[0]=1 for both terms, flip q[1] → (|11> - |10>)/√2 = -( |10> - |11>)/√2

Wait, let me redo this more carefully.

After H(q[1]) on |11>:
|1>⊗H|1> = |1>⊗(|0>-|1>)/√2 = (|10>-|11>)/√2

After CNOT(q[0], q[1]) on (|10>-|11>)/√2:
CNOT|10> = |11> (control=1, flip target)
CNOT|11> = |10> (control=1, flip target)
So result = (|11>-|10>)/√2

6. H(q[1]): Apply H to q[1] of (|11>-|10>)/√2
H|0> = |+>, H|1> = |->
So: (|1>⊗H|1> - |1>⊗H|0>)/√2 = (|1>⊗|-> - |1>⊗|+>)/√2
= |1>⊗(|-> - |+>)/√2
= |1>⊗(|1>-|0>-|0>-|1>)/(2)

Hmm let me be more careful.

|-> - |+> = (|0>-|1>)/√2 - (|0>+|1>)/√2 = -2|1>/√2 = -√2|1>

So: |1>⊗(-√2|1>)/√2 = -|11>

Wait, so Program B gives |11>? Let me recheck.

After step 3 (X(q[0]), X(q[1])): |11>

Step 4: H(q[1]) on |11> = |1>⊗H|1> = |1>⊗(|0>-|1>)/√2

Step 5: CNOT(q[0], q[1]):
(|1>⊗|0> - |1>⊗|1>)/√2 = (|10> - |11>)/√2

CNOT(|10>) = |11>, CNOT(|11>) = |10>

Result: (|11> - |10>)/√2

Step 6: H(q[1]) on (|11> - |10>)/√2:
= (|1>⊗H|1> - |1>⊗H|0>)/√2
= |1>⊗(H|1> - H|0>)/√2
= |1>⊗(|-> - |+>)/√2
= |1>⊗((|0>-|1>) - (|0>+|1>))/(2)
= |1>⊗(-2|1>)/2
= |1>⊗(-|1>)
= -|11>

So Program B gives -|11>, which has measurement probability {'11': 1.0}.

Now Program A:
After step 3: |11>
Step 4: CNOT(q[0], q[1]) on |11> = |10>

So Program A gives |10>, measurement probability {'10': 1.0}.

So they are NOT equivalent. Program A gives |10> while Program B gives |11>.

Wait, this contradicts the predicted output explanation which says "Program A produces {'11': 1.0} while Program B produces {'10': 1.0}". Let me recheck.

Program A:
- X(q[0]): |10>
- X(q[1]): |11>
- CNOT(q[0], q[1]): control is q[0]=|1>, target is q[1]. Flip q[1]: |11> → |10>
- Measure: |10> → {'10': 1.0}

Program B:
- X(q[0]): |10>
- X

### Reference answer

{'equivalent': False, 'explanation': "CZ (H-CNOT-H) vs plain CNOT on |11> give different results Program A produces {'11': 1.0} while Program B produces {'10': 1.0}.", 'probs_a': {'10': 1.0}, 'probs_b': {'11': 1.0}}

## isqTrain/1412

- task_id: `isqTrain/1412`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4273`

### Prompt

Implement a quantum circuit in isQ: Apply CZ to |+>|1>. Measure control in Z basis (phase kickback is invisible without basis change).

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply CZ to |+⟩|1⟩ and measure the control qubit to show phase kickback is invisible in the Z basis.

**Qubits:** 2 qubits (q[0] control, q[1] target); only q[0] is measured.

**State evolution:**
1. |00⟩ → X(q[1]) → |01⟩
2. H(q[0]) → (|0⟩+|1⟩)/√2 ⊗ |1⟩ = (|01⟩+|11⟩)/√2
3. CZ applies Z to q[1] when q[0]=|1⟩: |11⟩→-|11⟩, yielding (|01⟩-|11⟩)/√2 = (|0⟩-|1⟩)/√2 ⊗ |1⟩ = |-⟩⊗|1⟩

**Expected probabilities:** The control qubit ends in |−⟩=(|0⟩-|1⟩)/√2. The relative phase between |0⟩ and |1⟩ doesn't affect Z-basis measurement probabilities: P(|0⟩)=P(|1⟩)=|1/√2|²=0.5.

## isqTrain/670

- task_id: `isqTrain/670`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `global_phase`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3964`

### Prompt

Implement a quantum circuit in isQ: implements the gate_decomposition pattern with modified rotation parameters (num_pi2s_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning
The circuit applies H twice with a global phase in between, exploiting H²=I to return to the initial state.
One qubit (q[0]) is used and measured.
State evolution: |0⟩ →H (1/√2)(|0⟩+|1⟩) →GPhase(π/3) e^(iπ/3)(1/√2)(|0⟩+|1⟩) →H e^(iπ/3)|0⟩.
Since the global phase is unobservable, the final state is equivalent to |0⟩.
Measurement yields |0⟩ with probability 1.0.

## isqTrain/4584

- task_id: `isqTrain/4584`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3659`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    Rx(pi/4.0, q[0]);
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   `H(q[0])`: Apply Hadamard to q[0]. State goes from |00> to |+0> = (|00> + |10>)/sqrt(2).
    *   `CNOT(q[0], q[1])`: Apply CNOT with q[0] as control, q[1] as target. State becomes Bell state (|00> + |11>)/sqrt(2).
    *   `Rx(pi/4.0, q[0])`: Apply Rx(pi/4) to q[0]. In matrix form, Rx(theta) = [[cos(theta/2), -i*sin(theta/2)], [-i*sin(theta/2), cos(theta/2)]].
        cos(pi/8) = c, sin(pi/8) = s.
        Apply to q[0]:
        |0> -> c|0> - is|1>
        |1> -> -is|0> + c|1>
        State becomes: (1/sqrt(2)) [ (c|00> - is|10>) + (-is|11> + c|01>) ] = (1/sqrt(2)) [ c(|00> + |01>) - is(|10> + |11>) ].
    *   `H(q[0]); Z(q[0]); H(q[0]);`: Apply X to q[0]. (Because HZH = X).
        Applying X swaps |0> and |1> components on q[0].
        State becomes: (1/sqrt(2)) [ c(|10> + |11>) - is(|00> + |01>) ] = (1/sqrt(2)) [ -is(|00> + |01>) + c(|10> + |11>) ].
    *   `M(q[0]); M(q[1]);`: Measure both qubits.

2.  **Calculate Probabilities:**
    *   P(|00>) = | -is/sqrt(2) |^2 = (1/2) * sin^2(pi/8) = (1/2) * (1 - cos(pi/4))/2 = (1/4)(1 - 1/sqrt(2)) = 0.25 - 0.25*sqrt(2)/2 = 0.25 - sqrt(2)/8. Wait, let's use exact values.
    *   sin(pi/8) = sqrt( (1 - cos(pi/4))/2 ) = sqrt( (1 - 1/sqrt(2))/2 ) = sqrt( (2 - sqrt(2))/4 ) = sqrt(2-sqrt(2))/2.
    *   Let's check the magnitude squared: 1/2 * sin^2(pi/8).
        1/2 * (2 - sqrt(2))/4 = (2 - sqrt(2))/8 = 0.25 - sqrt(2)/8.
        sqrt(2)/8 ~ 1.41421356 / 8 = 0.176776695.
        0.25 - 0.176776695 = 0.073223305.
    *   P(|01>) = same as P(|00>) from the same term |00>+|01> factor. So P(|01>) = 0.0732233.
    *   P(|10>) = | c/sqrt(2) |^2 = (1/2) * cos^2(pi/8) = (1/2) * (1 + cos(pi/4))/2 = (1/4)(1 + 1/sqrt(2)) = (2 + sqrt(2))/8 ~ (3.41421356)/8 = 0.426776695.
    *   P(|11>) = same as P(|10>) = 0.426776695.
    *   Wait, the probabilities I derived are:
        |00>: 0.0732...
        |01>: 0.0732...
        |10>: 0.4267...
        |11>: 0.4267...
    *   Let's check the predicted output: {|00>: 0.07322330470336313, |01>: 0.42677669529663687, |10>: 0.42677669529663687, |11>: 0.07322330470336313}.
    *   My derivation gave P(|01>) = 0.0732... but Expected has P(|01>) = 0.4267... and P(|10>) = 0

### Reference answer

{'predicted_probs': {'00': 0.073223, '01': 0.426777, '10': 0.426777, '11': 0.073223}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.0732, P(|01>) = 0.4268, P(|10>) = 0.4268, P(|11>) = 0.0732.'}

## isqTrain/4692

- task_id: `isqTrain/4692`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2678`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[1];

procedure main() {
    Z(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes one qubit, q[0], in the state |0>.
2. The Z gate is applied, which flips the phase of |1> but leaves |0> unchanged. The state remains |0>.
3. The X gate is applied, which acts as a quantum NOT gate, flipping the state from |0> to |1>.
4. The final state before measurement is exactly |1>.
5. Measurement of this state will deterministically yield 1.

Predicted probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|1>) = 1.0000.'}

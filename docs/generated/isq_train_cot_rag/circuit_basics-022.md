# ISQ training COT RAG corpus: circuit_basics shard 22

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1716

- task_id: `isqTrain/1716`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5516`

### Prompt

Code this in isQ: Apply Ry(pi/2) then Rz(pi/2) to |0>. Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a sequence of Ry and Rz rotations to a qubit initially in the |0⟩ state, then measure it.
2. **Qubits**: Requires 1 qubit (`q[0]`), which is measured at the end.
3. **Evolution**:
    - Initial state: |ψ⟩ = |0⟩
    - After Ry(π/2): Ry(π/2)|0⟩ = (|0⟩ + |1⟩)/√2 = |+⟩
    - After Rz(π/2): Rz(π/2)|+⟩ = (|0⟩ + i|1⟩)/√2
4. **Probabilities**: The final state magnitudes are |1/√2|² for both |0⟩ and |1⟩, yielding an exact 50% probability for both measurement outcomes 0 and 1.

## isqTrain/1572

- task_id: `isqTrain/1572`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5410`

### Prompt

I need an isQ program to On 3 qubits, set q[0]=|1> and apply CNOT with control=q[0], target=q[1]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Initialize a 3-qubit system to the state |110> using an X gate and a CNOT gate, then measure all qubits.
2. **Qubits:** 3 qubits are required (`q[0]`, `q[1]`, `q[2]`), and all are measured.
3. **Evolution:**
   - Initial state: |000>
   - Apply X to `q[0]`: |000> → |100>
   - Apply CNOT with control=`q[0]`, target=`q[1]`: |100> → |110> (the target flips because the control is |1>).
4. **Probabilities:** The final state is exactly |110>, so measurement yields `110` with a probability of 1.0.

## isqTrain/1591

- task_id: `isqTrain/1591`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3283`

### Prompt

Write isQ code for the following quantum task: Put 3 qubits in superposition, measure only q[1].

### Chain-of-thought reasoning

## Reasoning
Goal: Place 3 qubits into equal superposition, then measure qubit q[1] to observe |0⟩ or |1⟩ with equal probability.
Qubits: 3 allocated (q[0], q[1], q[2]); only q[1] is measured.
State evolution:
  1. Initial: |000⟩
  2. H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |00⟩
  3. H(q[1]): (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ |0⟩
  4. H(q[2]): (|+⟩|+⟩|+⟩) = equal superposition of all 8 basis states
Measurement of q[1] traces out q[0] and q[2]; each of their 4 combinations pairs with q[1]=|0⟩ or |1⟩, yielding P(|0⟩)=P(|1⟩)=0.5.

## isqTrain/1582

- task_id: `isqTrain/1582`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3743`

### Prompt

Help me write isQ code that On 4 qubits, set q[2]=|1> and apply CNOT with control=q[2], target=q[0]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Set q[2] to |1⟩, then apply CNOT with q[2] as control and q[0] as target.
2. **Qubits**: 4 qubits (q[0]–q[3]), all measured; output bitstring order: q[0]=highest bit.
3. **State evolution**:
   - Initial: |0000⟩
   - After X(q[2]): |0010⟩ (q[2] flipped to |1⟩)
   - After CNOT(q[2], q[0]): since control q[2]=|1⟩, target q[0] flips → |1010⟩
4. **Result**: Final state is |1010⟩, so measurement yields bitstring 1010 with probability 1.0.

## isqTrain/1579

- task_id: `isqTrain/1579`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4831`

### Prompt

Write an isQ program that On 4 qubits, set q[0]=|1> and apply CNOT with control=q[0], target=q[3]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to initialize qubit q[0] to |1> and apply a CNOT gate with q[0] as control and q[3] as target.
2. The circuit requires 4 qubits, all of which are measured at the end.
3. Initial state is |0000>. After applying X(q[0]), the state becomes |1000>.
4. Applying CNOT(q[0], q[3]) flips the target q[3] because the control q[0] is in the |1> state, resulting in the final quantum state |1001>.
5. Measuring all qubits yields the basis state |1001> with a probability of 1.0.

## isqTrain/4761

- task_id: `isqTrain/4761`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `608`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

Program B:
```isq
import std;
qbit q[2];

procedure main() {
    CNOT(q[0], q[1]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

**Program A:**
1. Starts in |00⟩
2. X(q[0]) flips q[0] → |10⟩
3. CNOT(q[0], q[1]) copies |1⟩ to q[1] → |11⟩
4. Measurement always yields |11⟩ (100% probability)

**Program B:**
1. Starts in |00⟩
2. CNOT(q[0], q[1]) does nothing (control is |0⟩) → |00⟩
3. H(q[0]) creates superposition → (|00⟩ + |10⟩)/√2
4. Measurement yields |00⟩ with 50% probability and |10⟩ with 50% probability

**Key Difference:** Program A deterministically produces |11⟩, while Program B produces an equal superposition of |00⟩ and |10⟩.

**Verdict:** Not equivalent — the two programs produce entirely different measurement probability distributions.

No

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'11': 1.0}, 'probs_b': {'00': 0.5, '10': 0.5}}

## isqTrain/4712

- task_id: `isqTrain/4712`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5403`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[1], q[0]);
    M(q[0]); M(q[1]);
}

```

Version B:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A**:
    *   Initial state: $|00\rangle$
    *   `X(q[0])`: Applies X to q[0]. State becomes $|10\rangle$. (q[0] is the first qubit, q[1] is the second).
    *   `CNOT(q[1], q[0])`: q[1] is control, q[0] is target. Since q[1] is $|0\rangle$, the CNOT does nothing. State remains $|10\rangle$.
    *   Measurements: M(q[0]), M(q[1]). Measuring $|10\rangle$ yields '10' (assuming earlier measured qubit is higher bit, or just q[0] then q[1] -> '10').
    Wait, let's re-read the predicted output: "Program A produces {'11': 1.0}".
    Let me re-check my state evaluation.
    Program A:
    q[0], q[1] initially |00>.
    X(q[0]) -> q[0] is |1>, q[1] is |0>. State is |10>.
    CNOT(q[1], q[0]): Control is q[1], Target is q[0].
    q[1] is 0. So CNOT does nothing.
    Wait, why does the predicted output say Program A produces {'11': 1.0}?
    Let me re-read the CNOT syntax in isQ.
    `CNOT(control, target)` -> `CNOT(q[1], q[0])` means q[1] is control, q[0] is target.
    Let me re-read predicted output again: "Program A produces {'11': 1.0} while Program B produces {'10': 1.0}."
    Wait, if `X(q[0])` is applied, q[0] becomes 1.
    If CNOT(q[1], q[0]) is applied, control is q[1]. q[1] is 0. So target q[0] is unchanged. State is 10.
    If CNOT(q[0], q[1]) is applied, control is q[0]. q[0] is 1. So target q[1] is flipped. State is 11.
    Wait! My manual trace: Program A -> |10>. Program B -> |11>.
    predicted output says: "Program A produces {'11': 1.0} while Program B produces {'10': 1.0}."
    Ah! Is X(q[0]) applied in Program A, then CNOT(q[1], q[0])?
    Wait, maybe my bitstring interpretation is different.
    "earlier measured qubit = higher bit" -> M(q[0]) is higher bit, M(q[1]) is lower bit.
    So |q[0], q[1]> = |1, 0> -> '10'.
    Wait, why does the predicted output say Program A produces {'11': 1.0}?
    Let me carefully re-read the prompt.
    Program A:
    X(q[0]);
    CNOT(q[1], q[0]);
    This should be |10>. So '10' is the output.

    Program B:
    X(q[0]);
    CNOT(q[0], q[1]);
    This should be |11>. So '11' is the output.

    Wait, The predicted output the exact opposite!
    "Program A produces {'11': 1.0} while Program B produces {'10': 1.0}."
    Could `X(q[0])` mean it initializes to $|0\rangle$ and we apply X?
    Let's check if there's any weirdness.
    Maybe `CNOT(q[1], q[0])` means "If q[1] is 1, flip q[0]". Yes.
    But wait, if the prompt's predicted output has a typo, I should gently point out the correct states or just focus on the equivalence (which is False in either case).
    Actually, let's think: maybe `CNOT(q[0], q[1])` is control q[0], target q[1]? Yes.
    Is it possible that isQ uses a different ordering?
    Whatever the case, `CNOT(q[1], q[0])` is not the same as `CNOT(q[0], q[1])` when `q[0]` is in $|1\rangle$ and `q[1]` is in $|0\rangle$. The distributions are different.

    Let me write out the states:
    Program A:
    $|00\rangle \xrightarrow{X_0} |

### Reference answer

{'equivalent': False, 'explanation': "CNOT direction matters: q[0]->q[1] flips target, q[1]->q[0] does not Program A produces {'11': 1.0} while Program B produces {'10': 1.0}.", 'probs_a': {'10': 1.0}, 'probs_b': {'11': 1.0}}

## isqTrain/1564

- task_id: `isqTrain/1564`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1667`

### Prompt

实现以下量子计算任务（使用isQ）：Apply H then X to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply an H gate followed by an X gate to a single |0> qubit and measure it.
One qubit is required, and it is measured.
The initial state is |0>.
Applying the H gate transforms the state to |+> = (1/√2)|0> + (1/√2)|1>.
Applying the X gate flips the basis states, yielding X|+> = (1/√2)|1> + (1/√2)|0> = |+>.
Because the final state |+> has equal probability amplitudes for |0> and |1>, measurement yields a 50% probability for each outcome.

## isqTrain/4655

- task_id: `isqTrain/4655`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5605`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

Program B:
```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A applies the X gate twice to qubit q[0], which acts as the identity (X * X = I), leaving the state in |0>.
2. Program B applies the Rx(pi) gate, which is equivalent to -iX, rotating the |0> state to -i|1>.
3. The key difference is that Program A leaves the qubit in the |0> state, while Program B leaves it in the |1> state (up to global phase).
4. The measurement probabilities differ: Program A yields 0 with 100% probability, whereas Program B yields 1 with 100% probability.
Equivalent: False

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'0': 1.0}, 'probs_b': {'1': 1.0}}

## isqTrain/1780

- task_id: `isqTrain/1780`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3772`

### Prompt

Help me write isQ code that Apply X gate 12 times to |0> and measure. (X^12 = I.)

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the X gate 12 times to an initial |0> state, then measure.
2. **Qubits**: 1 qubit (`q[0]`) is required and measured.
3. **Evolution**: The initial state is |0>. The X gate acts as a bit-flip (|0>↔|1>). Applying X 12 times results in an even number of flips.
4. **Final State**: Since $X^{12} = (X^2)^6 = I^6 = I$, the state returns to the initial state |0>.
5. **Probabilities**: Measuring the final state |0> yields the outcome 0 with probability 1.0, i.e., P(|0>) = 1.0.

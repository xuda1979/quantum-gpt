# ISQ training COT RAG corpus: circuit_operations shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/601

- task_id: `isqTrain/601`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3623`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[5];

procedure main() {
    Ry(3.1415926535, q[0]);
    Ry(3.1415926535, q[1]);
    Ry(3.1415926535, q[2]);
    Ry(3.1415926535, q[3]);
    Ry(3.1415926535, q[4]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations applied:** The circuit applies an `Ry(π)` rotation gate to each of the 5 qubits `q[0]` through `q[4]`. It then measures all 5 qubits.
2. **State evolution:** The initial state of the 5-qubit system is |00000>. The `Ry(π)` gate rotates the state |0> to |1> (up to a global phase of -1, which is physically irrelevant).
3. **Final state:** Applying `Ry(π)` to all qubits independently evolves the state from |00000> to |11111>.
4. **Measurement probabilities:** Since the final state is exactly |11111>, measurement yields this outcome with 100% probability.

Predicted probability distribution: {|11111>: 1.0}

### Reference answer

{'predicted_probs': {'31': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/201. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1766

- task_id: `isqTrain/1766`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2406`

### Prompt

Code this in isQ: Apply a 4-controlled X gate where only 3 controls are |1> (one is |0>). The target should NOT flip.

### Chain-of-thought reasoning

## Reasoning
- Goal: Demonstrate that a 4-controlled X gate leaves the target qubit unchanged when one of its controls is in the |0> state.
- Qubits: 5 qubits (q[0] to q[4]) are allocated, and all are measured.
- State evolution: The circuit starts in |00000>. Applying X gates to q[0], q[1], and q[2] flips them to |1>, evolving the state to |11100>.
- Gate action: The 4-controlled X gate targets q[

## isqTrain/666

- task_id: `isqTrain/666`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2555`

### Prompt

用isQ实现implements the phase_kickback pattern using an alternative gate decomposition (CZ -> H CNOT H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Demonstrate phase kickback using CZ decomposed as H-CNOT-H, yielding deterministic |11⟩ output.

2. **Qubits**: 2 qubits (q[0], q[1]), both measured at the end.

3. **State evolution**:
   - |00⟩ initial state
   - Y(q[0]): i|10⟩ (since Y|0⟩ = i|1⟩)
   - H(q[1]); H(q[1]): i|10⟩ (H² = I, identity)
   - CNOT(q[0], q[1]): i|11⟩ (control q[0]=|1⟩ flips target q[1] from |0⟩ to |1⟩)
   - H(q[1]); H(q[1]): i

## isqTrain/4269

- task_id: `isqTrain/4269`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4842`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[1];

procedure main() {
    // Apply Hadamard for superposition
    H(q[0]);
    // Measure qubit
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit to the state |0>.
2. Applying the Hadamard gate `H(q[0])` puts the qubit into an equal superposition: 1/sqrt(2)(|0> + |1>).
3. Applying the Pauli-X gate `X(q[0])` flips the computational basis states: 1/sqrt(2)(|1> + |0>). Since addition is commutative, this state is exactly the same as the state before the X gate (up to a global phase).
4. The final state right before measurement is |+> = 1/sqrt(2)(|0> + |1>).
5. Predicted probability distribution: {|0>: 0.5, |1>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.5000, P(|1>) = 0.5000.'}

## isqTrain/1892

- task_id: `isqTrain/1892`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `1754`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(pi/4.0, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program and predict the measurement outcome probabilities.
The program:
1. `X(q[0]); X(q[1]);` -> |11>
2. `H(q[0]); H(q[1]);` -> |--> (H|1> = |-)
3. `CNOT(q[0], q[1]);` -> |--> (CNOT on |-)_{control}(|->)_{target} = (|0-> - |1->)/sqrt(2) = (|0>(|0>-|1>) - |1>(|1>-|0>))/2 = (|00>-|01>-|10>+|11>)/2. Wait. |-) = (|0>-|1>)/sqrt(2). CNOT|->|-> = (|0>|-> - |1>|->)/sqrt(2) -> CNOT changes |1>|-> to |0>|->? No, CNOT on |1>|-> = |1> X|-> = -|1>|->. So CNOT|->|-> = |-->.
4. `Rz(pi/4.0, q[1]);` -> Rz applies phase to |1> state. Since it's applied to q[1], Rz|-> = (|0> - e^{-i*pi/4}|1>)/sqrt(2). Wait, Rz(theta) = exp(-i*theta/2)|0><0| + exp(i*theta/2)|1><1|. So Rz|-> = exp(-i*pi/8)|0> - exp(i*pi/8)|1>. This means state is exp(-i*pi/8) |0> - exp(i*pi/8) |1>. = exp(-i*pi/8)( |0> - exp(i*pi/4) |1> ). Let's drop the global phase. Overall state is |->_{q[1]} shifted: |0>(|0> - e^{i*pi/4}|1>) - |1>(|0> - e^{i*pi/4}|1>) / 2 = (|00> - e^{i*pi/4}|01> - |10> + e^{i*pi/4}|11>) / 2.
5. `CNOT(q[0], q[1]);` -> applies CNOT on the state. State = (|00> - e^{i*pi/4}|01> - |10> + e^{i*pi/4}|11>)/2. CNOT(1,0) maps |00> to |00>, |01> to |01>, |10> to |11>, |11> to |10>.
So CNOT(state) = (|00> - e^{i*pi/4}|01> - |11> + e^{i*pi/4}|10>)/2 = (|00> + e^{i*pi/4}|10> - e^{i*pi/4}|01> - |11>)/2.
Let's factor it:
q[0] = (|0> + e^{i*pi/4}|1>)/sqrt(2)
q[1] = (e^{i*pi/4}|0> - |1>)/sqrt(2) -- wait, is it factorable?
q[0] tensor q[1] = (|0> + e^{i*pi/4}|1>)(e^{i*pi/4}|0> - |1>)/2 = (e^{i*pi/4}|00> - |01> + e^{i*pi/2}|10> - e^{i*pi/4}|11>)/2. No, the state is not factorable.
Wait! Let's re-evaluate step 3:
State before step 4: |--> = (|00> - |01> - |10> + |11>)/2.
Apply Rz(pi/4) on q[1]:
(|00> - e^{i*pi/4}|01> - |10> + e^{i*pi/4}|11>)/2.
Apply CNOT(q[0], q[1]):
CNOT leaves |0x> as is. It flips |1x>.
|00> -> |00>
- e^{i*pi/4}|01> -> - e^{i*pi/4}|01>
- |10> -> - |11>
+ e^{i*pi/4}|11> -> + e^{i*pi/4}|10>
State = (|00> + e^{i*pi/4}|10> - e^{i*pi/4}|01> - |11>)/2
= 1/2( (|0> + e^{i*pi/4}|1>)_0 |0>_1 - (|0> + e

### Reference answer

{'predicted_probs': {'00': 0.1464, '11': 0.8536}, 'explanation': 'Expected probabilities: [0.14644660940672627, 0.0, 0.0, 0.8535533905932737]'}

## isqTrain/1764

- task_id: `isqTrain/1764`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1440`

### Prompt

Implement the following in isQ: Apply a 3-controlled X gate where only 2 controls are |1> (one is |0>). The target should NOT flip.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Demonstrate that a 3-controlled X gate does NOT activate when one of its three controls is in state |0⟩.

**Qubits:** 4 qubits q[0..3]; all are measured.

**State evolution:**
1. Initialize to |0000⟩
2. X(q[0]) → |1000⟩
3. X(q[1]) → |1100⟩
4. 3-controlled X with controls q[0], q[1], q[2] and target q[3]: since q[2]=|0⟩, the AND condition fails, so no flip occurs → |1100⟩

**Expected probabilities:** The final state |1100⟩ yields measurement outcome |1100⟩ with probability 1.0, confirming the target was not flipped.

## isqTrain/1837

- task_id: `isqTrain/1837`
- task_type: `code_generation`
- category: `circuit_operations`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2055`

### Prompt

请用isQ语言编写一个量子电路：3 layer(s) of CNOT entanglement on 4 qubits starting from |1000>.

### Chain-of-thought reasoning

Let me analyze this circuit carefully.

The goal is to create 3 layers of CNOT entanglement on 4 qubits starting from |1000>.

Let me trace through the state evolution:

Initial state: |1000>

Layer 1:
- CNOT(q[0], q[1]): control=q[0]=1, so flip q[1] → |1100>
- CNOT(q[1], q[2]): control=q[1]=1, so flip q[2] → |1110>
- CNOT(q[2], q[3]): control=q[2]=1, so flip q[3] → |1111>

Layer 2:
- CNOT(q[0], q[1]): control=q[0]=1, so flip q[1] → |1011>
- CNOT(q[1], q[2]): control=q[1]=0, so don't flip q[2] → |1011>
- CNOT(q[2], q[3]): control=q[2]=1, so flip q[3] → |1010>

Layer 3:
- CNOT(q[0], q[1]): control=q[0]=1, so flip q[1] → |1110>
- CNOT(q[1], q[2]): control=q[1]=1, so flip q[2] → |1111>
- CNOT(q[2], q[3]): control=q[2]=1, so flip q[3] → |1110>

Final state: |1110>

Wait, let me redo this more carefully. The state is |q[0], q[1], q[2], q[3]>.

Initial: |1000>

Layer 1:
- CNOT(q[0], q[1]): q[0]=1, flip q[1] → |1100>
- CNOT(q[1], q[2]): q[1]=1, flip q[2] → |1110>
- CNOT(q[2], q[3]): q[2]=1, flip q[3] → |1111>

Layer 2:
- CNOT(q[0], q[1]): q[0]=1, flip q[1] → |1011>
- CNOT(q[1], q[2]): q[1]=0, no flip → |1011>
- CNOT(q[2], q[3]): q[2]=1, flip q[3] → |1010>

Layer 3:
- CNOT(q[0], q[1]): q[0]=1, flip q[1] → |1110>
- CNOT(q[1], q[2]): q[1]=1, flip q[2] → |1111>
- CNOT(q[2], q[3]): q[2]=1, flip q[3] → |1110>

Final state: |1110>

So the measurement should give 1110 with probability 1.

Wait, let me double-check by computing this differently. CNOT chain on a computational basis state just propagates. Starting from |1000>:

Each layer consists of CNOT(0,1), CNOT(1,2), CNOT(2,3).

Let me think of this as a parity computation. After the first CNOT chain:
- q[1] = q[0] XOR q[1] = 1 XOR 0 = 1
- q[2] = q[1] XOR q[2] = 1 XOR 0 = 1  
- q[3] = q[2] XOR q[3] = 1 XOR 0 = 1

State: |1111>

Second chain:
- q[1] = q[0] XOR q[1] = 1 XOR 1 = 0
- q[2] = q[1] XOR q[2] = 0 XOR 1 = 1
- q[3] = q[2] XOR q[3] = 1 XOR 1 = 0

State: |1010>

Third chain:
- q[1] = q[0] XOR q[1] = 1 XOR 0 = 1
- q[2] = q[1] XOR q[2] = 1 XOR 1 = 0
- q[3] = q[2] XOR q[3] = 0 XOR 0 = 0

State: |1010>

Hmm wait, I got a different answer. Let me be more careful. The CNOT updates the target in place, so subsequent gates use the updated value.

Layer 1:
- CNOT(q[0], q[1]): new q[1] = old q[1] XOR q[0] = 0

## isqTrain/669

- task_id: `isqTrain/669`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `388`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

qbit q[2];

procedure main() {
    Y(q[0]);
    H(q[1]);
    CZ(q[0], q[1]);
    H(q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

The user wants an analysis of the given isQ program.
The program has 2 qubits.
1. Initial state: $|00\rangle$.
2. Y(q[0]): Applies Y gate to q[0].
   $Y|0\rangle = i|1\rangle$. State becomes $i|10\rangle$.
3. H(q[1]): Applies H gate to q[1].
   $H|0\rangle = |+\rangle$. State becomes $i(|10\rangle + |11\rangle)/\sqrt{2}$.
4. CZ(q[0], q[1]): Applies CZ gate.
   $CZ|10\rangle = -|10\rangle$, $CZ|11\rangle = -|11\rangle$.
   Wait, CZ applies Z to target if control is 1.
   If q[0] is control, q[1] is target:
   $|10\rangle \to -|10\rangle$
   $|11\rangle \to -|11\rangle$
   State becomes $-i(|10\rangle + |11\rangle)/\sqrt{2}$.
   Wait, let me double check CZ matrix.
   CZ = diag(1, 1, 1, -1) in standard basis |00>, |01>, |10>, |11>.
   So CZ does nothing to |10>, and flips the phase of |11>?
   Let's check:
   |00> -> |00>
   |01> -> |01>
   |10> -> |10>
   |11> -> -|11>
   Wait, my previous thought was wrong. Z applied to |0> is |0>, Z applied to |1> is -|1>.
   So if target (q1) is |0>, no change. If target is |1>, phase flip.
   So $CZ(|10\rangle + |11\rangle)/\sqrt{2} = (|10\rangle - |11\rangle)/\sqrt{2}$.
   Let's re-evaluate:
   State before CZ: $i \frac{1}{\sqrt{2}}(|10\rangle + |11\rangle)$.
   After CZ: $i \frac{1}{\sqrt{2}}(|10\rangle - |11\rangle)$.
5. H(q[1]): Applies H gate to q[1].
   $H \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |1\rangle$.
   So the state becomes $i|11\rangle$.
6. M(q[0]) and M(q[1]):
   Probability of |11> is 1.0.

Let's trace step by step:
1. Initial state: $|00\rangle$.
2. `Y(q[0])`: $Y|0\rangle = i|1\rangle$. State: $i|10\rangle$.
3. `H(q[1])`: $H|0\rangle = |+\rangle$. State: $\frac{i}{\sqrt{2}}(|10\rangle + |11\rangle)$.
4. `CZ(q[0], q[1])`: Applies Z to q[1] if q[0] is $|1\rangle$. State: $\frac{i}{\sqrt{2}}(|10\rangle - |11\rangle)$.
5. `H(q[1])`: $H(|0\rangle - |1\rangle)/\sqrt{2} = |1\rangle$. State: $i|11\rangle$.
Global phase $i$ does not affect measurement.
Measurement outcomes: 100% probability of $|11\rangle$.
Wait, M(q[0]) then M(q[1]). Earlier measured qubit = higher bit.
q[0] is measured first. So it's the higher bit.
Outcome is q[0]=1, q[1]=1, which is |11>.

Let's double check step 2.
$Y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}$.
$Y|0\rangle = i|1\rangle$. Correct.

Step 3.
$H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$. Correct.
State: $i|1\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{i}{\sqrt{2}}(|10\rangle + |11\rangle)$. Correct.

Step 4.
CZ(q[0], q[1]) means q[0] is control, q[1] is target.
If q[0] is |1>, apply Z

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/219. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4532

- task_id: `isqTrain/4532`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3138`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/4.0, q[0]);
    inv S(q[0]);
    X(q[0]);  // replaced H with X
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
The circuit sequentially applies an $R_x(\pi/4)$ rotation, an inverse S gate ($S^\dagger$), and an X gate to a single qubit initialized to $|0\rangle$.
1. $R_x(\pi/4)$ transforms the state to $\cos(\pi/8)|0\rangle - i\sin(\pi

### Reference answer

{'predicted_probs': {'0': 0.146447, '1': 0.853553}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.1464, P(|1>) = 0.8536.'}

## isqTrain/1874

- task_id: `isqTrain/1874`
- task_type: `output_prediction`
- category: `circuit_operations`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2505`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[1];
procedure main() {
    Rz(pi/4.0, q[0]);
    Ry(pi/2.0, q[0]);
    Rz(pi/2.0, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step analysis of a 1-qubit quantum circuit written in isQ, ending with the predicted probability distribution. The state evolution must use Dirac notation.
2.  **Analyze the Circuit:**
    *   Initial state: |0>
    *   Gate 1: `Rz(pi/4.0, q[0])`
    *   Gate 2: `Ry(pi/2.0, q[0])`
    *   Gate 3: `Rz(pi/2.0, q[0])`
    *   Measurement: `M(q[0])`
3.  **State Evolution:**
    *   Start: $|0\rangle$
    *   After `Rz(pi/4.0)`: $R_z(\pi/4)$ is a phase shift. $|0\rangle \to e^{-i\pi/8}|0\rangle$. Wait, $R_z(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$. So $e^{-i\pi/8}|0\rangle$. Global phase doesn't matter for probabilities, but let's keep track or note it as a global phase. Actually, $R_z(\theta)|0\rangle = e^{-i\theta/2}|0\rangle$.
    *   After `Ry(pi/2.0)`: $R_y(\theta) = \begin{pmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$. For $\theta = \pi/2$, $R_y(\pi/2)|0\rangle = \cos(\pi/4)|0\rangle + \sin(\pi/4)|1\rangle = \frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$. Including the previous phase (which is global at this point since it only applies to the $|0\rangle$ component), it's $e^{-i\pi/8}(\frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle)$.
    *   Wait, let's look at the combined operation: $R_z(\pi/2) R_y(\pi/2) R_z(\pi/4)$.
    *   Actually, let's just do the matrix math or Dirac notation carefully.
    *   $|0\rangle \xrightarrow{R_z(\pi/4)} e^{-i\pi/8}|0\rangle$
    *   $\xrightarrow{R_y(\pi/2)} e^{-i\pi/8}(\frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle)$
    *   $\xrightarrow{R_z(\pi/2)} e^{-i\pi/8}(\frac{1}{\sqrt{2}}e^{-i\pi/4}|0\rangle + \frac{1}{\sqrt{2}}e^{i\pi/4}|1\rangle)$
    *   The state is $\frac{1}{\sqrt{2}}e^{-i3\pi/8}|0\rangle + \frac{1}{\sqrt{2}}e^{i\pi/8}|1\rangle$.
    *   This state is equal to $|+\rangle$ up to a global/unitary phase. The probabilities of measuring 0 and 1 are exactly $1/2$.
4.  **Draft the response:**
    *   **Operations:** Rz(pi/4), Ry(pi/2), Rz(pi/2), Measurement.
    *   **Evolution:**
        *   Start: |0>
        *   Rz(pi/4) applies a phase to |0>: $e^{-i\pi/8}|0\rangle$
        *   Ry(pi/2) rotates the state to the equator: $e^{-i\pi/8}(\frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle)$
        *   Rz(pi/2) applies a relative phase: $\frac{1}{\sqrt{2}}e^{-i3\pi/8}|0\rangle + \frac{1}{\sqrt{2}}e^{i\pi/8}|1\rangle$
        *   (Alternatively, just say $R_z(\pi/2) R_y(\

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Expected probabilities: [0.5000000000000001, 0.49999999999999983]'}

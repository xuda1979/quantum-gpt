# ISQ training COT RAG corpus: state_preparation shard 42

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3363

- task_id: `isqTrain/3363`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `366`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply H to even-indexed qubits only in a 4-qubit register. Odd qubits stay |0>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Initialize a 4-qubit register and apply Hadamard gates to the even-indexed qubits (q[0] and q[2]) while leaving odd qubits (q[1] and q[3]) in their initial |0> state.
2. **Qubits & Measurement:** 4 global qubits are used, and all 4 are measured at the end.
3. **State Evolution:**
   - Start in the ground state |0000>.
   - Apply H(q[0]): Transforms |0> to |+> = (|0> + |1>)/√2. The state becomes (|0000> + |1000>)/√2

## isqTrain/3214

- task_id: `isqTrain/3214`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5629`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply Rx(7*pi/16) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an Rx(7π/16) rotation to a single qubit and measure the result.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Initial state: |0⟩
   - Rx(7π/16)|0⟩ = cos(7π/32)|0⟩ - i·sin(7π/32)|1⟩
4. **Probabilities**:
   - P(|0⟩) = cos²(7π/32) ≈ 0.5975
   - P(|1⟩) = sin²(7π/32) ≈ 0.4025
   - The Rx gate rotates around the X-axis, creating a superposition with these probabilities.

## isqTrain/3361

- task_id: `isqTrain/3361`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1797`

### Prompt

Help me write isQ code that an isQ program: apply H to even-indexed qubits only in a 2-qubit register. Odd qubits stay |0>.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply a Hadamard gate to the even-indexed qubit (q[0]) in a 2-qubit system while leaving the odd-indexed qubit (q[1]) untouched.
Qubits: A register of 2 qubits is required, and both are measured at the end.
Evolution:
1. Initialize the 2-qubit register to the ground state |00>.
2. Apply the H gate to q[0], evolving the state to (H|0>) ⊗ |0> = |+>|0> = 1/√2 (|00> + |10>).
Probabilities: Because q[1] remains in the |0> state, measuring the final state yields an equal 50% probability for both |00> and |10>.

## isqTrain/4781

- task_id: `isqTrain/4781`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `2014`

### Prompt

Create an isQ quantum circuit that implements: HZH = X on 5 qubits via for-loops. Declare a global qbit array q of 5 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement the identity HZH = X on 5 qubits to prepare state |11111⟩.
2. **Qubits**: Array of 5 qubits `q[5]`, all measured at the end.
3. **State evolution**:
   - Initial: |00000⟩
   - H on all: |00000⟩ → |+++++⟩
   - Z on all: |+++++⟩ → |-----⟩ (since Z|+⟩ = |−⟩)
   - H on all: |-----⟩ → |11111⟩ (since H|−⟩ = |1⟩)
4. **Result**: Final state is |11111⟩ with probability 1.0, as HZH = X flips each qubit.

## isqTrain/1435

- task_id: `isqTrain/1435`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3869`

### Prompt

请用isQ语言编写一个量子电路：Put 2 qubits in |+> state, then create a CZ entanglement chain (CZ between consecutive pairs). Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Initialize 2 qubits into a superposition and entangle them using a CZ gate.
2. **Qubits:** 2 qubits (`q[0]`, `q[1]`), both are measured.
3. **State Evolution:**
    - Start in the initial state $|00\rangle$.
    - Apply H to both: $|00\rangle \xrightarrow{H \otimes H} \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$. Both qubits are now in the $

## isqTrain/1547

- task_id: `isqTrain/1547`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3322`

### Prompt

用isQ实现Apply X gate to each of 6 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply an X gate to 6 qubits to flip their state, followed by measuring all of them.
Six qubits are used, and all six are measured at the end of the circuit.
The system starts in the initialized ground state |000000>.
Applying the Pauli-X gate to each qubit individually flips its state from |0> to |1>.
The state evolution transforms the system step-by-step until it reaches the final state |111111>.
As the final state is deterministically in the |111111> basis state, measurement yields the bitstring '111111' with a probability of 1.0.

## isqTrain/558

- task_id: `isqTrain/558`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3873`

### Prompt

Write isQ code for the following quantum task: implements a variant of the state_preparation pattern using q[5] -> q[7]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this task carefully.

The task is to implement a "variant of the state_preparation pattern using q[5] -> q[7]". This means I need to:
1. Use a 7-qubit register (q[0] to q[6])
2. The circuit should q[5] as a pattern but the actual circuit should use q[0] through q[6]
3. The expected measurement is |0000101> with probability 1.0

Looking at the predicted output |0000101>:
- This is a 7-qubit state
- The bitstring 0000101 means:
  - q[0] = 1 (rightmost bit)
  - q[1] = 0
  - q[2] = 1
  - q[3] = 0
  - q[4] = 0
  - q[5] = 0
  - q[6] = 0

Wait, let me reconsider the bitstring convention. In the --probs output, "earlier measured qubit = higher bit". So if we measure q[0], q[1], q[2], q[3], q[4], q[5], q[6], then:
- q[0] is the highest bit
- q[6] is the lowest bit

So |0000101> would mean:
- q[0] = 0 (bit 6, leftmost)
- q[1] = 0 (bit 5)
- q[2] = 0 (bit 4)
- q[3] = 0 (bit 3)
- q[4] = 1 (bit 2)
- q[5] = 0 (bit 1)
- q[6] = 1 (bit 0, rightmost)

Hmm, but Analyzing the circuit requirements, it applies X(q[0]) and X(q[2]), which would flip q[0] and q[2] to |1>. If the measurement gives |0000101>, let me check...

Actually, I think I need to reconsider. The circuit should:

And The predicted output |0000101>. Let me think about how the measurement bitstring maps to qubits.

If M(q) measures all qubits q[0] through q[6], and earlier measured qubit = higher bit, then:
- The bitstring 0000101 in binary
- q[0] corresponds to the highest bit position
- q[6] corresponds to the lowest bit position

0000101 = binary number
Position: 6 5 4 3 2 1 0
Bits:     0 0 0 0 1 0 1

So:
- q[0] = bit 6 = 0
- q[1] = bit 5 = 0
- q[2] = bit 4 = 0
- q[3] = bit 3 = 0
- q[4] = bit 2 = 1
- q[5] = bit 1 = 0
- q[6] = bit 0 = 1

But The circuit should X(q[0]) and X(q[2]), which should set q[0] and q[2] to |1>, not q[4] and q[6].

Hmm, there might be a discrepancy or I'm misunderstanding something. Let me re-read the problem.

Oh wait, the task says "write an isQ program that implements a variant of the state_preparation pattern using q[5] -> q[7]". The implementation might be for a different variant (q[3] perhaps?), and I need to adapt it for q[7].

Let me think about what "using q[5] -> q[7]" means. It might mean:
1. Use a 7-qubit register (indices 0-6)
2. The pattern involves qubits 5 through 7 (but wait, indices go 0-6, so maybe it means the total size is 7?)

Actually, looking more carefully, The circuit should `qbit q[7];` which creates qubits q[0] through q[6] (7 qubits total). The comment says "variant of the state_preparation pattern using q[5] -> q[7]" which I interpret as:
- Original pattern might use 5 qubits
- Extended to use 7 qubits

The circuit should X gates to q[0] and q[2], then measures all 7 qubits. The predicted output |0000101>.

Let me verify: if we start with |0000000> (7 q

## isqTrain/640

- task_id: `isqTrain/640`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `556`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;

qbit q[3];

procedure main() {
    Ry(1.910633236, q[0]);
    ctrl H(q[0], q[1]);
    
    CNOT(q[1], q[2]);
    CNOT(q[0], q[1]);
    X(q[0]);
    
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   `qbit q[3];`: Initial state is $|000\rangle$.
    *   `Ry(1.910633236, q[0]);`: Applies $R_y$ gate to $q_0$. The angle $\theta \approx 1.9106$ radians. Note that $R_y(\theta) |0\rangle = \cos(\theta/2)|0\rangle + \sin(\theta/2)|1\rangle$. Wait, $1.910633236 \approx \pi/1.644 \approx ?$ No, $1.9106 \approx 1.91$. What angle gives equal probabilities?
        *   Let's calculate $\theta/2 = 1.910633236/2 \approx 0.955316618$.
        *   $\cos(0.955316618)^2 = 0.3333...$ and $\sin(0.955316618)^2 = 0.6666...$? No, let's recheck.
        *   Wait, $1.910633236$ rad. $\cos(1.910633236/2) = \cos(0.955316618) \approx 0.577350269$, which is $1/\sqrt{3}$.
        *   So, $\cos(\theta/2)^2 = 1/3$ and $\sin(\theta/2)^2 = 2/3$.
        *   Wait, is it $\arccos(1/\sqrt{3}) \approx 0.955316618$? Yes, $\arctan(\sqrt{2}) = 0.955316618$.
        *   State after this step: $\frac{1}{\sqrt{3}}|0\rangle + \sqrt{\frac{2}{3}}|1\rangle$ on $q_0$. Overall: $\frac{1}{\sqrt{3}}|000\rangle + \sqrt{\frac{2}{3}}|100\rangle$.
    *   `ctrl H(q[0], q[1]);`: A controlled-Hadamard gate. If $q_0=|1\rangle$, apply H to $q_1$.
        *   H|0\rangle = |+\rangle = $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        *   State becomes: $\frac{1}{\sqrt{3}}|000\rangle + \sqrt{\frac{2}{3}} \frac{1}{\sqrt{2}}(|10\rangle + |11\rangle) \otimes |0\rangle$
        *   State is: $\frac{1}{\sqrt{3}}|000\rangle + \frac{1}{\sqrt{3}}|100\rangle + \frac{1}{\sqrt{3}}|110\rangle$. (for $q_0 q_1 q_2$)
    *   `CNOT(q[1], q[2]);`: Flips $q_2$ if $q_1=|1\rangle$.
        *   State becomes: $\frac{1}{\sqrt{3}}|000\rangle + \frac{1}{\sqrt{3}}|100\rangle + \frac{1}{\sqrt{3}}|111\rangle$.
    *   `CNOT(q[0], q[1]);`: Flips $q_1$ if $q_0=|1\rangle$.
        *   For $|000\rangle$, control is 0 -> stays $|000\rangle$.
        *   For $|100\rangle$, control is 1, target is 0 -> flips target to 1 -> $|110\rangle$.
        *   For $|111\rangle$, control is 1, target is 1 -> flips target to 0 -> $|101\rangle$.
        *   State becomes: $\frac{1}{\sqrt{3}}(|000\rangle + |110\rangle + |101\rangle)$.
    *   `X(q[0]);`: Flips $q_0$.
        *   For $|000\rangle \rightarrow |100\rangle$.
        *   For $|110\rangle \rightarrow |010\rangle$.
        *   For $|101\rangle \rightarrow |001\rangle$.
        *   State becomes: $\frac{1}{\sqrt{3}}(|100\rangle + |010\rangle + |001\rangle)$.
    *   Measurements: `M(q[

### Reference answer

{'predicted_probs': {'1': 0.33333333327463904, '2': 0.33333333327463904, '4': 0.3333333334507219}, 'explanation': 'Parametric variant of isqHumanEval/212. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4054

- task_id: `isqTrain/4054`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1993`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// 3-qubit W-state: (|001> + |010> + |100>) / sqrt(3)
qbit q[3];

procedure main() {
    // Prepare W-state using rotation + CNOT method
    // Step 1: Ry(2*arccos(1/sqrt(3))) on q[0]
    // arccos(1/sqrt(3)) ~ 0.9553 rad
    Ry(2.0 * 0.9553166, q[0]);
    // Step 2: controlled-Ry to split remaining amplitude
    // nctrl Ry(pi/2) when q[0]=|0>
    nctrl Ry(3.14159265358979 / 2.0, q[0], q[1]);
    // Step 3: CNOT to create third term
    CNOT(q[1], q[2]);
    CNOT(q[0], q[1]);
    // Swap to get correct ordering
    CNOS(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

**The Bug:** The line `CNOS(q[0], q[2]);` contains an invalid gate name "CNOS" — this is a typo for `CNOT`. The isQ standard library does not have a gate called `CNOS`.

**The Fix:** Replace `CNOS(q[0], q[2]);` with `CNOT(q[0], q[2]);`. This restores the three-CNOT swap (three-CNOT decomposition) decomposition needed to swap q[0] and q[2].

**State Evolution (Corrected Circuit):**
1. Initial: |000⟩
2. After `Ry(2·arccos(1/√3))` on q[0]: √(1/3)|000⟩ + √(2/3)|100⟩
3. After `nctrl Ry(π/2)` on q[1] (triggers when q[0]=|0⟩): √(1/6)|000⟩ + √(1/6)|010⟩ + √(

## isqTrain/1552

- task_id: `isqTrain/1552`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3296`

### Prompt

I need an isQ program to Apply Y gate to each of 2 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Y gate to 2 qubits and measure.
2. **Qubits**: 2 qubits, both measured.
3. **State evolution**:
    - Start with |00>
    - Apply Y to q[0]: Y|0> = i|1>, giving i|10>
    - Apply Y to q[1]: Y|0> = i|1>, giving i*i|11> = -|11>
4. **Probabilities**: The final state is -|11>, which has measurement probability P(|11>) = 1.0.

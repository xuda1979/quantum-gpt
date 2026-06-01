# ISQ training COT RAG corpus: state_preparation shard 15

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3170

- task_id: `isqTrain/3170`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_procedures`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `2122`

### Prompt

Help me write isQ code that with a procedure `hadamard_all(qbit q[3])` that applies H to 3 qubits using a for loop. Call from main, measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Hadamard to all 3 qubits via a for loop, creating an equal superposition, then measure.
2. **Qubits**: 3 global qubits `q[3]`, all measured in `main`.
3. **State evolution**:
   - Start: |000⟩
   - After H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |00⟩ = (|000⟩+|100⟩)/√2
   - After H(q[1]): (|000⟩+|010⟩+|100⟩+|110⟩)/2
   - After H(q[2]): (|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)/(2√2)
4. **Probabilities**: Each of 8 basis states has amplitude 1/(2√2), so probability |1/(2√2)|² = 1/8 = 0.125 each.

## isqTrain/1554

- task_id: `isqTrain/1554`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2345`

### Prompt

I need an isQ program to Apply Y gate to each of 4 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply a Y gate to each of 4 qubits and measure all, yielding a deterministic outcome.
2. **Qubits:** 4 qubits (q[0]–q[3]), all measured.
3. **State evolution:** Starting from |0000⟩, each Y gate maps |0⟩→i|1⟩. After Y(q[0]): i|1000⟩; after Y(q[1]): −|1100⟩; after Y(q[2]): −i|1110⟩; after Y(q[3]): |1111⟩ (global phases cancel or are unobservable).
4. **Expected probabilities:** The final state is |1111⟩, so measurement yields |1111⟩ with probability 1.0.

## isqTrain/3367

- task_id: `isqTrain/3367`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2504`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply H to odd-indexed qubits only in a 4-qubit register.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Generate a reasoning section for a specific isQ quantum program.
    *   **Goal:** Apply H to odd-indexed qubits in a 4-qubit register.
    *   **circuit implementation:** `H(q[1]); H(q[3]);`
    *   **Expected Probabilities:** {|0000>: 0.25, |0001>: 0.25, |0100>: 0.25, |0101>: 0.25}
    *   **Constraints:** "Output ONLY the reasoning section, starting with '## Reasoning'". "Be concise: 3-8 lines". "Do NOT include isQ code". "Use Dirac notation".

2.  **Analyze the Circuit & State Evolution:**
    *   *Initial State:* 4 qubits all in |0>. State is $|0000\rangle$. (Indexing: q[3] q[2] q[1] q[0] or q[0] q[1] q[2] q[3] depending on bitstring order. Standard isq `q[0]` is highest bit in bitstring. Let's use standard Dirac: $|q_3 q_2 q_1 q_0\rangle$. Initial state $|0000\rangle$.
    *   *Gate 1:* `H(q[1])` on qubit 1. Transforms $|0\rangle \to |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$. State becomes $\frac{1}{\sqrt{2}}(|0000\rangle + |0010\rangle)$.
    *   *Gate 2:* `H(q[3])` on qubit 3. Transforms $|0\rangle \to |+\rangle$. State becomes $\frac{1}{2}(|0000\rangle + |0010\rangle + |1000\rangle + |1010\rangle)$.
    *   *Measurement:* `M(q[0..3])`. Squaring amplitudes gives 0.25 probability for each of the four states.
    *   *Wait, check bitstring matching predicted output:*
        *   Expected: {|0000>: 0.25, |0001>: 0.25, |0100>: 0.25, |0101>: 0.25}
        *   My states: |0000>, |0010>, |1000>, |1010>.
        *   Why the mismatch?
        *   Ah! the predicted output bitstrings map earlier measured qubits to higher bits: `q[0]` is the highest bit, `q[1]` is next, `q[2]` next, `q[3]` lowest bit.
        *   Let's check:
            *   q[0]=0, q[1]=0, q[2]=0, q[3]=0 -> 0000
            *   q[0]=0, q[1]=0, q[2]=0, q[3]=1 -> 0001 (So q[3] is lowest bit).
            *   q[0]=0, q[1]=1, q[2]=0, q[3]=0 -> 0100 (So q[1] is second lowest bit).
            *   Therefore, the state is $|q_0 q_1 q_2 q_3\rangle$. Wait, if q[3] is the lowest bit (value 1), then it's on the right.
            *   Let's rewrite Dirac as $|q_0\rangle \otimes |q_1\rangle \otimes |q_2\rangle \otimes |q_3\rangle$.
            *   Initial state: $|0\rangle_0 \otimes |0\rangle_1 \otimes |0\rangle_2 \otimes |0\rangle_3$.
            *   H(q[1]) -> $|0\rangle_0 \otimes |+\rangle_1 \otimes |0\rangle_2 \otimes |0\rangle_3$.
            *   H(q[3]) -> $|0\rangle_0 \otimes |+\rangle_1 \otimes |0\rangle_2 \otimes |+\rangle_3$.
            *   Expand: $|0\rangle|+\rangle|0\rangle|+\rangle = \frac{1}{2} (|0000\rangle + |0001\rangle + |0100\rangle + |0101\rangle)$.
            *   This matches the predicted output perfectly!

3.  **Draft the Reasoning Section

## isqTrain/144

- task_id: `isqTrain/144`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1359`

### Prompt

Write an isQ program that implements a variant of the state_preparation pattern using q[1] -> q[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement state preparation variant applying Rx rotation on q[1] with an expanded 3-qubit register.
2. Need 3 qubits (q[0], q[1], q[2]); measuring q[1] and q[2].
3. State evolution:
   - Initial: |000⟩
   - After Rx(π/3, q[1]): cos(π/6)|000

## isqTrain/3210

- task_id: `isqTrain/3210`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `329`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Rx(11*pi/12) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an Rx rotation of 11π/12 to a single qubit and measure the result.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Initial state: |0⟩
   - After Rx(11π/12): cos(11π/24)|0⟩ - i·sin(11π/24)|1⟩
   - Since 11π/24 ≈ 1.44 rad, cos(11π/24) ≈ 0.129 and sin(11π/24) ≈ 0.992
4. **Measurement probabilities**:
   - P(|0⟩) = cos²(11π/24) ≈ 0.017
   - P(|1⟩) = sin²(11π/24) ≈ 0.983
   - This matches the expected {|0⟩: 0.017, |1⟩: 0.983}

## isqTrain/3390

- task_id: `isqTrain/3390`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4385`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: in a 4-qubit register, apply X then H to q[0] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply X then H to q[0] in a 4-qubit register, leaving others at |0>, then measure all.

4 qubits needed; all are measured.

State evolution:
- Start: |0000⟩
- X(q[0]) flips q[0]: |0000⟩ → |1000⟩
- H(q[0]) puts q[0] in superposition: |1000⟩ → (1/√2)(|0000⟩ - |1000⟩)

Final state (1/√2)(|0000⟩ - |1000⟩) yields equal measurement probabilities: P(|0000⟩) = 0.5, P(|1000⟩) = 0.5.

## isqTrain/3968

- task_id: `isqTrain/3968`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1535`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// 3-qubit GHZ state with phase pi
// Target: (|000> + e^{i*pi}|111>) / sqrt(2)
qbit q[3];

procedure main() {
    // Create GHZ state
    H(q[0]);
    // Apply phase e^{i*phi} to |1> component
    Rz(2.0 * 3.14159265358979 * 4.0 / 4.0, q[0]);
    // Entangle all qubits
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

Let me analyze this buggy code:

The target state is $(|000\rangle + e^{i\pi}|111\rangle) / \sqrt{2}$

The buggy code has:

This evaluates to:
$2.0 \times \pi \times 4.0 / 4.0 = 2\pi$

An Rz rotation of $2\pi$ is a full rotation, which brings the state back to itself - no net phase change.

For a phase of $\pi$, we need:
$Rz(\pi, q[0])$

The fixed code has:

This evaluates to $\pi \times 4.0/4.0 = \pi$

So the bug is that the original code used `2.0 *` as a multiplier, making the Rz angle $2\pi$ instead of $\pi$.

Let me trace the state evolution:

1. Initial state: $|000\rangle$

2. H(q[0]): $(|000\rangle + |100\rangle)/\sqrt{2}$

3. Rz($\pi$, q[0]): Rz applies phase $e^{-i\theta/2}$ to $|0\rangle$ and $e^{i\theta/2}$ to $|1\rangle$. 

With $\theta = \pi$:
- $|0\rangle$ gets $e^{-i\pi/2} = -i$
- $|1\rangle$ gets $e^{i\pi/2} = i$

So: $(-i|000\rangle + i|100\rangle)/\sqrt{2}$

This is equivalent to $(|000\rangle - |100\rangle)/\sqrt{2}$ up to global phase $-i$... wait, let me reconsider.

Actually $(-i|000\rangle + i|100\rangle)/\sqrt{2} = i(-|000\rangle + |100\rangle)/\sqrt{2} \cdot (-1) = ...$

Hmm, let me be more careful. $(-i|000\rangle + i|100\rangle)/\sqrt{2} = i(-|000\rangle + |100\rangle)/\sqrt{2}$

The global phase $i$ doesn't matter. So effectively we have $(|100\rangle - |000\rangle)/\sqrt{2} = (|000\rangle - |100\rangle)/\sqrt{2}$ up to a sign.

Wait, that's not right either. Let me recalculate.

After H(q[0]): $(|0\rangle + |1\rangle)/\sqrt{2} \otimes |00\rangle$

Rz($\pi$) on q[0]:
$Rz(\pi) = \begin{pmatrix} e^{-i\pi/2} & 0 \\ 0 & e^{i\pi/2} \end{pmatrix} = \begin{pmatrix} -i & 0 \\ 0 & i \end{pmatrix}$

Applied to $(|0\rangle + |1\rangle)/\sqrt{2}$:
$(-i|0\rangle + i|1\rangle)/\sqrt{2} = i(-|0\rangle + |1\rangle)/\sqrt{2}$

Global phase $i$ irrelevant, so effectively $(|1\rangle - |0\rangle)/\sqrt{2}$

After CNOT(q[0], q[1]): $(|110\rangle - |000\rangle)/\sqrt{2}$

After CNOT(q[1], q[2]): $(|111\rangle - |000\rangle)/\sqrt{2}$

Hmm, but the target is $(|000\rangle + e^{i\pi}|111\rangle)/\sqrt{2} = (|000\rangle - |111\rangle)/\sqrt{2}$

So we get $-(|000\rangle - |111\rangle)/\sqrt{2} = (-|000\rangle + |111\rangle)/\sqrt{2}$

This is equivalent to $(|000\rangle - |111\rangle)/\sqrt{2}$ up to a global phase of $-1$. Since global phases are irrelevant in quantum mechanics, this is correct!

Measurement probabilities: $|000\rangle$ with probability 0.5, $|111\rangle$ with probability 0.5. ✓

Now with the buggy code (Rz with angle $2\pi$):

$Rz(

## isqTrain/3203

- task_id: `isqTrain/3203`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2955`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply Ry(1*pi/5) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply an Ry rotation of π/5 to a single qubit and measure the result.
2. One qubit is required and measured.
3. State evolution: |0⟩ → Ry(π/5) → cos(π/10)|0⟩ + sin(π/10)|1⟩.
4. Probabilities follow from the amplitudes: P(|0⟩) = cos²(π/10) ≈ 0.9045, P(|1⟩) = sin²(π/10) ≈ 0.0955.

## isqTrain/3385

- task_id: `isqTrain/3385`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4318`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: in a 2-qubit register, apply X then H to q[0] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply an X gate followed by an H gate to the first qubit in a 2-qubit register, leaving the second qubit unchanged, and then measure both.
We need 2 qubits, `q[0]` and `q[1]`, and both are measured at the end of the circuit.
The initial state is |00>. Applying the X gate to `q[0]` flips it to |1>, resulting in the state |10>.
Applying the H gate to `q[0]` puts it into an equal superposition, changing the state to 1/√2 (|00> + |10>).
The expected measurement probabilities are therefore 50% for |00> and 50% for |10>, as the final state is an equal superposition of these two basis states.

## isqTrain/1376

- task_id: `isqTrain/1376`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3943`

### Prompt

Code this in isQ: Prepare the state |01>, apply a SWAP gate, and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to initialize a 2-qubit system to |01>, swap the qubit states, and measure the result.
Both qubits are initially in the ground state |00>.
Applying an X gate to q[1] flips its state, preparing the system in |01>.
The swap operation (three-CNOT decomposition) exchanges the states of q[0] and q[1], evolving the system from |01> to |10>.
Measuring both qubits yields the final state |10> with a 100% probability.

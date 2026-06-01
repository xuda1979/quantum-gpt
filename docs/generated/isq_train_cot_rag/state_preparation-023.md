# ISQ training COT RAG corpus: state_preparation shard 23

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3753

- task_id: `isqTrain/3753`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2308`

### Prompt

Help me write isQ code that an entangled 2-qubit state by applying Ry(2.000) to q[0] followed by CNOT(q[0], q[1]). This creates cos(θ/2)|00> + sin(θ/2)|11>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Generate an entangled 2-qubit state via Ry(2.000) on q[0] followed by CNOT(q[0], q[1]), then measure both.
Qubits: 2 (q[0], q[1]), both measured.

State evolution:
1. |00> — initial state
2. Ry(2.000) on q[0]: → cos(1.000)|00> + sin(1.000)|10>
3. CNOT(q[0], q[1]): → cos(1.000)|00> + sin(1.000)|11>

Expected probabilities: P(|00>) = cos²(1.000) ≈ 0.291927, P(|11>) = sin²(1.000) ≈ 0.708073.

## isqTrain/3749

- task_id: `isqTrain/3749`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4008`

### Prompt

帮我写一个isQ程序：Prepare a 2-qubit product state by applying Ry(1.0) to q[0] and Ry(0.5) to q[1]. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare a 2-qubit product state via independent Ry rotations and measure both qubits.
Qubits: 2 (q[0], q[1]), both measured.
Evolution: |00> → Ry(1.0)⊗I → (cos(0.5)|0> + sin(0.5)|1>)⊗|0> → I⊗Ry(0.5) → (cos(0.5)|0> + sin(0.5)|1>)⊗(cos(0.25)|0> + sin(0.25)|1>).
Probabilities: P(|00>) = cos²(0.5)·cos²(0.25) ≈ 0.7230, P(|01>) = cos²(0.5)·sin²(0.25) ≈ 0.0471, P(|10>) = sin²(0.5)·cos²(0.25) ≈ 0.2158, P(|11>) = sin²(0.5)·sin²(0.25) ≈ 0.0141.

## isqTrain/3194

- task_id: `isqTrain/3194`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3920`

### Prompt

Write an isQ program that an isQ program: apply Ry(9*pi/10) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
Goal: Create partial entanglement via Ry rotation on qubit 0 followed by CNOT to qubit 1.

Two qubits (q[0], q[1]) are used and both are measured.

State evolution:
1. Initial: |00⟩
2. Ry(9π/10) on q[0]: rotates |0⟩ → cos(9π/20)|0⟩ + sin(9π/20)|1⟩, giving cos(9π/20)|00⟩ + sin(9π/20)|10⟩
3. CNOT(q[0], q[1]): flips q[1] when q[0]=|1⟩, yielding cos(9π/20)|00⟩ + sin(9π/20)|11⟩

Expected probabilities: P(|00⟩) = cos²(9π/20) ≈ 0.0245, P(|11⟩) = sin²(9π/20) ≈ 0.9755, matching the specification.

## isqTrain/3988

- task_id: `isqTrain/3988`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3231`

### Prompt

Fix the bug in this quantum program:

```
import std;
// 3-qubit GHZ state with phase pi/4
// Target: (|000> + e^{i*pi/4}|111>) / sqrt(2)
qbit q[3];

procedure main() {
    // Create GHZ state
    H(q[0]);
    // Apply phase e^{i*phi} to |1> component
    Rz(3.14159265358979 * 1.0 / 4.0, q[0]);
    // Entangle all qubits
    // BUG: missing gate here
    CNOT(q[1], q[2]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The missing gate is `CNOT(q[0], q[1])`, which should precede `CNOT(q[1], q[2])`. Without it, q[0] is never entangled with q[1] and q[2]. The existing `CNOT(q[1], q[2])` acts on two qubits both in |0⟩, doing nothing.

2. **Fix**: Insert `CNOT(q[0], q[1]);` before `CNOT(q[1], q[2]);` to propagate entanglement from q[0] → q[1] → q[2].

3. **State evolution**:
   - |000⟩
   - H(q[0]) → (|000⟩ + |100⟩)/√2
   - Rz(π/4, q[0]) → (|000⟩ + e^{iπ/4}|100⟩)/√2
   - CNOT(q[0], q[1]) → (|000⟩ + e^{iπ/4}|110⟩)/√2
   - CNOT(q[1], q[2]) → (|000⟩ + e^{iπ/4}|111⟩)/√2 ✓

   Measurement yields |000⟩ or |111⟩ each with probability 0.5.

## isqTrain/1445

- task_id: `isqTrain/1445`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5603`

### Prompt

Implement a quantum circuit in isQ: Prepare the computational basis state |0011> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the 4-qubit computational basis state |0011> using X gates.
2. **Qubits:** 4 qubits are required, and all 4 are measured.
3. **State Evolution:**
   - Initial state is |0000>.
   - X(q[2]) flips the 3rd qubit: |0000> -> |0010>.
   - X(q[3]) flips the 4th qubit: |0010> -> |0011>.
4. **Probabilities:** The final state is deterministically |0011>. Measuring all qubits yields the bitstring '0011' (integer 3) with 100% probability.

## isqTrain/3174

- task_id: `isqTrain/3174`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4260`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Ry(pi/4) to q[0], then CNOT(q[0],q[1]) to create partial entanglement. Measure both.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a partially entangled two-qubit state using an Ry rotation followed by a CNOT gate.
Qubits: 2 qubits are required, and both are measured.
Step 1: Initialize to |00>. Apply Ry(pi/4) to q[0], rotating it to cos(pi/8)|0> + sin(pi/8)|1>, yielding the state cos(pi/8)|00> + sin(pi/8)|10>.
Step 2: Apply CNOT(q[0], q[1]). The |10> component flips the target q[1] to |1>, resulting in the entangled state cos(pi/8)|00> + sin(pi/8)|11>.
Measurement probabilities: The resulting probabilities should be the squared magnitudes of the amplitudes.
P(|00>) = cos^2(pi/8) ≈ 0.8536, and P(|11>) = sin^2(pi/8) ≈ 0.1464.

## isqTrain/4472

- task_id: `isqTrain/4472`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

qbit q[3];

procedure main() {
    
    q = [0.0, 0.5773502691896257, 0.5773502691896257, 0.0, 0.5773502691896257, 0.0, 0.0, 0.0];
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the initial state:**
    The initial state vector is given as:
    `q = [0.0, 0.5773502691896257, 0.5773502691896257, 0.0, 0.5773502691896257, 0.0, 0.0, 0.0];`
    The coefficient $0.5773502691896257 \approx 1/\sqrt{3}$.
    This corresponds to the state:
    $|q_2 q_1 q_0\rangle$:
    Index 0 ($|000\rangle$): 0
    Index 1 ($|001\rangle$): $1/\sqrt{3}$
    Index 2 ($|010\rangle$): $1/\sqrt{3}$
    Index 3 ($|011\rangle$): 0
    Index 4 ($|100\rangle$): $1/\sqrt{3}$
    Index 5 ($|101\rangle$): 0
    Index 6 ($|110\rangle$): 0
    Index 7 ($|111\rangle$): 0

    So, initial state $|\psi_0\rangle = \frac{1}{\sqrt{3}}(|001\rangle + |010\rangle + |100\rangle)$.
    Wait, in Dirac notation, $|q_0 q_1 q_2\rangle$:
    isQ usually uses index 0 as the rightmost bit or leftmost depending on qubit arrays, but index 1 means q[0] is 1, q[1] is 0, q[2] is 0. Let's verify standard bitstring indexing:
    Amplitude for $|q_2 q_1 q_0\rangle = |100\rangle$ is index $4$.
    So $|\psi_0\rangle = \frac{1}{\sqrt{3}}(|001\rangle + |010\rangle + |100\rangle)$. Wait, wait.
    If index 1 is $1/\sqrt{3}$, it corresponds to q[0]=1, q[1]=0, q[2]=0 -> $|001\rangle$.
    If index 2 is $1/\sqrt{3}$, q[0]=0, q[1]=1, q[2]=0 -> $|010\rangle$.
    If index 4 is $1/\sqrt{3}$, q[0]=0, q[1]=0, q[2]=1 -> $|100\rangle$.
    So $|\psi_0\rangle = \frac{1}{\sqrt{3}} (|100\rangle + |010\rangle + |001\rangle)$. Note: q[0] is the least significant bit.

2.  **Analyze the operations:**
    `H(q[0]); Z(q[0]); H(q[0]);` is equivalent to applying the X gate to `q[0]`.
    $X|0\rangle = |1\rangle$, $X|1\rangle = |0\rangle$.
    So this operation flips `q[0]`.

3.  **Trace the state evolution:**
    $|\psi_0\rangle = \frac{1}{\sqrt{3}}(|100\rangle + |010\rangle + |001\rangle)$
    Apply X to q[0]:
    $X_0 |\psi_0\rangle = \frac{1}{\sqrt{3}}(|100\rangle + |010\rangle + |000\rangle)$? Wait.
    Let's re-read the state components:
    Component 1: $|100\rangle$ (q[2]=1, q[1]=0, q[0]=0). Apply X to q[0] -> q[0] becomes 1 -> $|101\rangle$.
    Component 2: $|010\rangle$ (q[2]=0, q[1]=1, q[0]=0). Apply X to q[0] -> q[0] becomes 1 -> $|011\rangle$.
    Component 3: $|001\rangle$ (q[2]=0, q[1]=0, q[0]=1). Apply X to q[0] -> q[0] becomes 0 -> $|000\rangle$.

    Let's double check index mapping:
    $|001\rangle \rightarrow$ index 1. q[0]=1, q[1]=0, q[2]=0. Apply X to q[0] gives $|000\rangle$ (index 0).

### Reference answer

{'predicted_probs': {'000': 0.333333, '101': 0.333333, '110': 0.333333}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.3333, P(|101>) = 0.3333, P(|110>) = 0.3333.'}

## isqTrain/3980

- task_id: `isqTrain/3980`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3150`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// 5-qubit GHZ state with phase pi/2
// Target: (|00000> + e^{i*pi/2}|11111>) / sqrt(2)
qbit q[5];

procedure main() {
    // Create GHZ state
    H(q[0]);
    // Apply phase e^{i*phi} to |1> component
    Rz(3.14159265358979 * 2.0 / 4.0, q[0]);
    // Entangle all qubits
    CNOT(q[1], q[0]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[4]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The first CNOT `CNOT(q[1], q[0])` has swapped control and target. Since q[1] is in |0⟩, this CNOT does nothing, failing to entangle q[0] with q[1].

2. **Fix**: Change `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`, using q[0] (the prepared qubit) as control.

3. **State evolution**:
   - H(q[0]): (|0⟩+|1⟩)/√2 |0000⟩
   - Rz(π/2, q[0]): (|0⟩+e^{iπ/2}|1⟩)/√2 |0000⟩
   - CNOT(q[0],q[1]): (|00⟩+e^{iπ/2}|11⟩)/√2 |000⟩
   - CNOT(q[1],q[2])→CNOT(q[2],q[3])→CNOT(q[3],q[4]): propagates entanglement
   - Final: (|00000⟩+e^{iπ/2}|11111⟩)/√2 ✓

## isqTrain/4779

- task_id: `isqTrain/4779`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `5540`

### Prompt

Write an isQ program that implements: HZH = X on 3 qubits via for-loops. Declare a global qbit array q of 3 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Implement the identity HZH = X on 3 qubits via sequential for-loops, starting from |000⟩.
2. **Qubits:** 3 global qubits q[0], q[1], q[2]; all measured.
3. **State evolution:**
   - Start: |000⟩
   - After first H-loop: |000⟩ → H⊗H⊗H |000⟩ = |+++⟩
   - After Z-loop: Z|+⟩ = (|0⟩-|1⟩)/√2 = |−⟩, so |+++⟩ → |−−−⟩
   - After second H-loop: H|−⟩ = |1⟩ (since HZH = X), so |−−−⟩ → |111⟩
4. **Final state:** |111⟩ with probability 1.0, consistent with HZH = X applied to |000⟩ giving |111⟩.

## isqTrain/404

- task_id: `isqTrain/404`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4836`

### Prompt

Implement the following in isQ: implements a variant of the state_preparation pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The task is to write an isQ program that implements a variant of state_preparation using 4 qubits (q[3] -> q[4] means expanding from 3 to 4 qubits).

Analyzing the circuit requirements, it creates a 3-qubit W state but with 4 qubits in the register. The state vector has 8 amplitudes (for 3 qubits), but the register has 4 qubits.

Wait, let me re-read. The state vector has 8 elements: [0.0, 0.577..., 0.577..., 0.0, 0.577..., 0.0, 0.0, 0.0]

For 3 qubits, the basis states are:
|000> = index 0
|001> = index 1
|010> = index 2
|011> = index 3
|100> = index 4
|101> = index 5
|110> = index 6
|111> = index 7

So the state is: 0.577...(|001> + |010> + |100>) which is the W state.

But we have 4 qubits (q[0], q[1], q[2], q[3]). The resulting probabilities should be:
|0010>: 0.333...
|0100>: 0.333...
|1000>: 0.333...

So q[3] is always 0 (measured as 0), and the W state is on qubits q[0], q[1], q[2].

Actually, looking at this more carefully:
- We declare qbit q[4] (4 qubits)
- The state vector only has 8 elements (for 3 qubits)
- This seems like it should have 16 elements for 4 qubits

Hmm, but The circuit should `q = [0.0, 0.577..., ...]` with 8 elements for a 4-qubit register. That doesn't quite make sense mathematically.

Wait, looking at the predicted output: {|0010>: 0.333..., |0100>: 0.333..., |1000>: 0.333...}

These are 4-bit strings. The higher bit corresponds to earlier measured qubit (q[0] is the highest bit).

So |0010> means q[0]=0, q[1]=0, q[2]=1, q[3]=0
|0100> means q[0]=0, q[1]=1, q[2]=0, q[3]=0
|1000> means q[0]=1, q[1]=0, q[2]=0, q[3]=0

So the state is (|0010> + |0100> + |1000>)/sqrt(3), which is a W state spread across qubits 0, 1, 2 with qubit 3 always |0>.

The implementation assigns an 8-element state vector to a 4-qubit register. This might be a quirk of isQ where it pads with zeros or the system interprets it in a specific way.

Actually, I think there might be something I'm missing. The assignment `q = [8 elements]` for a 4-qubit system... maybe isQ only initializes the first 3 qubits based on the array size? Or perhaps it's treating this differently.

Looking at the predicted output again - 3 non-zero probabilities for a 4-qubit system means we need 16 amplitudes in general. But the reference only provides 8.

I think what's happening is that in isQ, when you assign a state vector shorter than the full Hilbert space dimension, the remaining qubits are assumed to be in |0> state or something similar. The 8-element vector describes a 3-qubit state that gets applied to the first 3 qubits, with q[3] staying in |0>.

For the reasoning:
1. Goal: Create a 4-qubit variant of the W state preparation where the W state |001> + |010> + |100> is embedded in the first 3 qubits with q[3] remaining |0>
2. 4 qubits needed (q[0], q[1], q[2], q[3]), all are measured
3. State evolution: Initial |0000> → State preparation assigns (|001> + |010> + |100>)/√3 to q[0:3] → Final state is (|0010> + |0100> + |1000>)/√3
4. Equal amplitudes 1/√3 give equal probabilities 1/3 for each measurement outcome

Wait,

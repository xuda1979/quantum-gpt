# ISQ training COT RAG corpus: state_preparation shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4801

- task_id: `isqTrain/4801`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_if_else`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `4159`

### Prompt

Create an isQ quantum circuit that implements: for-loop skip qubit 3 via continue. Declare a global qbit array q of 4 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X gates to qubits 0, 1, 2 while skipping qubit 3 using a `continue` statement in a for-loop.
2. **Qubits**: 4 global qubits (`q[4]`), all measured at the end.
3. **State evolution**:
   - Start: |0000⟩
   - i=0: X(q[0]) → |1000⟩
   - i=1: X(q[1]) → |1100⟩
   - i=2: X(q[2]) → |1110⟩
   - i=3: `continue` skips X(q[3]) → state remains |1110⟩
4. **Final state**: |1110⟩, meaning q[0]=1, q[1]=1, q[2]=1, q[3]=0. With earlier-measured qubits as higher bits, the bitstring is `1110` with probability 1.0.

## isqTrain/3730

- task_id: `isqTrain/3730`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5063`

### Prompt

Help me write isQ code that Prepare the 3-qubit GHZ state with phase pi/4:
|GHZ> = (|000> + e^{i*pi/4}|111>) / sqrt(2)
Use Hadamard on first qubit, Rz for phase, then CNOT chain. Measure all 3 qubits.

### Chain-of-thought reasoning

The user wants me to generate a concise reasoning section for creating a 3-qubit GHZ state with phase $\pi/4$.
The target state is $|GHZ\rangle = \frac{1}{\sqrt{2}}(|000\rangle + e^{i\pi/4}|111\rangle)$.
Circuit description:
1. Start with $|000\rangle$.
2. Apply H on q[0]: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|00\rangle$.
3. Apply Rz($\pi/4$) on q[0]: This gate applies a phase of $e^{i\theta/2}$ to $|0\rangle$ and $e^{-i\theta/2}$ to $|1\rangle$, or $e^{-i\theta}$ to $|1\rangle$ depending on the global phase convention. Wait, standard Rz($\theta$) is $\text{diag}(1, e^{-i\theta})$ in isQ, or maybe $e^{-i\theta/2} \text{diag}(1, e^{i\theta})$. Actually, standard Qiskit Rz is $e^{-i\theta Z/2}$, which is $|0\rangle \to e^{i\theta/2}|0\rangle$, $|1\rangle \to e^{-i\theta/2}|1\rangle$. But in many programming languages (like isQ), Rz applies $e^{-i\theta/2}$ and $e^{i\theta/2}$, or $e^{i\theta}$ and $1$. Let's look at the prompt's circuit implementation: `Rz(3.14159265358979 * 1.0 / 4.0, q[0]);`. If the state needs $e^{i\pi/4}|1\rangle$, and they use Rz($\pi/4$), then Rz($\theta$) must act as $|0\rangle \to |0\rangle$, $|1\rangle \to e^{i\theta}|1\rangle$ (up to global phase). Let's assume standard isQ Rz($\theta$) is effectively equivalent to $U1(\theta) = \text{diag}(1, e^{i\theta})$. Let's just trace it as "Applies phase $e^{i\pi/4}$ to $|1\rangle$, giving $\frac{1}{\sqrt{2}}(|000\rangle + e^{i\pi/4}|111\rangle)$." Wait, The circuit should Rz($\pi/4$) after H. So H creates $(|0\rangle+|1\rangle)/\sqrt{2}$. Then Rz creates $(|0\rangle + e^{i\pi/4}|1\rangle)/\sqrt{2}$.
4. Apply CNOT(q[0], q[1]): $\frac{1}{\sqrt{2}}(|00\rangle + e^{i\pi/4}|11\rangle)|0\rangle$.
5. Apply CNOT(q[1], q[2]): $\frac{1}{\sqrt{2}}(|000\rangle + e^{i\pi/4}|111\rangle)$.
6. Measure all 3 qubits. Expected probabilities: 50% for |000>, 50% for |111>.

Let's structure the reasoning as requested:
## Reasoning
Goal: Prepare the 3-qubit GHZ state with a phase of $\pi/4$ on the $|111\rangle$ component.
Qubits: 3 qubits (`q[0]`, `q[1]`, `q[2]`), all measured.
State evolution:
- Initial state: $|000\rangle$
- `H(q[0])` creates superposition: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|00\rangle$
- `Rz(pi/4, q[0])` adds phase to $|1\rangle$: $\frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/4}|1\rangle)|00\rangle$
- `CNOT(q[0], q[1])` entangles q0, q1: $\frac{1}{\sqrt{2}}(|00\rangle + e^{i\pi/4}|11\rangle)|0\rangle$
- `CNOT(q[1], q[2])` entangles q1, q2: $\frac{1}{\sqrt{2}}(|000\rangle + e^{i\pi/4}|111\rangle)$
Measurements yield $|000\rangle$ and $

## isqTrain/4012

- task_id: `isqTrain/4012`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3187`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// 4-qubit GHZ state via for loop
qbit q[4];

procedure main() {
    // Superposition on first qubit
    H(q[0]);
    // Entangle all via CNOT chain
    for i in 0:3 {
        CZ(q[i], q[i + 1]);
    }
    // Measure all
    for i in 0:4 {
        M(q[i]);
    }
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The entanglement loop uses `CZ(q[i], q[i + 1])` instead of `CNOT(q[i], q[i + 1])`. CZ applies a Z gate (phase flip) to the target when the control is |1⟩, but since all targets start in |0⟩, Z|0⟩ = |0⟩ — the gate has no effect. The qubits never become entangled, leaving the state at (|0000⟩ + |1000⟩)/√2.

2. **Fix**: Replace `CZ` with `CNOT` in the for loop. CNOT flips the target qubit from |0⟩ to |1⟩ when the control is |1⟩, propagating the superposition across all qubits.

3. **State evolution (corrected)**:
   - Init: |0000⟩
   - H(q[0]): (|0000⟩ + |1000⟩)/√2
   - CNOT(q[0],q[1]): (|0000⟩ + |1100⟩)/√2
   - CNOT(q[1],q[2]): (|0000⟩ + |1110⟩)/√2
   - CNOT(q[2],q[3]): (|0000⟩ + |1111⟩)/√2
   - Measurement: {|0000⟩: 0.5, |1111⟩: 0.5} ✓

## isqTrain/3130

- task_id: `isqTrain/3130`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4427`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: use a for loop to apply H to each of 5 qubits, then measure all with a for loop.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create an equal superposition across 5 qubits using Hadamard gates, then measure all qubits.
2. **Qubits**: 5 qubits (q[0]–q[4]), all measured.
3. **State evolution**: Start in |00000⟩. Each H gate maps |0⟩ → |+⟩ = (|0⟩+|1⟩)/√2. After H on all 5 qubits: |ψ⟩ = (1/√2)^5 Σ_{x∈{0,1}^5} |x⟩ = (1/4√2)(|00000⟩+|00001⟩+⋯+|11111⟩).
4. **Probabilities**: Each of the 32 basis states has amplitude 1/(4√2), giving probability |1/(4√2)|² = 1/32 ≈ 0.03125. Measurement yields a uniform distribution over all 32 possible outcomes.

## isqTrain/4763

- task_id: `isqTrain/4763`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4217`

### Prompt

Code this in isQ: implements: H on first 2, X on rest of 4 qubits. Declare a global qbit array q of 4 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create superposition on first 2 qubits with H gates and flip remaining 2 qubits to |1> with X gates.
2. **Qubits**: 4 global qubits `q[4]`, all measured at the end.
3. **State evolution**:
   - Initialize: |ψ₀⟩ = |0000⟩
   - H(q[0]) and H(q[1]): |ψ₁⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2 ⊗ |00⟩
   - X(q[2]) and X(q[3]): |ψ₂⟩ = (|0011⟩+|0111⟩+|1011⟩+|1111⟩)/2
4. **Probabilities**: Each of the 4 basis states has amplitude 1/2, giving probability |1/2|² = 0.25 each, matching predicted output.

## isqTrain/572

- task_id: `isqTrain/572`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5661`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[5];

procedure main() {
    X(q[1]);
    X(q[4]);
    M(q);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program**:
    *   Qubits initialized: `q[5]` -> $|00000\rangle$
    *   `X(q[1]);` -> Applies X gate to `q[1]`. Note: Usually qubit arrays in isQ are 0-indexed. `q[1]` is the second qubit.
    *   `X(q[4]);` -> Applies X gate to `q[4]`. `q[4]` is the fifth qubit.
    *   `M(q);` -> Measures all qubits `q[0]` to `q[4]`.

2.  **Determine state evolution**:
    *   Initial state: $|00000\rangle$
    *   After `X(q[1])`: $|00010\rangle$ (since `q[1]` is flipped to 1, wait, let's check the bit order convention. The prompt says "earlier measured qubit = higher bit" for `--probs` mode output. So `q[0]` is the highest bit, `q[4]` is the lowest bit. The string is $q_0 q_1 q_2 q_3 q_4$.)
    *   Let's re-verify: `X(q[1])` flips the second qubit ($q_1$). State becomes $q_0=0, q_1=1, q_2=0, q_3=0, q_4=0$. String: `01000`.
    *   After `X(q[4])`: flips the fifth qubit ($q_4$). State becomes $q_0=0, q_1=1, q_2=0, q_3=0, q_4=1$. String: `01001`.
    *   Wait, let me double check the predicted output in the prompt: `Expected measurement probabilities: {|10010>: 1.0}`.
    *   Ah! the predicted output is `10010`. Let's count indices:
        *   If `q[1]` corresponds to a bit, and `q[4]` corresponds to a bit.
        *   In the predicted output `10010`, the '1's are at positions (from left, 0-indexed): 0 and 3.
        *   Let's count from right (0-indexed): 1 and 4.
        *   If the bitstring is $q_4 q_3 q_2 q_1 q_0$, then `q[1]` is the second bit from the right (index 1), and `q[4]` is the fifth bit from the right (index 4).
        *   Wait, `10010` has bits: $q_4=1, q_3=0, q_2=0, q_1=1, q_0=0$.
        *   So `q[4]` is 1, `q[3]` is 0, `q[2]` is 0, `q[1]` is 1, `q[0]` is 0.
        *   Let's re-read: "earlier measured qubit = higher bit". So `M(q)` measures `q[0]`, then `q[1]`, etc.
        *   So `q[0]` is the highest bit (leftmost in the string).
        *   If `q[0]` is leftmost, then `10010` means:
            *   `q[0]` = 1
            *   `q[1]` = 0
            *   `q[2]` = 0
            *   `q[3]` = 1
            *   `q[4]` = 0
        *   But the code says `X(q[1])` and `X(q[4])`. If `q[1]` and `q[4]` are flipped, their values should be 1. So the string should have 1s at `q[1]` and `q[4]`. That would be `01001`.
        *   Why is the expected `{|10010>: 1.0}`? Let's check standard isQ bit ordering. Maybe "earlier measured qubit = lower bit"?
        *   Let's rethink: `q[0]` = rightmost bit (index 0). `q[1]` = index 1. `q[4]` = index 4.
        *   If `q[1]` = 1 and `q[4]` = 1, then the string is `10010`. (

### Reference answer

{'predicted_probs': {'18': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/191. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3391

- task_id: `isqTrain/3391`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3254`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: in a 4-qubit register, apply X then H to q[1] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a reasoning section for an isQ program that applies X and then H to the second qubit (q[1]) of a 4-qubit register, leaving the rest as |0>, and measuring all qubits.
2.  **Circuit Details**:
    *   4 qubits: `q[0]`, `q[1]`, `q[2]`, `q[3]`
    *   Initial state: |0000>
    *   Apply X to q[1]: state becomes |0010> (where q[1] is the second bit, wait... isQ bit ordering: usually standard is q[0] is highest or lowest. Let's assume standard Dirac order: $|q_3 q_2 q_1 q_0\rangle$. But wait, standard Dirac is $|q_{n-1}...q_0\rangle$. Actually, X(q[1]) flips the 2nd qubit, so state is |0010> if q[0] is LSB, or |0100> if q[0] is MSB. Let's just say "flips q[1] to |1>". So $|0\rangle \otimes |1\rangle \otimes |0\rangle \otimes |0\rangle$.
    *   Apply H to q[1]: state becomes $|0\rangle \otimes |+\rangle \otimes |0\rangle \otimes |0\rangle$.
    *   Measuring all: probabilities are 50% |0000> and 50% for the state where q[1] is 1. The prompt says: "Expected measurement probabilities: {|0000>: 0.5, |0100>: 0.5}". This implies q[1] is the 3rd bit from the right (index 1 from MSB? No, wait. If the string is `0100`, that means the second bit from the left is 1, so it's q[1] if q[0] is MSB, or q[2] if q[0] is LSB. Actually, standard notation in quantum often has q[0] as the rightmost bit. But the problem states `|0100>` for q[1]=1. If q[0] is the rightmost bit (LSB), then the string is `q[3]q[2]q[1]q[0]`. If q[1] is 1, the string is `0100`. This perfectly matches. So $|q_3 q_2 q_1 q_0\rangle$ = $|0100\rangle$).
3.  **Drafting the reasoning**:
    *   Goal: Apply X and H gates to a single target qubit (q[1]) within a 4-qubit register.
    *   Qubits: 4 qubits (`q[0]` to `q[3]`), all measured.
    *   Evolution:
        *   Initial state: |0000>
        *   X on q[1]: Flips the second qubit, resulting in state |0100>.
        *   H on q[1]: Transforms |1> to |-> on q[1]. Wait! H|1> = |->. BUT, wait! H applied to |1> creates $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. The probabilities of measuring $|0\rangle$ and $|1\rangle$ are still 50/50.
        *   Final state: $\frac{1}{\sqrt{2}}(|0000\rangle - |0100\rangle)$.
    *   Probabilities: The amplitudes for |0000> and |0100> are $1/\sqrt{2}$ and $-1/\sqrt{2}$, respectively. Squaring the amplitudes gives a 50% probability for each. (Note: the prompt says {|0000>: 0.5, |0100>: 0.5}, matching this).
4.  **Formatting**: Keep it 3-8 lines, concise, precise.
    *   Line 1: Goal
    *   Line 2: Qubits
    *   Line 3-4: Evolution
    *   Line 5: Probabilities
5.  **Refining the text**:
    ## Reasoning
    1. **Goal**: Apply X and H gates sequentially to q[1] in a 4-qubit register while leaving other qubits in their initial |0> state.
    2. **Qubits**: Requires 4 qubits (q[0] to q[3]), all of

## isqTrain/1545

- task_id: `isqTrain/1545`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1807`

### Prompt

Write isQ code for the following quantum task: Apply X gate to each of 4 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Flip the state of 4 qubits from |0> to |1> using X gates, then measure them.
2. Qubits: 4 qubits are needed, and all are measured.
3. State evolution:
   - Initial state: |0000>
   - X gates applied to each qubit flip their states: X|0> = |1>
   - Final state: |1111>
4. Expected probabilities: Measuring |1111> yields the bitstring 1111 with probability 1.0.

## isqTrain/4219

- task_id: `isqTrain/4219`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1821`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[2];

procedure main() {
    Ry(0.0, q[0]);
    Ry(1.0, q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the measurement output of an isQ circuit.
    *   Circuit:
        
    *   Format Requirements: Step-by-step reasoning using Dirac notation. Concise (3-8 lines). Start with "## Circuit Analysis". End with the predicted probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: |00>
    *   Gate 1: `Ry(0.0, q[0])` -> No-op. $R_y(0) = \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}$. State remains |00>.
    *   Gate 2: `Ry(1.0, q[1])` -> $R_y(\theta) |0\rangle = \cos(\theta/2)|0\rangle + \sin(\theta/2)|1\rangle$.
        *   $\theta = 1.0$.
        *   State on q[1] becomes $\cos(0.5)|0\rangle + \sin(0.5)|1\rangle$.
        *   Combined state: $|0\rangle \otimes (\cos(0.5)|0\rangle + \sin(0.5)|1\rangle) = \cos(0.5)|00\rangle + \sin(0.5)|01\rangle$.
    *   Measurement: `M(q[0])` and `M(q[1])`.
        *   $P(q[0]=0) = 1$, so $q[0]$ is always 0.
        *   $P(q[1]=0) = \cos^2(0.5)$, $P(q[1]=1) = \sin^2(0.5)$.

3.  **Determine Probability Distribution:**
    *   Basis states: |00>, |01>, |10>, |11>.
    *   $P(|00\rangle) = \cos^2(0.5) \approx (0.8775)^2 \approx 0.770$.
    *   $P(|01\rangle) = \sin^2(0.5) \approx (0.4794)^2 \approx 0.230$.
    *   $P(|10\rangle) = 0$.
    *   $P(|11\rangle) = 0$.
    *   Note: Earlier measured qubit is higher bit. `M(q[0])` measured first, `M(q[1])` second.
        *   Wait, isQ reference says "array indexed by measurement bitstring (earlier measured qubit = higher bit)".
        *   `M(q[0])` -> higher bit. `M(q[1])` -> lower bit.
        *   Result 0 (q[0]=0, q[1]=0) is 00 -> 0.
        *   Result 1 (q[0]=0, q[1]=1) is 01 -> 1.
    *   Most likely outcome: `00` (or index 0).

4.  **Draft the Analysis:**
    *   Start with ## Circuit Analysis
    *   Step 1: Initial state is |00>.
    *   Step 2: `Ry(0.0, q[0])` applies identity to q[0], leaving state |00>.
    *   Step 3: `Ry(1.0, q[1])` rotates q[1] around Y-axis by $\theta=1.0$. State evolves to $\cos(0.5)|00\rangle + \sin(0.5)|01\rangle$.
    *   Step 4: Measurements are applied.
    *   Probabilities: $P(00) = \cos^2(0.5) \approx 77.0\%$ and $P(01) = \sin^2(0.5) \approx 23.0\%$. Most likely outcome is 00.

5.  **Refine for Conciseness (Target 3-8 lines):**
    ## Circuit Analysis
    1. Initial state is |00>.
    2. `Ry(0.0, q[0])` does nothing, leaving the state as |00>.
    3. `Ry(1.0, q[1])` rotates q[1] by 1.0

### Reference answer

Dominant output states: |00> with probability ~0.77 each

## isqTrain/3752

- task_id: `isqTrain/3752`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `58`

### Prompt

Code this in isQ: an entangled 2-qubit state by applying Ry(1.500) to q[0] followed by CNOT(q[0], q[1]). This creates cos(θ/2)|00> + sin(θ/2)|11>. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a 2-qubit entangled state of the form $\cos(\theta/2)|00\rangle + \sin(\theta/2)|11\rangle$ using an Ry rotation and a CNOT gate, then measure both.
2. **Qubits**: 2 qubits are needed (`q[0]`, `q[1]`), and both are measured.
3. **Evolution**: 
   - Initial state is $|00\rangle$.
   - Apply `Ry(1.500)` to `q[0]`: evolves to $\cos(0.75)|00\rangle + \sin(0.75)|10\rangle$.
   - Apply `CNOT(q[0], q[1])`: entangles the qubits, resulting in $\cos(0.75)|00\rangle + \sin(0.75)|11\rangle$.
4. **Probabilities**: Measuring yields $P(|00\rangle) = \cos^2(0.75) \approx 0.535369$ and $P(|11\rangle) = \sin^2(0.75) \approx 0.464631$.

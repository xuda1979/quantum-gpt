# ISQ training COT RAG corpus: state_preparation shard 29

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3741

- task_id: `isqTrain/3741`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4669`

### Prompt

Create an isQ quantum circuit that Prepare a 2-qubit product state by applying Ry(1.0) to q[0] and Ry(0.0) to q[1]. Measure both qubits.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Goal: Generate a reasoning section for a given quantum task.
    *   Task: Prepare a 2-qubit product state using Ry(1.0) on q[0] and Ry(0.0) on q[1], then measure both.
    *   predicted output Format: ONLY the reasoning section starting with "## Reasoning".
    *   Constraints: 3-8 lines (since it's a simple circuit), use Dirac notation, be concise.

2.  **Analyze the Circuit / Task:**
    *   Initial state: $|00\rangle$ (implicit for 2 qubits).
    *   Operation 1: $R_y(1.0)$ on $q[0]$.
        *   $R_y(\theta) = e^{-i\theta Y/2} = \cos(\theta/2)I - i\sin(\theta/2)Y = \begin{pmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$.
        *   For $\theta=1.0$, $R_y(1.0) |0\rangle = \cos(0.5)|0\rangle + \sin(0.5)|1\rangle$.
    *   Operation 2: $R_y(0.0)$ on $q[1]$.
        *   $R_y(0.0)$ is Identity. $|0\rangle \to |0\rangle$.
    *   State after rotations: $(\cos(0.5)|0\rangle + \sin(0.5)|1\rangle) \otimes |0\rangle$.
    *   Measurements: Both qubits measured.
    *   Probabilities:
        *   $P(|00\rangle) = \cos^2(0.5) \approx (0.877582)^2 \approx 0.770151$.
        *   $P(|10\rangle) = \sin^2(0.5) \approx (0.479425)^2 \approx 0.229849$.
        *   $P(|01\rangle) = 0, P(|11\rangle) = 0$.

3.  **Draft the Reasoning (Iterative refinement for conciseness):**
    *   *Line 1:* The goal is to prepare a 2-qubit product state by applying $R_y$ rotations and measure both qubits.
    *   *Line 2:* Two qubits, $q[0]$ and $q[1]$, are initialized to $|00\rangle$, and both are measured.
    *   *Line 3:* Applying $R_y(1.0)$ to $q[0]$ rotates it to $\cos(0.5)|0\rangle + \sin(0.5)|1\rangle$, while $R_y(0.0)$ on $q[1]$ leaves it as $|0\rangle$.
    *   *Line 4:* The resulting product state is $(\cos(0.5)|0\rangle + \sin(0.5)|1\rangle) \otimes |0\rangle$.
    *   *Line 5:* Measuring this state yields probabilities $P(|00\rangle) = \cos^2(0.5) \approx 0.770151$ and $P(|10\rangle) = \sin^2(0.5) \approx 0.229849$.

4.  **Check against Constraints:**
    *   Starts with "## Reasoning"? Yes.
    *   Concise (3-8 lines)? Yes, 5 lines.
    *   Uses Dirac notation? Yes.
    *   Code NOT included? Yes.

5.  **Final Polish:**
    Make it look standard and professional.
    ## Reasoning
    1. The goal is to prepare a 2-qubit product state using specified Ry rotations and measure both qubits.
    2. Two qubits are used, both initialized to |00> and both are measured at the end.
    3. Applying Ry(1.0) to q[0] evolves its state to cos(0.5)|0> + sin(0.5)|1>, while Ry(0.0) on q[1] leaves it unchanged as |0>.
    4. The combined system state becomes the product state (cos(0.5)|0> + sin(0.5)|1>) ⊗ |0>.
    5. Consequently, the measurement probabilities are P(|00>) = cos²(0.5)

## isqTrain/4799

- task_id: `isqTrain/4799`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_if_else`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `5620`

### Prompt

Implement the following in isQ: implements: nested if-else variant 1. Declare a global qbit array q of 3 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to implement a nested if-else control flow to conditionally apply quantum gates based on classical variables.
2. The circuit uses 3 global qubits (`q[0]`, `q[1]`, `q[2]`), all of which are measured at the end.
3. The initial quantum state is |000>.
4. Because `a = 0`, the outer `if (a == 1)` condition evaluates to false, completely skipping the nested block containing `H` and `X` gates.
5. The gate `X(q[2])` executes unconditionally, flipping the third qubit and transitioning the state to |001>.
6. Measuring all qubits in the |001> state yields an expected measurement probability of {|001>: 1.0}.

## isqTrain/4210

- task_id: `isqTrain/4210`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `4864`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[5];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[4]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Circuit:**
    *   Qubits: `q[5]` (indices 0 to 4), all initialized to $|0\rangle$.
    *   Initial state: $|00000\rangle$.
    *   Gates:
        *   `H(q[0])`: Apply Hadamard to qubit 0.
        *   `CNOT(q[0], q[1])`: Entangle 0 and 1.
        *   `CNOT(q[1], q[2])`: Entangle 1 and 2.
        *   `CNOT(q[2], q[3])`: Entangle 2 and 3.
        *   `CNOT(q[3], q[4])`: Entangle 3 and 4.
    *   Measurements: All 5 qubits `M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);`

2.  **Step-by-step State Evolution:**
    *   $|\psi_0\rangle = |00000\rangle$
    *   After `H(q[0])`: $|\psi_1\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0000\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + |10000\rangle)$
    *   After `CNOT(q[0], q[1])`: Flips q[1] if q[0] is 1. $|\psi_2\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + |11000\rangle)$
    *   After `CNOT(q[1], q[2])`: Flips q[2] if q[1] is 1. $|\psi_3\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + |11100\rangle)$
    *   After `CNOT(q[2], q[3])`: Flips q[3] if q[2] is 1. $|\psi_4\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + |11110\rangle)$
    *   After `CNOT(q[3], q[4])`: Flips q[4] if q[3] is 1. $|\psi_5\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + |11111\rangle)$

3.  **Measurement Probabilities:**
    *   Final state is a GHZ state: $\frac{1}{\sqrt{2}}(|00000\rangle + |11111\rangle)$.
    *   Measurement outcomes:
        *   $|00000\rangle \rightarrow 00000$ (probability 1/2 = 50%)
        *   $|11111\rangle \rightarrow 11111$ (probability 1/2 = 50%)
    *   Note on bitstrings: Earlier measured qubit = higher bit.
        *   `M(q[0])` -> bit 4
        *   `M(q[1])` -> bit 3
        *   `M(q[2])` -> bit 2
        *   `M(q[3])` -> bit 1
        *   `M(q[4])` -> bit 0
        *   So `00000` is 0, and `11111` is $2^5-1 = 31$.

4.  **Drafting the response:**
    *   Follow the rules: concisely state operations, evolution, final state, distribution.
    *   Keep it to ~5-8 lines.
    *   Format: "## Circuit Analysis" followed by text.

    *   *Draft:*
        ## Circuit Analysis
        1. **Operations:** The circuit initializes 5 qubits in $|0\rangle$, applies a Hadamard gate to `q[0]`, followed by a cascade of CNOT gates from `q[0]` to `q[4]`.
        2. **State Evolution:** The initial state $|00000\rangle$ becomes $\frac{1}{\sqrt{2}}(|00000\rangle + |10000\rangle)$ after H. Each subsequent CNOT copies the control's state to its target, resulting in the GHZ state $\frac{1}{\sqrt{2}}(|00000\rangle + |11111\rangle)$.
        3. **Final State:** The state before measurement is $|\psi\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + |11111

### Reference answer

Dominant output states: |00000>, |11111> with probability ~0.50 each

## isqTrain/4803

- task_id: `isqTrain/4803`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_switch`, `isq_syntax_classical_vars`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `5207`

### Prompt

Help me write isQ code that uses switch-case on a measurement result. Declare 2 global qubits. Set q[0] to |1> with X, measure it into variable x. Use switch(x): case 0 applies Z(q[1]), case 1 applies X(q[1]). Since q[0] is |1>, case 1 executes, flipping q[1] to |1>. Measure q[1]. Expected output: |11>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate classical control flow via switch-case on a measurement result to conditionally operate on a target qubit.
2. **Qubits**: 2 global qubits q[0], q[1]; both are measured (q[0] first, q[1] second).
3. **State evolution**:
   - Initial state: |00⟩
   - After X(q[0]): |10⟩
   - Measure q[0] → x = 1 (deterministic, since q[0] is |1⟩)
   - Switch case 1 executes: X(q[1]) applied
   - After X(q[1]): |11⟩
   - Measure q[1] → result 1
4. **Expected probabilities**: {|11⟩: 1.0} — both measurements yield 1 deterministically, giving bitstring 11 (q[0]=bit1, q[1]=bit0).

## isqTrain/1452

- task_id: `isqTrain/1452`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5180`

### Prompt

请用isQ语言编写一个量子电路：Prepare the computational basis state |1011> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Code generation reasoning.
    *   Goal: Prepare the state |1011> using X gates on a 4-qubit register, then measure.
    *   predicted output: A concise reasoning section starting with "## Reasoning" explaining the state preparation and measurement.
    *   Target State: |1011>.
    *   Format Constraints: Dirac notation, 3-8 lines, no code blocks, NO isQ CODE in output.

2.  **Analyze the Circuit / Problem:**
    *   Qubits: 4 (q[0] to q[3], initialized to |0000>).
    *   Target state: |1011>. Note that bit strings are often represented with q[0] as the rightmost bit or leftmost depending on convention, but standard isQ indexing `q[0]` is the 0th index. Let's look at The implementation: `X(q[0])`, `X(q[2])`, `X(q[3])`.
    *   If `q[0]` is index 0, and we want |1011>, where the highest index is on the left or right? Usually `|q[3]q[2]q[1]q[0]>`. So |1011> means `q[3]=1`, `q[2]=0`, `q[1]=1`, `q[0]=1`.
    *   Wait, The implementation does `X(q[0]); X(q[2]); X(q[3]);`. This flips q[0], q[2], q[3]. So q[0]=1, q[1]=0, q[2]=1, q[3]=1. The state would be |1101> if written as `|q[3]q[2]q[1]q[0]>`. But if written as `|q[0]q[1]q[2]q[3]>`, it's |1011>. Let's trace it exactly as the code does.
    *   Initial state: |0000> (where the kets are `|q[0], q[1], q[2], q[3]>`).
    *   X(q[0]) -> |1000>
    *   X(q[2]) -> |1010>
    *   X(q[3]) -> |1011>

3.  **Draft the Reasoning:**
    *   Goal: Initialize a 4-qubit register to the state |1011> using X gates, then measure all qubits.
    *   Initial state is |0000>. We need to flip qubits 0, 2, and 3 to 1.
    *   Apply X to q[0]: state becomes |1000>.
    *   Apply X to q[2]: state becomes |1010>.
    *   Apply X to q[3]: state becomes |1011>.
    *   Measure all qubits: yields the classical bitstring 1011 with 100% probability.

4.  **Refine for Conciseness (3-8 lines):**
    ## Reasoning
    1.  **Goal:** Prepare the 4-qubit computational basis state |1011> from |0000> and measure it.
    2.  **Qubits:** 4 qubits are needed (`q[0]` to `q[3]`), and all are measured.
    3.  **Evolution:**
        *   Start in |0000> (format |q[0]q[1]q[2]q[3]>).
        *   `X(q[0])` flips the 1st qubit: |0000> → |1000>.
        *   `X(q[2])` flips the 3rd qubit: |1000> → |1010>.
        *   `X(q[3])` flips the 4th qubit: |1010> → |1011>.
    4.  **Probabilities:** The final state is exactly |1011>. Measurement deterministically yields this bitstring with probability 1.0.

5.  **Check Constraints:**
    *   Start with "## Reasoning"? Yes.
    *   Dirac notation used? Yes.
    *   Concise (3-8 lines)? Yes, 8 lines.
    *   No isQ code blocks? Yes.
    *   No isQ code *at all*? The prompt says "Do NOT include the isQ code" and "Do NOT include code blocks". I should probably avoid even mentioning `X(q[0])` in backticks or just use regular text to be safe. "Apply X to q[0]..." is

## isqTrain/3296

- task_id: `isqTrain/3296`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5365`

### Prompt

Write an isQ program that an isQ program: use a for loop to apply X to all 3 qubits, preparing |111>.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare the |111> state from |000> by applying X gates to all 3 qubits.
2. Qubits: 3 qubits declared (q[0], q[1], q[2]), all measured at the end.
3. State evolution:
   - |000> (initial)
   - X(q[0]) → |100>
   - X(q[1]) → |110>
   - X(q[2]) → |111>
4. The X gate flips |0> to |1>, so each qubit transitions deterministically, yielding measurement probability P(|111>) = 1.0.

## isqTrain/3115

- task_id: `isqTrain/3115`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `694`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Rx(2*pi/3) to a single qubit and measure. Expected P(0)=0.2500, P(1)=0.7500.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply an Rx rotation of 2*pi/3 to a single qubit and measure the resulting state.
One qubit is required, which is initialized to |0> and measured at the end.
Applying Rx(2*pi/3) to |0> evolves the state to cos(pi/3)|0> - i*sin(pi/3)|1>.
This yields the final quantum state (1/2)|0> - i*(sqrt(3)/2)|1>.
The probability of measuring |0> is the squared amplitude (1/2)^2 = 0.25.
The probability of measuring |1> is the squared amplitude |-i*sqrt(3)/2|^2 = 3/4 = 0.75.

## isqTrain/1453

- task_id: `isqTrain/1453`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `524`

### Prompt

Write isQ code for the following quantum task: Prepare the computational basis state |1101> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

The user wants to prepare the computational basis state |1101> on 4 qubits.
1. Goal: Prepare state |1101> on 4 qubits using X gates and measure all.
2. Qubits: 4 qubits `q[0]`, `q[1]`, `q[2]`, `q[3]`. All are measured.
3. Evolution:
   - Initial state: |0000>
   - Apply X(q[0]): |0001> (since q[0] is the first qubit, but wait, typically q[0] is the right-most bit in string notation if little-endian is used, or left-most. Let's assume standard notation where q[0] corresponds to the rightmost bit or leftmost. Analyzing the circuit requirements: `X(q[0]); X(q[1]); X(q[3]);` targets q[0], q[1], q[3] to get |1101>. This means q[3] corresponds to the leftmost bit '1', q[2] to '0', q[1] to '1', q[0] to '1'. So the bitstring is q[3]q[2]q[1]q[0] = 1101. Let's trace:
   - |0000>
   - X(q[0]) -> |0001>
   - X(q[1]) -> |0011>
   - X(q[3]) -> |1011> Wait, the bit order in Dirac notation: if q[3] is the leftmost bit, then X(q[3]) changes it from 0 to 1. So |1011> where the bits are q[3]q[2]q[1]q[0]. Wait, the reference says state is |1101> and it applies X to q[0], q[1], q[3].
   Let's check the binary: 1101 is 13.
   If q[0] is LSB: q[0]=1, q[1]=0, q[2]=1, q[3]=1. Wait, 1101 -> q[0]=1, q[1]=0, q[2]=1, q[3]=1.
   Let's look at the reference:
   `X(q[0]); X(q[1]); X(q[3]);`
   If it applies to 0, 1, 3, then q[0]=1, q[1]=1, q[2]=0, q[3]=1.
   Bitstring (q[3]q[2]q[1]q[0]): 1 0 1 1 = |1011>.
   But the prompt says "Prepare state |1101>".
   Wait! 1101 in bits: q[0]=1, q[1]=0, q[2]=1, q[3]=1.
   If it applies X to 0, 2, 3, then state is |1101>.
   Let me read The implementation carefully:
   `X(q[0]); X(q[1]); X(q[3]);`
   Wait, if X is applied to q[0], q[1], q[3], the state is |q[3]q[2]q[1]q[0]> = |1011>.
   But the prompt says: "Prepare state |1101>".
   Is The implementation wrong?
   If q[3]q[2]q[1]q[0] is 1101, then q[3]=1, q[2]=1, q[1]=0, q[0]=1. So X should be applied to q[0], q[2], q[3].
   Wait, let's look at the reference again. circuit implementation:
   `X(q[0]); X(q[1]); X(q[3]);`
   Maybe q[0] is the *left-most* bit? If q[0] is the left-most bit, then |q[0]q[1]q[2]q[3]> = |1101>. Then q[0]=1, q[1]=1, q[2]=0, q[3]=1.
   Then X should be on q[0], q[1], q[3]. This matches The implementation!
   Yes, in many quantum programming languages, q[0] is the leftmost bit.
   But wait, the prompt also says: `--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit).`
   If earlier measured qubit = higher bit, then q[0] is the highest bit.
   So M(q[0]), M(q[1]), M(q[2]), M

## isqTrain/4044

- task_id: `isqTrain/4044`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3071`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// Graph state for line_5 topology
// Edges: [(0, 1), (1, 2), (2, 3), (3, 4)]
qbit q[5];

procedure main() {
    // Step 1: Hadamard on all qubits (|+>^n)
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    H(q[4]);
    // Step 2: CZ for each edge
    CNOT(q[0], q[1]);  // edge (0,1)
    CZ(q[1], q[2]);  // edge (1,2)
    CZ(q[2], q[3]);  // edge (2,3)
    CZ(q[3], q[4]);  // edge (3,4)
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
    M(q[4]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: Line 14 uses `CNOT(q[0], q[1])` instead of `CZ(q[0], q[1])` for edge (0,1). CNOT flips the target qubit when the control is |1>, which modifies the state differently than CZ (which applies a Z-phase).

2. **Fix**: Replace `CNOT(q[0], q[1])` with `CZ(q[0], q[1])`.

3. **State evolution**: Starting from |0⟩^5 → H^⊗5 → |+⟩^5 = (1/√32)∑|x⟩ for all x∈{0,1}^5. Each CZ gate applies a phase of (-1)^(x_i·x_j) for connected vertices. The resulting graph state has equal amplitude (1/√32) for all 32 basis states, yielding measurement probability 0.03125 for each outcome.

## isqTrain/1448

- task_id: `isqTrain/1448`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1472`

### Prompt

用isQ实现Prepare the computational basis state |0110> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the 4-qubit computational basis state |0110⟩.
2. **Qubits:** 4 qubits (q[0] to q[3]) are needed, and all are measured.
3. **Evolution:**
   - Start in the initial state |0000⟩.
   - Apply X gate to q[1]: flips the second qubit, evolving the state to |0010⟩.
   - Apply X gate to q[2]: flips the third qubit, evolving the state to |0110⟩.
4. **Probabilities:** The circuit deterministically produces the pure state |0110⟩. Thus, measurement yields the bitstring '0110' with probability 1.0.

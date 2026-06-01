# ISQ training COT RAG corpus: state_preparation shard 8

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3963

- task_id: `isqTrain/3963`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3247`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// 2-qubit state via Ry rotations: Ry(2.0 * 0.5) ⊗ Ry(0.5)
qbit q[2];

procedure main() {
    // Apply rotations to create product state
    Ry(0.5, q[0]);
    Ry(0.5, q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

The buggy code has:

The comment says `Ry(2.0 * 0.5) ⊗ Ry(0.5)`, suggesting the first rotation should be `Ry(1.0, q[0])` (i.e., `2.0 * 0.5 = 1.0`), but the code applies `Ry(0.5, q[0])`.

Wait, let me re-read. The original task says "2-qubit Ry product state: (0.5, 0.5)". So both parameters should be 0.5. The comment in the buggy code says `Ry(2.0 * 0.5) ⊗ Ry(0.5)` which would mean the first qubit gets `Ry(1.0)` and the second gets `Ry(0.5)`.

But the "corrected" code shows both as `Ry(0.5, q[0])` and `Ry(0.5, q[1])`, and the comment is fixed to `Ry(0.5) ⊗ Ry(0.5)`.

The predicted measurement probabilities are {|00>: 0.881329, |01>: 0.057462, |10>: 0.057462, |11>: 0.003747}.

Let me verify: Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]

For Ry(0.5):
cos(0.25) ≈ 0.9689
sin(0.25) ≈ 0.2474

P(|0>) = cos²(0.25) ≈ 0.9388
P(|1>) = sin²(0.25) ≈ 0.0612

For 2 qubits with same rotation:
P(|00>) = 0.9388² ≈ 0.8813
P(|01>) = 0.9388 × 0.0612 ≈ 0.0575
P(|10>) = 0.0612 × 0.9388 ≈ 0.0575
P(|11>) = 0.0612² ≈ 0.00375

This matches! So The corrected version both Ry(0.5).

But wait, the buggy code ALSO has both Ry(0.5). The comment is wrong in the buggy code but the actual gate parameters are the same in both versions...

Hmm, let me re-read the buggy code more carefully:

Buggy:

Corrected:

These are identical! The only difference is in the comment. The bug in the comment says `Ry(2.0 * 0.5)` but the actual code is `Ry(0.5)`.

Wait, maybe I'm misunderstanding. Perhaps the bug is that the comment describes the wrong intent, or maybe the original buggy code should have been different. Let me re-read...

Actually, looking at this more carefully - the prompt says "The following isQ code has a bug (wrong parameter). Fix the code so it produces the correct output."

the predicted output matches having both qubits with Ry(0.5). The current code already has both Ry(0.5). So maybe the buggy code was supposed to have something different, like Ry(1.0, q[0]) following the comment?

Hmm, but looking at the "correct" code provided, it's the same as the buggy code except for the comment. This is a bit confusing.

Let me reconsider. Perhaps the task description has a typo, and the actual buggy code should have `Ry(1.0, q[0])` to match the comment `Ry(2.0 * 0.5)`. The fix would be changing it to `Ry(0.5, q[0])`.

Given the structure of the task (bug_fix type), the intent seems to be:
- The buggy code has `Ry(0.5, q[0])` and `Ry(0.5, q[1])` but the comment suggests the first should be `Ry(2.0 * 0.5) = Ry(1.0)`
- The correct code should have both as `Ry(0.5)` based

## isqTrain/1442

- task_id: `isqTrain/1442`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3651`

### Prompt

Code this in isQ: Prepare the computational basis state |011> on 3 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the computational basis state |011> on 3 qubits.
2. **Qubits:** 3 qubits are needed (`q[0]`, `q[1]`, `q[2]`), and all are measured.
3. **State Evolution:**
   - Initialize to the ground state: |000>.
   - Apply X gate to `q[1]`, flipping it from |0> to |1>: |010>.
   - Apply X gate to `q[2]`, flipping it from |0> to |1>: |011>.
4. **Probabilities:** Since the final state is deterministically the computational basis state |011>, measurement will yield `011` with a probability of 1.0.

## isqTrain/586

- task_id: `isqTrain/586`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `4572`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[5];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[4]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with all 5 qubits in the initial state |00000>.
2. Applying H(q[0]) puts the first qubit into

### Reference answer

{'predicted_probs': {'0': 0.5, '31': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/195. Dimension: predict probabilities for reference circuit.'}

## isqTrain/563

- task_id: `isqTrain/563`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4964`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[5];

procedure main() {
    X(q[0]);
    X(q[3]);
    M(q);
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program and predict the probability distribution of measurement outcomes.
The program has 5 qubits initialized to $|0\rangle$.
$X(q[0])$ is applied.
$X(q[3])$ is applied.
Then all 5 qubits are measured.

Let's trace the states:
Initial state: $|00000\rangle$ (Note: in standard quantum notation, usually $q_0$ is the first qubit, $q_4$ is the last. But let's check the output indexing). The prompt specifies "earlier measured qubit = higher bit" in --probs output. Since `M(q)` is used, it measures `q[0]` to `q[4]` in order. Wait, the prompt circuit implementation says `{|01001>: 1.0}`.
Let's see: $q[0]$ gets X gate -> state $|1\rangle$.
$q[3]$ gets X gate -> state $|1\rangle$.
Initial: $q[4]q[3]q[2]q[1]q[0] = |00000\rangle$.
After X(q[0]): $q_0 = 1 \implies |00001\rangle$.
After X(q[3]): $q_3 = 1 \implies |01001\rangle$.
Wait, $q[4]q[3]q[2]q[1]q[0]$. If $q[3]=1$, the 5-bit string is $01001$.
Bit 0: 1 (from q[0])
Bit 1: 0 (from q[1])
Bit 2: 0 (from q[2])
Bit 3: 1 (from q[3])
Bit 4: 0 (from q[4])
So the string is `10010`? No.
circuit implementation says `{|01001>: 1.0}`.
Wait, let's write out `01001` in bits from high to low.
Bit 4: 0
Bit 3: 1
Bit 2: 0
Bit 1: 0
Bit 0: 1
So it matches exactly my state $q_3=1, q_0=1$.
Wait, earlier measured qubit = higher bit.
`M(q)` measures `q[0]`, then `q[1]`, ..., `q[4]`.
So `q[0]` is the highest bit.
Let's check: if `q[0]` is highest bit, then the bitstring is `q[0]q[1]q[2]q[3]q[4]`.
If $q_0=1$ and $q_3=1$, the string is `10010`.
Wait, why does the reference say `{|01001>: 1.0}`?
Ah, `q[0]` is the highest bit, so if $q_0=1$ and $q_3=1$, then `q[0]q[1]q[2]q[3]q[4]` = `10010`.
But reference says `{|01001>: 1.0}`.
Could it be `q[4]` is the highest bit?
If earlier measured qubit = higher bit, `M(q)` measures `q[0]` first. So `q[0]` is the highest bit.
Wait! Look at the reference: `Expected measurement probabilities: {|01001>: 1.0}`.
Is it possible that it's `q[0]q[1]q[2]q[3]q[4]`? Yes, `10010`. Wait, `01001` is 9 in decimal. `10010` is 18 in decimal.
Wait! Maybe X gate was applied to `q[0]` and `q[3]`, but `q` is indexed 0 to 4.
Wait, `01001` means `q[0]=0`, `q[1]=1`, `q[2]=0`, `q[3]=0`, `q[4]=1`.
Let me count again.
In `01001`:
Index 0: '0'
Index 1: '1'
Index 2: '0'
Index 3: '0'
Index 4: '1'
So `q[0]=0`, `q[1]=1`, `q[2]=0`, `q[3]=0`, `q[4]=1`.
But the code applies X to `q[0]` and `q[3]`.
If earlier measured qubit is higher bit, `q[0]` is measured first, so it's the highest bit

### Reference answer

{'predicted_probs': {'9': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/182. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3297

- task_id: `isqTrain/3297`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1911`

### Prompt

I need an isQ program to an isQ program: use a for loop to apply X to all 4 qubits, preparing |1111>.

### Chain-of-thought reasoning

## Reasoning
The goal is to prepare the 4-qubit state |1111> by applying X gates to all qubits initialized to |0000>.
Four qubits are required, and all four are measured at the end.
The system starts in the state |0000>. The for loop applies an X gate to each qubit sequentially.
Since X|0> = |1>, each gate flips its target qubit, evolving the state to |1111>.
Because the final state is exactly |1111>, measuring the qubits yields the bitstring 1111 with a probability of 1.0.

## isqTrain/4856

- task_id: `isqTrain/4856`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2916`

### Prompt

请用isQ语言编写一个量子电路：measuring q[0] and q[2] of 3 qubits, skipping q[1]. Apply H to all, measure q[0] and q[2].

### Chain-of-thought reasoning

## Reasoning
*   **Goal:** Apply Hadamard gates to 3 qubits to create superposition, then selectively measure only q[0] and q[2].
*   **State Evolution:** Starting from $|000\rangle$, applying an H gate to each qubit yields the state $|+++\rangle = \frac{1}{2\sqrt{2}} \sum_{x=0}^{7} |x\rangle$.
*   **Probabilities:** Since all qubits are in completely independent, equal superpositions, tracing out (ignoring) the unmeasured q[1] leaves q[0] and q[2] in a uniform product state. Measuring these two qubits yields the four possible outcomes $|00\rangle$, $|01\rangle$, $|10\rangle$, and $|11\rangle$, each with a probability of exactly 0.25.<|user|>

## isqTrain/4222

- task_id: `isqTrain/4222`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5188`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[2];

procedure main() {
    Ry(1.0, q[0]);
    Ry(1.0, q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the measurement output of a given isQ circuit.
    *   Input: A simple 2-qubit circuit with `Ry(1.0, q[0])` and `Ry(1.0, q[1])`.
    *   Constraints: 3-8 lines for simple circuits. Use Dirac notation. no code blocks. Start with "## Circuit Analysis". End with probability distribution.

2.  **Analyze the Circuit:**
    *   Qubits: `q[2]` initialized to |00>.
    *   Gates:
        *   `Ry(1.0, q[0])` applies rotation around Y axis by angle 1.0 radians on q[0].
        *   `Ry(1.0, q[1])` applies rotation around Y axis by angle 1.0 radians on q[1].
    *   Measurement: `M(q[0])`, `M(q[1])` measures both qubits.

3.  **Trace the State Evolution:**
    *   Initial state: |00>
    *   After `Ry(1.0, q[0])`: $\cos(0.5)|0\rangle + \sin(0.5)|1\rangle$ for q[0]. Since $1.0$ is roughly $57.3^\circ$ or $\pi/3.14$, $\cos(0.5) \approx \cos(0.5) \approx 0.877$, $\sin(0.5) \approx 0.479$.
    *   After `Ry(1.0, q[1])`: $\cos(0.5)|0\rangle + \sin(0.5)|1\rangle$ for q[1].
    *   Final state: $|\psi\rangle = (\cos(0.5)|0\rangle + \sin(0.5)|1\rangle) \otimes (\cos(0.5)|0\rangle + \sin(0.5)|1\rangle)$
    *   $|\psi\rangle = \cos^2(0.5)|00\rangle + \cos(0.5)\sin(0.5)|01\rangle + \sin(0.5)\cos(0.5)|10\rangle + \sin^2(0.5)|11\rangle$.

4.  **Calculate Probabilities:**
    *   $P(00) = \cos^2(0.5) \approx 0.877^2 \approx 0.769$
    *   $P(11) = \sin^2(0.5) \approx 0.479^2 \approx 0.230$
    *   $P(01) = P(10) = \cos(0.5)\sin(0.5) = 0.5 \sin(1.0) \approx 0.5 \times 0.841 \approx 0.420$
    *   Wait, the sum must be 1. $0.769 + 0.230 + 2(0.420) = 1.839 \neq 1$.
    *   Let me re-evaluate trig values:
        *   $0.5$ radians. $\cos(0.5) \approx 0.87758$. $\sin(0.5) \approx 0.47942$.
        *   $\cos^2(0.5) \approx 0.770$
        *   $\sin^2(0.5) \approx 0.229$
        *   $\cos(0.5)\sin(0.5) = 0.5 \sin(1.0) \approx 0.420$.
        *   Sum: $0.770 + 0.229 + 2 \times 0.420 = 1.839 \neq 1$.
    *   ERROR IN CALCULATION:
        *   $0.87758^2 \approx 0.7701$
        *   $0.47942^2 \approx 0.2298$
        *   $2 \times 0.87758 \times 0.47942 = 0.4207$
        *   $0.7701 + 0.2298 + 0.4207 + 0.4207 = 1.8413$??
        *   Let me check $A^2 + 2AB + B^2 = (A+B)^2$.
        *   $(\cos(0.5

### Reference answer

Dominant output states: |00> with probability ~0.59 each

## isqTrain/3206

- task_id: `isqTrain/3206`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `807`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply Ry(4*pi/5) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply an Ry(4*pi/5) rotation to a single qubit and measure the resulting quantum state.
2. **Qubits:** The circuit uses 1 qubit, which is measured at the end.
3. **Evolution:** Starting in the initial state |0>, the Ry(4*pi/5) gate rotates the state around the Y-axis, evolving it to cos(2*pi/5)|0> + sin(2*pi/5)|1>.
4. **Probabilities:** The measurement probabilities are determined by the squared

## isqTrain/4722

- task_id: `isqTrain/4722`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3712`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial state**: The system begins in the |00> state.
2. **H(q[0])**: Applies a Hadamard gate to qubit 0, evolving the state to (|00> + |10>) / √2.
3. **CNOT(q[0], q[1])**: Entangles the two qubits, resulting in the Bell state (|00> + |11>) / √2.
4. **X(q[0])**: Flips the state of qubit 0, changing the state to (|10> + |01>) / √2.
5. **Measurement**: Measuring yields the states |01> and |10> with equal probability.

Predicted probability distribution: {|01>: 0.5, |10>: 0.5}

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 0.5000, P(|10>) = 0.5000.'}

## isqTrain/4719

- task_id: `isqTrain/4719`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1829`

### Prompt

判断以下两段isQ代码是否产生相同的测量结果：

代码1：
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    M(q[0]); M(q[1]);
}

```

代码2：
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A:**
    *   Initializes 2 qubits: $|00\rangle$.
    *   Applies `X(q[0])` and `X(q[1])`.
    *   `X` gate flips $|0\rangle$ to $|1\rangle$.
    *   State becomes $|11\rangle$.
    *   Measures both: P('11') = 1.0.

2.  **Analyze Program B:**
    *   Initializes 2 qubits: $|00\rangle$.
    *   Applies `H(q[0])`.
    *   State becomes $|+\rangle \otimes |0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   Applies `CNOT(q[0], q[1])`.
    *   Control is q[0], target is q[1].
    *   State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
    *   Measures both: P('00') = 0.5, P('11') = 0.5.

3.  **Compare and contrast:**
    *   Program A yields deterministic measurement: 100% '11'.
    *   Program B yields Bell state, probabilistic measurement: 50% '00', 50% '11'.
    *   the predicted output note says "Bell state P(00)=P(11)=0.5 vs deterministic |11> Program A produces {'00': 0.5, '11': 0.5} while Program B produces {'11': 1.0}." The predicted output note seems to have reversed Program A and B in its explanation string! "Bell state P(00)=P(11)=0.5 vs deterministic |11> Program A produces {'00': 0.5, '11': 0.5} while Program B produces {'11': 1.0}."
    *   Wait, look at the prompt's predicted output:
        `predicted output: Equivalent: False`
        `Explanation: Bell state P(00)=P(11)=0.5 vs deterministic |11> Program A produces {'00': 0.5, '11': 0.5} while Program B produces {'11': 1.0}.`
        This text from the prompt contains a logical error in its own explanation (it says Program A produces {'00': 0.5, '11': 0.5} but Program A has X gates!).
        I will correct the analysis based on actual quantum mechanics:
        Program A applies two X gates, yielding $|11\rangle$, so P('11') = 1.0.
        Program B applies H and CNOT, yielding $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$, so P('00') = P('11') = 0.5.

4.  **Draft the response:**
    *   **Equivalence Analysis**
    *   1. Program A applies `X` gates to both qubits $q_0$ and $q_1$, transforming the initial state $|00\rangle$ to $|11\rangle$.
    *   2. Program B applies an `H` gate to $q_0$ followed by a `CNOT` with control $q_0$ and target $q_1$, creating the Bell state $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
    *   3. The key difference is that Program A creates a deterministic computational basis state, while Program B creates an entangled superposition.
    *   4. The measurement probabilities differ: Program A yields `{'11': 1.0}`, whereas Program B yields `{'00': 0.5, '11': 0.5}`.
    *   5. Verdict: Not equivalent.

5.  **Refine based on constraints:**
    *   "3-8 lines for simple circuits, up to 15 for complex ones."
    *   "Output ONLY the analysis, starting with "## Equivalence Analysis""
    *   "End with a clear "Yes/No" verdict line"
    *   "Do NOT include code blocks"
    *   Use Dirac notation.

6.  **Formatting exactly as requested:**
    ## Equivalence Analysis
    1. Program A applies X gates to both q[0] and q[1], changing the state from |00> to |11>.
    2. Program B applies an H gate to q

### Reference answer

{'equivalent': False, 'explanation': "Bell state P(00)=P(11)=0.5 vs deterministic |11> Program A produces {'00': 0.5, '11': 0.5} while Program B produces {'11': 1.0}.", 'probs_a': {'11': 1.0}, 'probs_b': {'00': 0.5, '11': 0.5}}

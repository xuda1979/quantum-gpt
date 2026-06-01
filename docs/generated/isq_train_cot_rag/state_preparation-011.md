# ISQ training COT RAG corpus: state_preparation shard 11

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1752

- task_id: `isqTrain/1752`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4958`

### Prompt

请用isQ语言编写一个量子电路：Prepare a 8-qubit GHZ state: (|00000000> + |11111111>) / sqrt(2). Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare an 8-qubit GHZ state (|00000000⟩ + |11111111⟩)/√2, then measure all qubits.
2. **Qubits**: 8 qubits required; all 8 are measured.
3. **State evolution**:
   - Start: |00000000⟩
   - H(q[0]): (|00000000⟩ + |10000000⟩)/√2
   - CNOT(q[0]→q[1]): (|00000000⟩ + |11000000⟩)/√2
   - CNOT(q[0]→q[2]): (|00000000⟩ + |11100000⟩)/√2
   - CNOT(q[0]→q[3]): (|00000000⟩ + |11110000⟩)/√2
   - CNOT(q[0]→q[4]): (|00000000⟩ + |11111000⟩)/√2
   - CNOT(q[0]→q[5]): (|00000000⟩ + |11111100⟩)/√2
   - CNOT(q[0]→q[6]): (|00000000⟩ + |11111110⟩)/√2
   - CNOT(q[0]→q[7]): (|00000000⟩ + |11111111⟩)/√2
4. **Probabilities**: Equal amplitudes ±1/√2 yield P(|00000000⟩) = 0.5, P(|11111111⟩) = 0.5.

## isqTrain/3295

- task_id: `isqTrain/3295`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4022`

### Prompt

Help me write isQ code that an isQ program: use a for loop to apply X to all 2 qubits, preparing |11>.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare the 2-qubit state |11⟩ by applying X gates to both qubits via a for loop.
Two qubits q[0] and q[1] are allocated; both are measured.
State evolution: |00⟩ →(X on q[0])→ |10⟩ →(X on q[1])→ |11⟩.
Since both qubits are deterministically flipped to |1⟩, measurement yields |11⟩ with probability 1.0.

## isqTrain/4748

- task_id: `isqTrain/4748`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2090`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    H(q[1]);
    M(q[0]); M(q[1]);
}

```

Second program:
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

1.  **Analyze Program A**:
    *   Initial state: $|00\rangle$
    *   `H(q[0])` -> $(|0\rangle + |1\rangle)/\sqrt{2} \otimes |0\rangle = (|00\rangle + |10\rangle)/\sqrt{2}$
    *   `H(q[1])` -> $(|0\rangle + |1\rangle)/\sqrt{2} \otimes (|0\rangle + |1\rangle)/\sqrt{2} = (|00\rangle + |01\rangle + |10\rangle + |11\rangle)/2$
    *   Measurement probabilities: $P(00)=0.25, P(01)=0.25, P(10)=0.25, P(11)=0.25$.

2.  **Analyze Program B**:
    *   Initial state: $|00\rangle$
    *   `H(q[0])` -> $(|00\rangle + |10\rangle)/\sqrt{2}$
    *   `CNOT(q[0], q[1])` -> $(|00\rangle + |11\rangle)/\sqrt{2}$ (Bell state)
    *   Measurement probabilities: $P(00)=0.5, P(11)=0.5, P(01)=0, P(10)=0$.

3.  **Compare the two**:
    *   Program A creates an unentangled product state $(|+\rangle \otimes |+\rangle)$, yielding equal 25% probabilities for 00, 01, 10, 11.
    *   Program B creates an entangled Bell state $(|\Phi^+\rangle)$, yielding 50% for 00 and 50% for 11.
    *   Wait, look at the predicted output! "Program A produces {'00': 0.5, '11': 0.5} while Program B produces {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}."
    *   Let me re-read the predicted output carefully. "Program A produces {'00': 0.5, '11': 0.5} while Program B produces {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}."
    *   Wait! the predicted output has the states swapped in the text description, but the probabilities align with the actual programs.
    *   Wait, let me double check the predicted output: "Program A produces {'00': 0.5, '11': 0.5} while Program B produces {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}." - This text in the prompt's "predicted output" actually swapped A and B by mistake in the prompt generation, or maybe it meant Program A is the one with CNOT?
    *   Let's look at Program A: H(q[0]), H(q[1]). Probabilities: 0.25 for all.
    *   Program B: H(q[0]), CNOT(q[0], q[1]). Probabilities: 0.5 for 00, 0.5 for 11.
    *   I must provide the CORRECT analysis matching the programs, even if the prompt's predicted output swapped the descriptions. The prompt explicitly asks to "Explain your reasoning." I will state the correct probabilities for each program.
    *   Program A creates $|+\rangle|+\rangle$ (uniform distribution). Program B creates a Bell state $|\Phi^+\rangle$ (correlated).
    *   Let's re-read the predicted output: "Bell state has correlated outcomes, product state has independent 50/50 Program A produces {'00': 0.5, '11': 0.5} while Program B produces {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}."
    *   Ah, this is likely an error in the predicted output's text, where A and B are flipped. But I will write the accurate description of Program A and B.
    *   Actually, wait. Is it possible that `q[0]` is the lower bit and `q[1]` is the higher bit? Yes, but both are uniform or both entangled, so the actual sets of probabilities are what matter. Program A: {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}. Program B: {'

### Reference answer

{'equivalent': False, 'explanation': "Bell state has correlated outcomes, product state has independent 50/50 Program A produces {'00': 0.5, '11': 0.5} while Program B produces {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}.", 'probs_a': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'probs_b': {'00': 0.5, '11': 0.5}}

## isqTrain/4780

- task_id: `isqTrain/4780`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `3304`

### Prompt

Write isQ code for the following quantum task: implements: for-loop X on 5 qubits -> all |1>. Declare a global qbit array q of 5 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X gates via for-loop to 5 qubits, flipping each from |0⟩ to |1⟩, yielding |11111⟩ with certainty.
2. **Qubits**: 5 global qubits `q[5]`, all measured.
3. **State evolution**: Initial state |00000⟩ → X(q[0]) gives |10000⟩ → X(q[1]) gives |11000⟩ → X(q[2]) gives |11100⟩ → X(q[3]) gives |11110⟩ → X(q[4]) gives |11111⟩.
4. **Expected probabilities**: All qubits are in |1⟩, so measurement yields |11111⟩ with probability 1.0; all other outcomes have probability 0.

## isqTrain/591

- task_id: `isqTrain/591`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `1282`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[6];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[4]);
    CNOT(q[4], q[5]);
    M(q);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ program, predict probability distribution.
    *   Input program: Applies H to q[0], then a chain of CNOTs (q[0]->q[1]->q[2]->q[3]->q[4]->q[5]). Measures all 6 qubits.
    *   Constraints: "Circuit Analysis" format, Dirac notation, concise (3-15 lines), end with predicted probability distribution. no code blocks. Output ONLY the analysis.

2.  **Analyze the Circuit:**
    *   Initial state: $|000000\rangle$
    *   H(q[0]): Transforms $|0\rangle$ to $(|0\rangle + |1\rangle)/\sqrt{2}$. State: $\frac{1}{\sqrt{2}}(|000000\rangle + |100000\rangle)$
    *   CNOT(q[0], q[1]): Entangles q[0] and q[1]. State: $\frac{1}{\sqrt{2}}(|000000\rangle + |110000\rangle)$
    *   CNOT(q[1], q[2]): State: $\frac{1}{\sqrt{2}}(|000000\rangle + |111000\rangle)$
    *   CNOT(q[2], q[3]): State: $\frac{1}{\sqrt{2}}(|000000\rangle + |111100\rangle)$
    *   CNOT(q[3], q[4]): State: $\frac{1}{\sqrt{2}}(|000000\rangle + |111110\rangle)$
    *   CNOT(q[4], q[5]): State: $\frac{1}{\sqrt{2}}(|000000\rangle + |111111\rangle)$
    *   Measurement: Measures all qubits. Outcomes are either all 0s or all 1s with equal probability (50% each).

3.  **Draft the Response:**
    *   *Step 1 (Operations)*: The circuit initializes 6 qubits in |0>, applies a Hadamard (H) gate to q[0], followed by a chain of CNOT gates propagating entanglement from q[0] to q[5].
    *   *Step 2 (Evolution)*:
        *   Initial state: |000000>.
        *   H(q[0]) creates a superposition: (1/√2)(|000000> + |100000>).
        *   The CNOT chain entangles all qubits, propagating the |1> state: (1/√2)(|000000> + |110000>) -> ... -> (1/√2)(|000000> + |111111>).
    *   *Step 3 (Final state)*: The GHZ state (1/√2)(|000000> + |111111>).
    *   *Step 4 (Probabilities)*: Measuring this state collapses it to either |000000> or |111111>, each with a 50% probability.
    *   *Ending*: Predicted probability distribution: {|000000>: 0.5, |111111>: 0.5}

4.  **Refine and Format:**
    *   Keep it concise.
    *   Start with "## Circuit Analysis".
    *   End with "Predicted probability distribution: {|000000>: 0.5, |111111>: 0.5}".

    *Drafting the actual text:*
    ## Circuit Analysis
    1. **Operations:** The circuit initializes 6 qubits in |0>, applies an H gate to `q[0]`, and cascades CNOT gates from `q[0]` to `q[5]`.
    2. **State Evolution:**
       - Initial state: |000000>.
       - H(q[0]) creates a superposition: (1/√2)(|000000> + |100000>).
       - The subsequent CNOT gates propagate the |1> state, entangling all qubits. Each CNOT(control, target) flips the target when the control is |1>, evolving the state to (1/√2)(|000000> + |111111>).
    3. **Final State:** The system is in the 6-qubit GHZ state: (|000000> + |111111>)/√2.
    4. **Probabilities:** Because the superposition only consists of |000000> and |111111>, measuring the qubits will result in either all 0s or all 1s.

    Predicted probability distribution: {|000000>: 0.5, |111111>:

### Reference answer

{'predicted_probs': {'0': 0.5, '63': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/196. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3921

- task_id: `isqTrain/3921`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2282`

### Prompt

Fix the bug in this quantum program:

```
import std;
// Graph state for star_5 topology
// Edges: [(0, 1), (0, 2), (0, 3), (0, 4)]
qbit q[5];

procedure main() {
    // Step 1: Hadamard on all qubits (|+>^n)
    H(q[0]);
    X(q[1]);
    H(q[2]);
    H(q[3]);
    H(q[4]);
    // Step 2: CZ for each edge
    CZ(q[0], q[1]);  // edge (0,1)
    CZ(q[0], q[2]);  // edge (0,2)
    CZ(q[0], q[3]);  // edge (0,3)
    CZ(q[0], q[4]);  // edge (0,4)
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
1. **Bug**: Line 9 applies `X(q[1])` instead of `H(q[1])`. The comment says "Hadamard on all qubits," but qubit 1 gets an X gate, preparing it in |1⟩ instead of |+⟩.

2. **Fix**: Replace `X(q[1])` with `H(q[1])` so all five qubits are initialized to |+⟩ before entanglement.

3. **State evolution (corrected)**: All qubits start in |0⟩^⊗5 → H on all yields |+⟩^⊗5 → Four CZ gates along edges (0,1),(0,2),(0,3),(0,4) produce the star-5 graph state → Measurement gives uniform distribution over all 32 basis states (each with probability 1/32 = 0.03125), confirming the correct graph state.

## isqTrain/3193

- task_id: `isqTrain/3193`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3105`

### Prompt

帮我写一个isQ程序：an isQ program: apply Ry(7*pi/10) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Create a partially entangled two-qubit state using Ry rotation followed by CNOT.

**Qubits**: 2 qubits (q[0], q[1]), both measured.

**State evolution**:
1. Initial state: |00⟩
2. After Ry(7π/10) on q[0]: cos(7π/20)|00⟩ + sin(7π/20)|10⟩, since Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
3. After CNOT(q[0], q[1]): cos(7π/20)|00⟩ + sin(7π/20)|11⟩ — CNOT maps |10⟩ → |11⟩

**Probabilities**: P(|00⟩) = cos²(7π/20) ≈ 0.2061, P(|11⟩) = sin²(7π/20) ≈ 0.7939. The state is a non-maximally entangled Bell-like state with ~79% weight on |11⟩.

## isqTrain/1783

- task_id: `isqTrain/1783`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4453`

### Prompt

Implement the following in isQ: Apply H then Z to each of 4 qubits. Measure all. Z phase is invisible in Z-basis measurement.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H then Z to 4 qubits, measuring all in the Z-basis.
2. **Qubits**: 4 qubits (q[0]–q[3]), all measured.
3. **State evolution**: |0000⟩ → H⊗4 → (1/4)Σ|x⟩ (equal superposition over all 16 basis states) → Z⊗4 → (1/4)Σ(-1)^{|x|}|x⟩, where |x| counts the 1s in bitstring x.
4. **Why probabilities**: Z gates only introduce phase factors (±1), which are squared away in measurement probabilities; all 16 outcomes remain equally likely at 1/16 = 0.0625.

## isqTrain/3882

- task_id: `isqTrain/3882`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2292`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```
import std;
// Entangled 2-qubit state via Ry(2.0 * 0.500) + CNOT
qbit q[2];

procedure main() {
    // Create entangled state
    Ry(0.500, q[0]);
    CNOT(q[0], q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

The buggy code has:

But the comment says "Ry(2.0 * 0.500)" which would be Ry(1.000). However, looking at the "correct" fixed code, it says:

Wait, that's the same. Let me re-read.

The expected measurement probabilities are: {|00>: 0.938791, |11>: 0.061209}

Let me check: Ry(θ) rotates |0⟩ towards |1⟩. After Ry(θ, q[0]), the state is:
cos(θ/2)|0⟩ + sin(θ/2)|1⟩

For θ = 0.500:
cos(0.250) = cos(0.25) ≈ 0.9689
sin(0.250) = sin(0.25) ≈ 0.2474

Prob of |0⟩ = cos²(0.25) ≈ 0.9388
Prob of |1⟩ = sin²(0.25) ≈ 0.0612

So after CNOT, if q[0] is |0⟩, q[1] stays |0⟩; if q[0] is |1⟩, q[1] becomes |1⟩.

So measurement probabilities: |00⟩: 0.9388, |11⟩: 0.0612. This matches!

So the "correct" code with Ry(0.500) produces the predicted output. But the buggy code also has Ry(0.500). Wait, let me re-read the buggy code more carefully.

Oh wait, I see the comment in the buggy code says "Ry(2.0 * 0.500)" suggesting it should be Ry(1.000). But the actual code says Ry(0.500). 

Hmm, but then the "fixed" code also says Ry(0.500) with a different comment. the predicted output matches Ry(0.500).

Wait, I'm confused. Let me re-read:

Buggy code comment: `// Entangled 2-qubit state via Ry(2.0 * 0.500) + CNOT`
Buggy code line: `Ry(0.500, q[0]);`

Fixed code comment: `// Entangled 2-qubit state via Ry(0.500) + CNOT`
Fixed code line: `Ry(0.500, q[0]);`

They're the same code! That can't be right. Unless the bug is that the comment describes the wrong thing but the code is correct... but that doesn't make sense as a bug fix.

Hmm, wait. Maybe I'm misreading. Let me look again at the buggy code more carefully:

Actually, maybe the buggy code has `Ry(1.000, q[0])` (matching the comment `2.0 * 0.500`) and the fix changes it to `Ry(0.500, q[0])`. Let me re-read the prompt.

The buggy code block shows:

And the corrected version also shows:

These look identical. This is strange. 

Actually, looking more carefully at the original prompt structure - the user shows me the buggy code twice (once in the initial prompt and once in the "Buggy code" section), and then shows the "correct (fixed) code." Perhaps there's a subtle difference I'm missing, or perhaps the bug is just the comment being wrong (claiming 2.0 * 0.500 = 1.000 but the code says 0.500).

Hmm, but the task says "wrong parameter" bug type. Let me think about this differently.

Wait - maybe the buggy code actually has `Ry(1.000, q[0])` (i.e., 2.0 * 0.500 = 1.0) and it should be `Ry(0.500, q[0])`. The rendering might have a copy-paste issue.

Let me verify: If Ry(1.000), then:
cos(0.5) ≈ 0.8776
sin(0.5) ≈ 0.4794
P(|00⟩) = cos²(0.5) ≈ 0.7702
P(|11⟩) = sin²(0.5) ≈ 0.2298

That doesn't match the predicted output of {|00>: 0.938791, |11>: 0.061209}.

For Ry(

## isqTrain/4771

- task_id: `isqTrain/4771`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `1466`

### Prompt

Code this in isQ: implements: classical var variant 1. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate classical variable usage to conditionally apply a Hadamard gate on a single qubit.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Initial: |0⟩
   - Classical check `val > 1` (2 > 1) is true → apply H(q[0])
   - After H: (|0⟩ + |1⟩)/√2 = |+⟩
4. **Measurement**: The |+⟩ state yields equal probability of |0⟩ and |1⟩, giving P(|0⟩) = 0.5 and P(|1⟩) = 0.5.

# ISQ training COT RAG corpus: gate_decomposition shard 15

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/606

- task_id: `isqTrain/606`
- task_type: `output_prediction`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3040`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[5];

procedure main() {
    X(q[0]);
    SWAP(q[0], q[4]);
    SWAP(q[1], q[3]);
    M(q);
}
```

### Chain-of-thought reasoning

Step 1: Initial state is |00000>.
Step 2: X(q[0]) flips q[0] to |1>, changing the state to |10000>.
Step 3: swap (three-CNOT decomposition)(q[0], q[4]) swaps the states of q[0] and q[4]. Since q[0] was |1> and q[4] was |0>, the state becomes |00001>.
Step 4: swap (three-CNOT decomposition)(q[1], q[3]) swaps the states of q[1] and q[3]. Since both are |0>, the state remains |00001>.
Wait, let me double check the bitstring representation.
Usually bitstrings are read left-to-right as q[0], q[1], ..., q[N-1] or q[N-1] down to q[0].
The prompt asks for probability distribution in format like {|10000>: 1.0} but wait, The implementation says `Expected measurement probabilities: {|10000>: 1.0}`. Wait, The implementation says `Expected measurement probabilities: {|10000>: 1.0}`.
Let's trace:
Initial: |00000>
X(q[0]) -> |10000>
swap (three-CNOT decomposition)(q[0], q[4]) -> state moves from q[0] to q[4], so q[4] is 1, q[0] is 0. The state is |00001>. But wait, in bitstrings, usually q[0] is the rightmost bit (least significant).
If q[4]=1, q[0]=0, then in integer form it is 10000 (binary, where q[4] is MSB).
Ah! `q[0]` is swapped with `q[4]`. So `q[4]` becomes 1.
Wait, if the bitstring is `10000`, does it mean q[4]=0, q[3]=0, q[2]=0, q[1]=0, q[0]=1?
Yes! The implementation expects `{|10000>: 1.0}`. This implies `1` is at the first position, which is `q[0]`.
Wait, if `swap (three-CNOT decomposition)(q[0], q[4])` swaps them, `q[0]` becomes 0 and `q[4]` becomes 1. Then the state should be `00001` (where q[0] is left-most? No, if q[0] is left-most, it's `00001` where q[0]=0, q[4]=1. But wait, if the bitstring is `10000`, then q[0] must be 1!)
Let me re-read the code.
Wait! Does swap (three-CNOT decomposition)(q[0], q[4]) change the indices or just swap the states?
Ah! If the array is `q[5]`, swap (three-CNOT decomposition)(q[0], q[4]) swaps the *qubits* themselves. Or does it?
No, `swap (three-CNOT decomposition)` gate swaps the states of two qubits.
If initial state is |00000>.
X(q[0]) -> q[0] becomes 1. State is |00001> (where q[4] is MSB, q[0] is LSB).
Then swap (three-CNOT decomposition)(q[0], q[4]) swaps the states of q[0] and q[4]. So q[4] becomes 1, q[0] becomes 0. State is |10000>.
Then swap (three-CNOT decomposition)(q[1], q[3]) swaps the states of q[1] and q[3]. Both are 0. State remains |10000>.
So the final state is |10000>.
Ah, the bitstring `10000` means q[4]=1, q[3]=0, q[2]=0, q[1]=0, q[0]=0. Which evaluates to the integer 16.
Let me check standard notation: bitstring "10000" means MSB is 1, which is q[4] in some notations, or q[0] in others.
In the `--probs` output, the prompt says: "array indexed by measurement bitstring (earlier measured qubit = higher bit)."
If we measure `q`, it measures `q[0]`, `q[1]`, ..., `q[4]`.
"earlier measured qubit = higher bit."
So `q[0]` is measured first, so `q[0]` is the highest bit.
If `q[0]` is the highest bit, then bitstring is `q[0] q[1] q[2] q[3] q[4]`.
Wait, if X(q[0]) flips q[0] to 1, then `q

### Reference answer

{'predicted_probs': {'16': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/204. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3284

- task_id: `isqTrain/3284`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `451`

### Prompt

帮我写一个isQ程序：an isQ program: apply Rx(1*pi/3) then Rx(-1*pi/3) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

Let me analyze this circuit:

1. Goal: Apply Rx(π/3) then Rx(-π/3) to demonstrate cancellation, resulting in |0⟩.

2. Qubits: 1 qubit (q[0]), which is measured.

3. State evolution:
   - Initial state: |0⟩
   - After Rx(π/3): The Rx gate rotates around the X-axis by angle π/3. Starting from |0⟩, this creates a superposition cos(π/6)|0⟩ - i·sin(π/6)|1⟩
   - After Rx(-π/3): This is the inverse of the first rotation. Rx(-π/3) · Rx(π/3) = I (identity), so the state returns to |0⟩.

4. Expected probabilities: Since the final state is |0⟩, measuring gives |0⟩ with probability 1.0.

Let me verify the Rx gate matrix:
Rx(θ) = cos(θ/2)I - i·sin(θ/2)X = [[cos(θ/2), -i·sin(θ/2)], [-i·sin(θ/2), cos(θ/2)]]

For θ = π/3:
Rx(π/3)|0⟩ = cos(π/6)|0⟩ - i·sin(π/6)|1⟩

For θ = -π/3:
Rx(-π/3) = cos(-π/6)I - i·sin(-π/6)X = cos(π/6)I + i·sin(π/6)X

Applying Rx(-π/3) to the previous state:
Rx(-π/3)(cos(π/6)|0⟩ - i·sin(π/6)|1⟩)
= cos(π/6)·Rx(-π/3)|0⟩ - i·sin(π/6)·Rx(-π/3)|1⟩

Rx(-π/3)|0⟩ = cos(π/6)|0⟩ + i·sin(π/6)|1⟩

Rx(-π/3)|1⟩ = -i·sin(π/6)|0⟩ + cos(π/6)|1⟩

So:
= cos(π/6)·(cos(π/6)|0⟩ + i·sin(π/6)|1⟩) - i·sin(π/6)·(-i·sin(π/6)|0⟩ + cos(π/6)|1⟩)
= cos²(π/6)|0⟩ + i·cos(π/6)sin(π/6)|1⟩ - sin²(π/6)|0⟩ - i·sin(π/6)cos(π/6)|1⟩
= (cos²(π/6) - sin²(π/6))|0⟩
= cos(π/3)|0⟩ + 0|1⟩

Hmm, that doesn't give exactly |0⟩... Let me recalculate.

Wait, I think I need to reconsider. The product of the two Rx gates should be:
Rx(-π/3) · Rx(π/3) = Rx(-π/3 + π/3) = Rx(0) = I

Because Rx(α) · Rx(β) = Rx(α + β) since rotations around the same axis compose additively.

So yes, the final state should be |0⟩ exactly.

Let me redo the calculation more carefully:
cos²(π/6) - sin²(π/6) = cos(2·π/6) = cos(π/3) = 1/2

Hmm, that's not 1. Let me recalculate...

cos(π/6) = √3/2
sin(π/6) = 1/2

cos²(π/6) - sin²(π/6) = 3/4 - 1/4 = 1/2

This is cos(π/3) = 1/2, which is correct since cos(2x) = cos²(x) - sin²(x).

But wait, this doesn't give |0⟩...

Let me re-examine. The Rx rotations do compose additively:
Rx(α)Rx(β) = Rx(α+β)

So Rx(-π/3)Rx(π/3) = Rx(0) = I

Let me verify this by direct matrix multiplication:

Rx(θ) = [[cos(θ/2), -i·sin(θ/2)], [-i·sin(θ/2), cos(θ/2)]]

For θ = π/3:
cos(π/6) = √3/2, sin(π/6) = 1/2
Rx

## isqTrain/1705

- task_id: `isqTrain/1705`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4595`

### Prompt

Code this in isQ: Verify the gate identity 8T = I by applying the gate sequence to a qubit and measuring.

### Chain-of-thought reasoning

## Reasoning
* **Goal**: Verify the gate identity $T^8 = I$ by applying 8 T gates to a single qubit and measuring it.
* **Qubits**: 1 qubit is required and measured.
* **State Evolution**: The qubit starts in the initial state $|0\rangle$. The T gate adds a phase of $e^{i\pi/4}$ to the $|1\rangle$ state but leaves the $|0\rangle$ state unchanged. Applying the T gate eight times transforms the state as $T^8|0\rangle = |0\rangle$.
* **Probabilities**: Because the final quantum state is exactly $|0\rangle$, measurement yields the outcome $|0\rangle$ with a 100% probability ($P(|0\rangle) = 1.0$).

## isqTrain/3331

- task_id: `isqTrain/3331`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `600`

### Prompt

Code this in isQ: an isQ program: apply gate chain T-H-T to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply the gate chain T-H-T to a single qubit initialized to |0> and measure it.
One qubit is required, which is measured at the end.
Initial state is |0>.
First T gate acts on |0>, resulting in state |0> (since T|0> = |0>).
H gate transforms |0> into |+> = (1/√2)(|0> + |1>).
Second T gate transforms |+> into (1/√2)(|0> + e^(iπ/4)|1>).
The probabilities of measuring |0> and |1> are |1/√2|² = 0.5 and |e^(iπ/4)/√2|² = 0.5, respectively.

## isqTrain/3276

- task_id: `isqTrain/3276`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3196`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Ry(1*pi/3) then Ry(-1*pi/3) to cancel. Measure: should get |0>.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a reasoning section for a specific isQ quantum program (Ry cancellation).
    *   Input: The prompt, circuit implementation, expected probabilities, syntax reference.
    *   Output: ONLY the "## Reasoning" section (3-8 lines).
    *   Content constraints: Goal, qubits/measured, state evolution, expected probabilities explanation, Dirac notation, NO isQ code, precise, concise.

2.  **Analyze the Circuit:**
    *   Start: |0>
    *   Gate 1: Ry(π/3). This rotates around the Y-axis by 60 degrees.
    *   Gate 2: Ry(-π/3). This rotates around the Y-axis by -60 degrees.
    *   Effect: Ry(-π/3) * Ry(π/3) = I (Identity).
    *   End state: |0>
    *   Measurement: P(|0>) = 1.0.

3.  **Drafting the Reasoning (Iterative refinement):**
    *   *Draft 1:*
        ## Reasoning
        The goal is to demonstrate that two opposite Y-rotations cancel each other out.
        We need 1 qubit, and it will be measured at the end.
        1. Initial state is |0>.
        2. Apply Ry(π/3) to |0>, which rotates the state to cos(π/6)|0> + sin(π/6)|1>.
        3. Apply Ry(-π/3), which acts as the inverse of the first gate, returning the state exactly back to |0>.
        Because the final state is exactly |0>, measuring this qubit will yield 0 with 100% probability, so the probabilities are {|0>: 1.0}.
    *   *Checking constraints:*
        *   Goal in one line? Yes.
        *   Qubits/measured mentioned? Yes.
        *   State evolution? Yes (|0> -> cos(π/6)|0> + sin(π/6)|1> -> |0>). Let's make it simpler. Ry(-θ) Ry(θ) |0> = I |0> = |0>.
        *   Expected probabilities explained? Yes.
        *   3-8 lines? Yes, it's about 5-6 lines.
        *   Dirac notation? Yes.
        *   No code? Yes.

    *   *Refining for better precision and flow:*
        ## Reasoning
        The goal is to show that applying a Y-rotation and its exact inverse results in no net change to the quantum state.
        We require one qubit, `q[0]`, which is measured at the end.
        1. The circuit starts in the initial state |0>.
        2. The gate Ry(π/3) rotates the state, but the subsequent gate Ry(-π/3) is its exact inverse (since Ry(-θ)Ry(θ) = I).
        3. The state evolution is simply |0> → Ry(π/3)|0> → Ry(-π/3)Ry(π/3)|0> = |0>.
        Since the net effect is the identity, the final state is exactly |0>, meaning measurement yields |0> with a probability of 1.0.

    *   *Line count check:*
        Line 1: The goal is to show that applying a Y-rotation and its exact inverse results in no net change to the quantum state.
        Line 2: We require 1 qubit, which is measured.
        Line 3: 1. Initial state is |0>.
        Line 4: 2. Applying Ry(π/3) rotates the state, but applying Ry(-π/3) immediately cancels it.
        Line 5: 3. The net operation is the identity, so the state evolution is |0> -> |0>.
        Line 6: Because the final state is exactly |0>, the expected measurement probabilities are {|0>: 1.0}.
        Total 6 lines. Perfect.

4.  **Final Polish:**
    Ensure strict adherence to formatting. No code blocks for isQ. Use `## Reasoning`.
    Text to output:
    ## Reasoning
    The goal is to demonstrate that applying a Y-rotation followed by its inverse results in no net change.
    We need 1 qubit, which is measured at the end.
    1. The qubit begins in the initial state |0>.
    2. Applying Ry(π/3) rotates the state around the Y-axis.
    3. Applying Ry(-π/3) exactly cancels the previous rotation, as Ry(-θ)Ry(θ) = I.

## isqTrain/3341

- task_id: `isqTrain/3341`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4533`

### Prompt

Implement a quantum circuit in isQ: an isQ program: apply gate chain Y-X-Z to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
* Goal: Apply a Y-X-Z gate sequence to a single qubit initialized to |0> and measure the result.
* Qubits: 1 qubit is required and measured.
* State evolution:
  1. Initial state is |0>.
  2. Y gate maps |0> to i|1>.
  3. X gate maps i|1> to i|0>.
  4. Z gate leaves |0> unchanged (up to a global phase), keeping the state i|0>.
* Expected probabilities: The final state is exactly |0> (ignoring the unobservable global phase), yielding a 100% probability of measuring |0>.

## isqTrain/3127

- task_id: `isqTrain/3127`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4799`

### Prompt

Write an isQ program that an isQ program: apply ctrl Z (=CZ) on initial state |10> and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply a controlled-Z (CZ) gate to the state |10> and measure both qubits.
2. **Qubits:** 2 qubits (`q[0]`, `q[1]`), both measured.
3. **State Evolution:**
   - Initialize to |00⟩.
   - Apply X to `q[0]`: state becomes |10⟩.
   - Apply CZ(`q[0]`, `q[1]`): since the control `q[0]` is in |1⟩, the Z gate is applied to `q[1]`. Since Z|0⟩ = |0⟩, the state acquires a global phase and becomes -|10⟩.
4. **Probabilities:** The final state is -|10⟩, which is physically equivalent to |10⟩. Measurement yields the bitstring '10' with 100% probability.

## isqTrain/3357

- task_id: `isqTrain/3357`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `5663`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: prepare |01>, apply H1-CNOT, measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the Bell-like state by initializing |01⟩, applying H₁ then CNOT, and measuring both qubits.
2. **Qubits**: 2 qubits (`q[0]`, `q[1]`), both measured.
3. **State evolution**:
   - Start: |00⟩
   - After `X(q[1])`: |01⟩
   - After `H(q[1])`: H|1⟩ = |−⟩ → |0⟩|−⟩ = (|00⟩ − |01⟩)/√2
   - After `CNOT(q[0], q[1])`: Control (q[0]) is |0⟩, so target is unchanged: (|00⟩ − |01⟩)/√2
4. **Probabilities**: Both |00⟩ and |01⟩ have amplitude 1/√2, giving P(|00⟩) = 0.5 and P(|01⟩) = 0.5.

## isqTrain/5

- task_id: `isqTrain/5`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2913`

### Prompt

Code this in isQ: implements the gate_decomposition pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Demonstrate gate decomposition (swap (three-CNOT decomposition) via CNOTs) and identity gate cancellation (H-H pair).

**Qubits:** 2 global qubits `q[2]`, both measured.

**State evolution:**
1. Initial: |00⟩
2. `X(q[1])` → |01⟩
3. `swap_gate` (CNOT₀₁, CNOT₁₀, CNOT₀₁): CNOT₀₁ on |01⟩ → |01⟩; CNOT₁₀ → |11⟩; CNOT₀₁ → |10⟩. State: |10⟩
4. `H(q[0])` → (1/√2)(|00⟩ + |10⟩)
5. `H(q[0])` → H² = I, reverts to |10⟩

**Result:** Final state |10⟩ yields P(|10⟩) = 1.0, since the H-H pair cancels and swap (three-CNOT decomposition) correctly transfers the |1⟩ from q[1] to q[0].

## isqTrain/3340

- task_id: `isqTrain/3340`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5149`

### Prompt

用isQ实现an isQ program: apply gate chain T-H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
* Goal: Apply a T gate followed by an H gate to an initial |0> state and measure the outcome.
* Qubits: 1 qubit is allocated and measured.
* Evolution: The initial state |0> is unchanged by the T gate (since T|0> = |0>). The subsequent H gate puts it into an equal superposition |+> = (|0> + |1>)/sqrt(2).
* Probabilities: Measuring the |+> state yields |0> and |1> with identical probabilities of 0.5.

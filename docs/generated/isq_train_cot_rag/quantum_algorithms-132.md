# ISQ training COT RAG corpus: quantum_algorithms shard 132

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2713

- task_id: `isqTrain/2713`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `604`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
oracle bool[1] g(bool a[6]) {
    bool s[] = [true, true, true, false, true, true];
    bool ba[] = s & a;
    bool res[1];
    res[0] = ba[0] != ba[1] != ba[2] != ba[3] != ba[4] != ba[5];
    return res;
}
qbit q[6], res[1];

procedure main(){
    X(res);
    H(res);
    H(q);
    g(q, res);
    H(q); 
    print M(q); 
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Trace an isQ quantum program, explain the step-by-step reasoning, and determine the measurement probabilities.
    *   **Program Type:** Deutsch-Jozsa / Bernstein-Vazirani style oracle problem.
    *   **Output Format:** Start with "## Circuit Analysis", 3-15 lines, NO isQ code blocks, end with the predicted probability distribution.

2.  **Analyze the isQ Code:**
    *   **Qubits:** `qbit q[6], res[1];` (7 qubits total, $q_0..q_5$ and $res$).
    *   **Oracle `g(bool a[6])`:**
        *   `s[] = [true, true, true, false, true, true]` -> `s = 111011` in binary.
        *   `ba[] = s & a`
        *   `res[0] = ba[0] != ba[1] != ba[2] != ba[3] != ba[4] != ba[5]` -> This computes the bitwise AND of `s` and `a`, then takes the parity (XOR sum) of the result. This is exactly the dot product $s \cdot a \pmod 2$. The oracle implements $|a\rangle |b\rangle \to |a\rangle |b \oplus (s \cdot a)\rangle$.
        *   Wait, let's verify the parity expression: `!=` behaves as XOR for booleans. So it's $ba_0 \oplus ba_1 \oplus ba_2 \oplus ba_3 \oplus ba_4 \oplus ba_5$.
        *   Since $ba_i = s_i \wedge a_i$, the sum is $\bigoplus (s_i a_i) = s \cdot a$.
    *   **Main Procedure:**
        *   `X(res)` -> Initialize `res` to $|1\rangle$.
        *   `H(res)` -> Put `res` into $|-\rangle$.
        *   `H(q)` -> Apply H to all 6 qubits of `q`. State of `q` is now a uniform superposition of all $2^6$ states.
        *   `g(q, res)` -> Apply the oracle. For phase kickback, $|a\rangle |-\rangle \to (-1)^{s \cdot a} |a\rangle |-\rangle$. The phase is $-1$ if $s \cdot a = 1$.
        *   `H(q)` -> Apply H to all 6 qubits of `q` again.
        *   `print M(q)` -> Measure all 6 qubits of `q`.

3.  **Trace the Quantum State:**
    *   Initial state: $|000000\rangle_q |0\rangle_{res}$
    *   After `X(res)`: $|000000\rangle_q |1\rangle_{res}$
    *   After `H(res)`: $|000000\rangle_q |-\rangle_{res}$
    *   After `H(q)`: $\frac{1}{\sqrt{2^6}} \sum_{a=0}^{63} |a\rangle_q |-\rangle_{res}$
    *   After `g(q, res)`: $\frac{1}{\sqrt{2^6}} \sum_{a=0}^{63} (-1)^{s \cdot a} |a\rangle_q |-\rangle_{res}$, where $s = 111011_2$. (Note: The index order in isQ array assignment usually means `s[0]` is the lowest bit or highest bit depending on convention. Let's look at standard bit order. If `s = [true, true, true, false, true, true]`, and standard bitstring formatting puts index 0 as the lowest bit (rightmost). Let's trace carefully: "111011" corresponds to $s_0=1, s_1=1, s_2=0, s_3=1, s_4=1, s_5=1$? No, `s = [true, true, true, false, true, true]` means `s[0]=1, s[1]=1, s[2]=1, s[3]=0, s[4]=1, s[5]=1`. Let's map this to bits. Bitstring `q5 q4 q3 q2 q1 q0` is usually written with `q5` as the highest bit. If `s = [1, 1, 1, 0, 1,

### Reference answer

{'predicted_probs': {'110111': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1391

- task_id: `isqTrain/1391`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5703`

### Prompt

Implement the following in isQ: the Bernstein-Vazirani algorithm to find the secret string s = 100 (MSB first). Use 3 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Bernstein-Vazirani to find secret string s=100 using phase kickback and Hadamard transforms.

Qubits: 3 input (q[0-2]) measured, 1 ancilla (anc[0]) unmeasured.

State evolution:
1. |000>|0> → X(anc[0]) → |000>|1> → H(anc[0]) → |000>|->
2. H(q[0,1,2]) → |+++>|- > = (1/2√2)Σ_x|x>|-> (uniform superposition over all |x>)
3. Oracle CNOT(q[0],anc[0]): phase kickback applies (-1)^(s·x) = (-1)^(x₀) since s=100 → (1/2√2)Σ_x (-1)^(x₀)|x>|->
4. H(q[0,1,2]): H^⊗3 transforms phase encoding to computational basis: H^⊗3 Σ_x(-1)^(s·x)|x> = 2|s> = 2|100>

Final state: |100>|->, so measuring input qubits yields |100> with probability 1.0.

## isqExpand/algo/45

- task_id: `isqExpand/algo/45`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `grover`, `3qubit`, `multi_solution`, `optimal_iterations`
- source: `isq_expansion`
- dataset_index: `2408`

### Prompt

Write isQ code for the following quantum task: implements Grover's algorithm on 3 qubits to search for two marked states: |011> and |101>. Apply one Grover iteration. With M=2 solutions out of N=8, one iteration achieves perfect success (probability 1.0 on the marked states).

### Chain-of-thought reasoning

## Reasoning
Goal: 3-qubit Grover with 2 solutions: |011> (index 3) and |101> (index 5).

Oracle marks both states:
- Mark |011> (q[0]=0, q[1]=1, q[2]=1): X(q[0]); ctrl @[q[0], q[1]] Z(q[2]); X(q[0]);
- Mark |101> (q[0]=1, q[1]=0, q[2]=1): X(q[1]); ctrl @[q[0], q[1]] Z(q[2]); X(q[1]);

For N=8, M=2 solutions:
theta = arcsin(sqrt(2/8)) = arcsin(1/2) = pi/6
After 1 iteration: P_total = sin^2(3*pi/6) = sin^2(pi/2) = 1.0

Each marked state gets P = 0.5, all unmarked get P = 0.

## isqTrain/3033

- task_id: `isqTrain/3033`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2792`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[2];
procedure main() {
    nctrl X(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a circuit analysis for a simple isQ program. The analysis needs to include the operations, step-by-step state evolution using Dirac notation, the final state, and the predicted probability distribution.
2.  **Analyze the isQ program:**
    *   `qbit q[2];`: Initialize two qubits, `q[0]` and `q[1]`, in state $|0\rangle$. So initial state is $|00\rangle$.
    *   `nctrl X(q[0], q[1]);`: Wait, `nctrl` means *negative control*. In isQ, `ctrl` applies when control is $|1\rangle$. `nctrl` applies when control is $|0\rangle$.
        *   The syntax is `nctrl X(control, target)` or `nctrl X(target, control)`? Looking at standard isQ docs, typically `ctrl CNOT(c, t)` or similar. Here it's `nctrl X(q[0], q[1])`. Wait, `X` is a single qubit gate. In isQ, passing two qubits to a single-qubit gate with a control modifier usually implies `q[0]` is the control and `q[1]` is the target.
        *   Let's check the exact isQ syntax reference provided: "Control modifier: `ctrl @[c1, c2] Gate(target);`". But the prompt uses `nctrl X(q[0], q[1])`. Wait, `nctrl X(a, b)` might be an alternative syntax for negatively controlled X, where `a` is control and `b` is target. If `nctrl` means "apply if control is 0", and initial state is $|00\rangle$.
        *   Since it's $|00\rangle$, the control q[0] is in state $|0\rangle$, so the negative control condition is met. X is applied to target q[1].
        *   So $|00\rangle \to |01\rangle$.
        *   If it was `ctrl X(q[0], q[1])`, since q[0] is $|0\rangle$, it wouldn't apply, state would be $|00\rangle$.
        *   Since it's `nctrl X`, and state is $|00\rangle$, it applies X to q[1].
        *   Let's double check if `nctrl X(q[0], q[1])` means X is controlled by q[0] negatively. Yes, "nctrl" = negative control. Target = q[1].
    *   Initial state: $|q[1] q[0]\rangle = |00\rangle$.
    *   `nctrl X(q[0], q[1])`: If q[0] == $|0\rangle$, apply X to q[1].
    *   New state: $|01\rangle$ (considering q[1] is the target, its state flips from 0 to 1).
3.  **Determine Output Probabilities:**
    *   Final state is $|01\rangle$.
    *   Measured qubits: `q[0]`, then `q[1]`.
    *   In the `--probs` array, "earlier measured qubit = higher bit". So `q[0]` is the high bit, `q[1]` is the low bit.
    *   If state is $|q[1]=1, q[0]=0\rangle$, the bitstring is `01`.
    *   Probability of '01' is 1.0.
4.  **Format the Output:**
    *   Follow the requested format: "## Circuit Analysis", operations list, state evolution, final state, and probabilities.
    *   Ensure Dirac notation is used correctly.
    *   Keep it concise.

Let's re-verify `nctrl X(q[0], q[1])`.
The syntax `nctrl X(q[0], q[1])` is not explicitly in the syntax reference, but `nctrl` generally means apply if $|0\rangle$. The reference shows `ctrl @[c] Gate(target)`. The syntax `ctrl X(q[0], q[1])` is a shorthand where the first argument is the control, second is the target.
`nctrl X(q[0], q[1])` -> negative control on q[0], target q[1].
Initial state: $|0\rangle_{q[0]} \otimes |0\rangle_{q[1]} = |00\rangle$.
Negative control checks if q[0] is $|0\rangle$. It is.
Applies X to

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqExpand/algo/14

- task_id: `isqExpand/algo/14`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `simon`, `hidden_period`, `oracle`
- source: `isq_expansion`
- dataset_index: `4608`

### Prompt

Implement the following in isQ: implements Simon's algorithm for a 2-bit function with hidden period s=11. The oracle maps |x>|y> to |x>|y XOR f(x)> where f(00)=f(11)=00 and f(01)=f(10)=01.

### Chain-of-thought reasoning

## Reasoning
Goal: Simon's algorithm for s=11, f(00)=f(11)=00, f(01)=f(10)=01.

q[0],q[1] = input register, q[2],q[3] = output register.

1. H on input: uniform superposition (|00>+|01>+|10>+|11>)/2
2. Oracle: implements f(x) XOR'd into output
   - f(00)=00, f(01)=01, f(10)=01, f(11)=00
   - CNOT(q[0],q[2]): copies q[0] to q[2]
   - CNOT(q[1],q[3]): copies q[1] to q[3]
   - CNOT(q[0],q[3]): XOR q[0] into q[3]
   This gives f(x0,x1) = (x0, x1 XOR x0)
3. H on input register: produces y such that y·s = 0 mod 2
   s=11, so y·s = y0+y1 mod 2 = 0
   Solutions: y=00 and y=11, each with probability 0.5

Expected: {|00>: 0.5, |11>: 0.5}

## isqTrain/2800

- task_id: `isqTrain/2800`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3931`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```isq
import std;

bool m1, m2;
qbit q_1, q_2, q_3;

procedure Teleport(qbit qsrc, qbit qanc, qbit qdest) 
{
    H(qanc);
    CNOT(qanc, qdest);
    CNOT(qsrc, qanc);
    H(qsrc);
    X(qsrc); // BUG: spurious X before measurement

    m1 = M(qsrc);
    m2 = M(qanc);
    if (m2) { X(qdest); }
    if (m1) { Z(qdest); }
}

procedure main()
{
    X(q_1);
    Teleport(q_1, q_2, q_3);
    print M(q_3);
}
```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The `X(qsrc)` gate on line 16 of the Teleport procedure is spurious. It flips the source qubit just before measurement, corrupting the classical outcome `m1` and causing incorrect Pauli corrections on `qdest`.

2. **Fix**: Remove the `X(qsrc)` line entirely. The standard teleportation circuit measures `qsrc` and `qanc` directly after the entangling CNOT and H operations.

3. **Corrected state evolution**:
   - `main`: X(q_1) prepares |ψ⟩ = |1⟩ on q_1.
   - `H(q_2)`: q_2 → |+⟩.
   - `CNOT(q_2, q_3)`: creates Bell pair between q_2, q_3: (|00⟩+|11⟩)/√2.
   - `CNOT(q_1, q_2)`: entangles source with ancilla.
   - `H(q_1)`: rotates source into measurement basis.
   - Measuring q_1→m1, q_2→m2 yields random outcomes; conditional `X(q_3)` (if m2) and `Z(q_3)` (if m1) recover |ψ⟩ on q_3.
   - Final `M(q_3)` returns 1 with certainty, confirming successful teleportation.

## isqTrain/3007

- task_id: `isqTrain/3007`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3280`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    H(q[0]);
    H(q[1]);
    H(q[1]);
    H(q[2]);
    H(q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The initial state of the 3-qubit system is |000>.
2. The circuit applies the Hadamard gate (H) exactly twice to each qubit: q[0], q[1], and q[2].
3. Since the Hadamard gate is its own inverse ($H \cdot H = I$, the identity operation), applying it twice sequentially leaves the quantum state unchanged.
4. The system remains in the initial computational basis state |000> just before measurement.
5. Therefore, the measurement deterministically collapses the state to |000> with absolute certainty.

Predicted probability distribution: {'000': 1.0}

### Reference answer

{'predicted_probs': {'000': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/823

- task_id: `isqTrain/823`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4281`

### Prompt

Code this in isQ: implements the half_full_adder pattern but with a different initial state preparation (flip q[[1]] -> q[2]).

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program that implements a "half_full_adder pattern but with a different initial state preparation (flip q[[1]] -> q[2])".

Let me analyze The implementation:
1. q[0]: Input a, put in superposition with H gate
2. q[1]: Input b, stays |0⟩
3. q[2]: Sum output (also has X gate applied initially, setting it to |1⟩)
4. q[3]: Carry output

Wait, Analyzing the circuit requirements more carefully:
- H(q[0]) puts q[0] in |+⟩ state
- X(q[2]) sets q[2] to |1⟩ initially (this is the "flip q[2]" part)

But the description says "flip q[[1]] -> q[2]", which suggests we should flip q[1] instead of q[2].

Let me re-read: "implements the half_full_adder pattern but with a different initial state preparation (flip q[[1]] -> q[2])"

So the original pattern might have X(q[1]) to set b=1, and now we're changing it to X(q[2]) instead.

Actually, Analyzing the code, X(q[2]) is already there. So the "different initial state preparation" is that we flip q[2] instead of q[1].

Let me trace through the circuit:

Initial state: |0000⟩

After H(q[0]):
|0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
State: (|0000⟩ + |1000⟩)/√2

After X(q[2]):
q[2] flips |0⟩ → |1⟩
State: (|0010⟩ + |1010⟩)/√2 = (|0⟩ + |1⟩)/√2 ⊗ |0⟩ ⊗ |1⟩ ⊗ |0⟩

Now the half adder operations:

CNOT(q[0], q[2]): XOR of q[0] into q[2]
- If q[0] = |0⟩, q[2] stays |1⟩ → |1⟩
- If q[0] = |1⟩, q[2] flips |1⟩ → |0⟩

State after first CNOT:
- When q[0] = |0⟩: |0010⟩
- When q[0] = |1⟩: |1010⟩ → CNOT flips q[2]: |1000⟩

State: (|0010⟩ + |1000⟩)/√2

Wait, let me be more careful. q[2] was |1⟩. CNOT(q[0], q[2]) means:
- If q[0] = |0⟩: q[2] unchanged = |1⟩
- If q[0] = |1⟩: q[2] flipped = |0⟩

So:
- |0⟩₀|0⟩₁|1⟩₂|0⟩₃ → |0⟩₀|0⟩₁|1⟩₂|0⟩₃ (unchanged)
- |1⟩₀|0⟩₁|1⟩₂|0⟩₃ → |1⟩₀|0⟩₁|0⟩₂|0⟩₃ (q[2] flipped)

State: (|0010⟩ + |1000⟩)/√2

CNOT(q[1], q[2]): XOR of q[1] into q[2]
q[1] is always |0⟩, so q[2] is never flipped.
State unchanged: (|0010⟩ + |1000⟩)/√2

Toffoli(q[0], q[1], q[3]): AND of q[0] and q[1] into q[3]
q[1] is always |0⟩, so Toffoli never activates.
State unchanged: (|0010⟩ + |1000⟩)/√2

Now we measure q[2] and q[3]:
- |0010⟩: q[2] = 1, q[3] = 0 → "10" (q[2] is higher bit since measured first)
- |1000⟩: q[2] = 0, q[3] = 0 → "00"

Wait, let me check the measurement order. M(q[2]) is called first, M(q[3]) second.

In the --probs output, "earlier measured qubit = higher bit".
So q[2] is the higher bit and q[3] is the lower bit.

For |0010⟩: q[2] = 1, q[3] = 0 → bitstring "10" = 2
For |100

## isqExpand/algo/19

- task_id: `isqExpand/algo/19`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `deutsch_jozsa`, `oracle`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `1616`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    H(q[1]);
    X(q[2]);
    H(q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    H(q[0]);
    H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. H(q[0]), H(q[1]): input qubits in superposition
2. X(q[2]), H(q[2]): ancilla in |-> = (|0>-|1>)/sqrt(2)
3. CNOT(q[0],q[2]) + CNOT(q[1],q[2]): oracle for f(x)=x0 XOR x1
   With ancilla in |->: applies (-1)^f(x) phase to each |x>
4. H(q[0]), H(q[1]): transform back

For balanced f(x)=x0 XOR x1:
- After oracle: (|00>-|01>-|10>+|11>)/2 ⊗ |->
- After H⊗H: |11> ⊗ |->

Measuring q[0],q[1] only (2 qubits).
Expected: {|11>: 1.0}

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'This is the Deutsch-Jozsa algorithm for f(x0,x1) = x0 XOR x1 (balanced). q[2] is the ancilla in |-> state. The oracle CNOT(q[0],q[2])+CNOT(q[1],q[2]) implements f(x)=x0 XOR x1. After H on input register, the balanced function produces |11> with certainty... Wait, let me recalculate. Actually f(x)=x0 XOR x1 which is balanced, so the output should be non-zero. H^2 on the state after oracle gives |11>. Expected: {|11>: 1.0}'}

## isqTrain/1399

- task_id: `isqTrain/1399`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2898`

### Prompt

Implement a quantum circuit in isQ: the Bernstein-Vazirani algorithm to find the secret string s = 1001 (MSB first). Use 4 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Find secret string s=1001 using Bernstein-Vazirani algorithm with a single oracle query.

**Qubits**: 4 input qubits q[0..3] (measured), 1 ancilla anc[0] (unmeasured, provides phase kickback).

**State evolution**:
1. Initialize ancilla to |-> via X then H: |0000>|1> → |0000>|->
2. Apply H⊗⁴ to input register: |0000> → |++++> = (1/4)Σx|x>
3. Oracle (CNOT from q[0], q[3] to anc[0]) applies phase (-1)^(s·x) via kickback: (1/4)Σx(-1)^(s·x)|x>|-> where s=1001
4. Apply H⊗⁴ again: transforms phase-encoded string to computational basis state |s> = |1001>|->

**Result**: Measurement of input register yields |1001> with probability 1.0, as H⊗⁴ converts the oracle's phase encoding back to the basis state |s>.

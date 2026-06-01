# ISQ training COT RAG corpus: quantum_algorithms shard 145

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1271

- task_id: `isqTrain/1271`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5171`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the simon_algorithm pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants me to analyze an isQ program implementing a variant of Simon's algorithm. Let me trace through the circuit step by step.

Looking at the code:
- We have q[4] (4 qubits for input register) and out[3] (3 qubits for output register)
- The oracle f takes bool x[3] and returns [x[0], x[1], false]
- Wait, but the oracle declaration says `oracle bool[3] f(bool x[3])` but then uses `f(q, out)` which seems inconsistent

Actually, let me re-read the isQ syntax. In Simon's algorithm:
- The input register gets put into superposition
- The oracle computes f(x) into the output register
- Then we apply Hadamard again to the input register

Let me trace the state evolution:

1. Initial state: |0⟩^⊗7 (4 qubits in q, 3 qubits in out)

2. After H on q[0], q[1], q[2]: (assuming q[3] is not Hadamarded based on the code)
   The input register (q[0], q[1], q[2]) is in superposition |+⟩|+⟩|+⟩ = 1/√8 ∑|x⟩ for x in {0,...,7}
   But wait, q[3] is not Hadamarded, so it stays |0⟩

3. After the oracle f(q, out): 
   The oracle should compute f(x) into the output register
   For the given oracle: f([x0, x1, x2]) = [x0, x1, false]
   So it copies x[0] to out[0], x[1] to out[1], and sets out[2] to |0⟩

4. After H on q[0], q[1], q[2] again:
   This should extract the period information

Let me think about what state we end up with.

Actually, looking at the predicted output: {|0000⟩: 0.25, |0100⟩: 0.25, |1000⟩: 0.25, |1100⟩: 0.25}

So we're measuring 4 qubits (q[0], q[1], q[2], q[3]), and the outcomes are:
- |0000⟩: 25%
- |0100⟩: 25%  
- |1000⟩: 25%
- |1100⟩: 25%

This means q[3] is always 0, and q[0], q[1], q[2] are measured with equal probability for certain states.

Wait, the predicted output show that only states with q[2]=0 appear. Let me trace more carefully.

The oracle f ignores x[2] (the period is s=100), so f(x) = f(x XOR 100).

Let me trace step by step:

1. Initial: |0000000⟩ (q[0..3] and out[0..2])

2. H(q[0]), H(q[1]), H(q[2]):
   1/√8 (|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩) ⊗ |0⟩ ⊗ |000⟩
   = 1/√8 ∑_{x=0}^{7} |x⟩|0⟩|000⟩

3. Oracle f(q, out):
   Since f copies x[0] to out[0], x[1] to out[1], and false to out[2]:
   The state becomes:
   1/√8 ∑_x |x⟩|q3⟩|f(x)⟩
   
   But this is getting complicated because the oracle might entangle the registers.

Actually, let me think about this differently. In Simon's algorithm, after the oracle, the input register and output register are entangled. But then we measure the output register or ignore it, and the Hadamard on the input register extracts the period.

The predicted output that after everything, we get equal probability for |0000⟩, |0100⟩, |1000⟩, |1100⟩ when measuring q[0..3].

Hmm, let me reconsider. The code applies H to q[0], q[1], q[2] but not q[3]. Then after the oracle and second set of Hadamards, we measure all 4 qubits.

Let me trace more carefully. The period s = 100, so f(x) = f(x XOR 100).

After the first Hadamards on q[0..2], the state is:
1/√8 ∑_{x} |x

## isqTrain/3947

- task_id: `isqTrain/3947`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `768`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// Grover search on 3 qubits targeting |101>, 2 iterations
qbit q[3];

// Oracle: mark target state |101>
unit grover_oracle(qbit q[3]) {
    X(q[1]);
    ctrl CZ(q[0], q[1], q[2]);
    Y(q[1]);
} deriving gate

// Diffusion operator
unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

// Main: 2 Grover iterations for higher success probability
procedure main() {
    // Initialize superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Iteration 1
    grover_oracle(q);
    grover_diffusion(q);
    // Iteration 2
    grover_oracle(q);
    grover_diffusion(q);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

**The Bug:** In `grover_oracle`, the final gate `Y(q[1])` is incorrect — it should be `X(q[1])`.

**Why it's wrong:** The oracle targets |101⟩ by flipping q[1] with X (converting |101⟩ → |111⟩), applying the controlled-Z to phase-mark |111⟩, then flipping q[1] back. The uncomputation must use the same gate (X) because X·X = I restores the state. Using Y instead gives X·Y = iZ ≠ I, leaving an incorrect rotation and phase on q[1] that corrupts the oracle.

**The Fix:** Replace `Y(q[1])` with `X(q[1])` in the oracle.

**Corrected state evolution:**
1. **Init:** |000⟩ → H⊗3 → (1/2√2)Σ|x⟩ (equal superposition over 8 states)
2. **Oracle (corrected):** X(q[1]) maps |101⟩↔|111⟩; ctrl CZ flips phase of |111⟩; X(q[1]) restores — net effect: phase flip on |101⟩ only
3. **Diffusion:** Inverts amplitudes about the mean, amplifying |101⟩
4. **Iteration 2:** Repeats oracle + diffusion, further amplifying |101⟩
5. **Result:** |101⟩ has amplitude ≈ 0.972 (probability ≈ 0.945), all others ≈ 0.088 (probability ≈ 0.0078 each), matching predicted output.

## isqTrain/3073

- task_id: `isqTrain/3073`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `2261`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```isq
import std;
qbit q[4];
// Initialize to |0011>
procedure main() {
    X(q[2]);
    X(q[3]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The last measurement `M(q[0])` measures qubit `q[0]` a second time instead of measuring `q[3]`. The initialization prepares `|0011⟩` using X on `q[2]` and `q[3]`, so all four qubits should be measured once each.

2. **Fix**: Change the last line from `M(q[0])` to `M(q[3])` so that qubits q[0], q[1], q[2], and q[3] are each measured exactly once.

3. **State evolution**: Initial state `|0000⟩` → X(q[2]) gives `|0100⟩` → X(q[3]) gives `|0011⟩`. Measuring all four qubits yields the bitstring `0011` with probability 1.0, matching the predicted output.

## isqTrain/2726

- task_id: `isqTrain/2726`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1303`

### Prompt

What does this isQ program output when measured?

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

1.  **Understand the Goal:** The user wants a step-by-step analysis of an isQ quantum program, specifically identifying the final state and probability distribution before measurement. The output must be a "## Circuit Analysis" section following specific length and format constraints.

2.  **Analyze the isQ Code:**
    *   `qbit q[6], res[1];` -> 7 qubits. `q` is a 6-qubit register, `res` is a 1-qubit register.
    *   `X(res)` -> Flips `res` from $|0\rangle$ to $|1\rangle$.
    *   `H(res)` -> Puts `res` into $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. (Since it was $|1\rangle$, $H|1\rangle = |-\rangle$).
    *   `H(q)` -> Applies H to all 6 qubits of `q`. State is now $|+\rangle^{\otimes 6} \otimes |-\rangle$.
    *   `g(q, res)` -> Applies the oracle.
        *   Oracle logic: `s = [true, true, true, false, true, true]` (which is `111011` in binary).
        *   `ba = s & a` -> Bitwise AND.
        *   `res = ba[0] ^ ba[1] ...` -> XOR sum of `s & a`.
        *   This computes $s \cdot a \pmod 2$ (inner product of $s$ and $a$).
        *   The phase kickback will flip the phase of `q` if $s \cdot a = 1$.
        *   Since `res` is in $|-\rangle$, applying a CNOT (controlled by $f(a)=1$) to $|-\rangle$ gives $-|-\rangle$. So the overall state gets a phase of $(-1)^{s \cdot a}$.
        *   Effectively, this is a phase oracle: $|a\rangle \to (-1)^{s \cdot a}|a\rangle$.
        *   The state of `q` becomes $\frac{1}{\sqrt{2^6}} \sum_{a \in \{0,1\}^6} (-1)^{s \cdot a} |a\rangle$.
    *   `H(q)` -> Applies H to all 6 qubits of `q`.
        *   The state of `q` transforms from $\frac{1}{\sqrt{2^6}} \sum_{x} (-1)^{s \cdot x} |x\rangle$ to $|s\rangle$.
        *   Why? $H^{\otimes n} \left( \frac{1}{\sqrt{2^n}} \sum_{x} (-1)^{s \cdot x} |x\rangle \right) = |s\rangle$.
        *   Here $s = 111011_2$. Wait, `s` array is `[true, true, true, false, true, true]`.
        *   Let's check indices. `s[0]=1, s[1]=1, s[2]=1, s[3]=0, s[4]=1, s[5]=1`.
        *   In bitstrings, typically index 0 is the least significant bit or most significant bit.
        *   Let's trace carefully: The oracle evaluates $f(a) = s \cdot a$. If it equals 1, it applies X to `res`. Since `res` is in $|-\rangle$, it flips the sign.
        *   $H^{\otimes n}$ transforms $\sum (-1)^{s \cdot x} |x\rangle$ into $2^{n/2} |s\rangle$.
        *   Therefore, the final state of `q` before measurement is exactly $|s\rangle = |111011\rangle$.
    *   Wait, is `s` 111011 or 110111?
    *   Let's check `s` again: `bool s[] = [true, true, true, false, true, true]`
        *   `s[0] = true` -> 1
        *   `s[1] = true` -> 1
        *   `s[2] = true` -> 1
        *   `s[3] = false` -> 0
        *   `s[4] = true` -> 1
        *   `s[5] = true` -> 1
    *   If index 0 is the

### Reference answer

{'predicted_probs': {'110111': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3561

- task_id: `isqTrain/3561`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_ctrl_nctrl`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `4714`

### Prompt

Fix the bug in the following isQ program.

Bug description: Missing X gate for state preparation

The program should 3-qubit W state preparation.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a "Bug Analysis" section for a specific isQ program bug fix.
    *   Bug: Missing X gate for state preparation.
    *   Target: 3-qubit W state preparation (though the expected probs given are 1/6, 1/6, 2/3 which doesn't match a symmetric W state, wait... ah, the prompt says Expected measurement probabilities: {|001>: 0.166667, |010>: 0.166667, |100>: 0.666667}. Wait, (|100> + |010> + |001>)/sqrt(3) should give 1/3, 1/3, 1/3. Why 2/3, 1/6, 1/6? Let's trace the buggy and fixed circuit.)
    *   Actually, The resulting probabilities should be |100>: 2/3, |010>: 1/6, |001>: 1/6. Let's check the fixed circuit.
    *   Initial: |000>
    *   After `X(q[0])`: |100>
    *   `Ry(1.2309594173407747, q[0])`: cos(theta/2) = sqrt(1/3). Ry matrix is [[cos(t/2), -sin(t/2)], [sin(t/2), cos(t/2)]]. Wait, no, isQ Ry is typically [[cos(t/2), -sin(t/2)], [sin(t/2), cos(t/2)]]? No, standard is [[cos(t/2), -sin(t/2)], [sin(t/2), cos(t/2)]].
    *   Let's trace: `Ry(1.2309)` on |1> -> cos(t/2)|1> + sin(t/2)|0> ? No, if it's |1>, Ry(t)|1> = -sin(t/2)|0> + cos(t/2)|1>.
    *   If theta/2 = arccos(sqrt(1/3)), then cos(t/2) = sqrt(1/3), sin(t/2) = sqrt(2/3).
    *   So Ry(t)|1> = -sqrt(2/3)|0> + sqrt(1/3)|1>.
    *   Next: `nctrl X(q[0], q[1])`. This means if q[0] is |0>, apply X to q[1].
    *   State before nctrl: -sqrt(2/3)|00> + sqrt(1/3)|10> (ignoring q[2] for a sec, it's |0>). Wait, q[0] is the first qubit.
    *   nctrl X(q[0], q[1]): flips q[1] when q[0]=|0>.
    *   State after nctrl: -sqrt(2/3)|010> + sqrt(1/3)|100>. Wait, q[0] is highest bit? No, q[0] is bit 2, q[1] is bit 1, q[2] is bit 0. So |100> means q[0]=1.
    *   So state is sqrt(1/3)|100> - sqrt(2/3)|010>.
    *   Next: `ctrl Ry(1.5707963267949, q[1], q[2])`. This is C(Ry(pi/2), q[1], q[2]). Applied to q[2] when q[1]=|1>.
    *   The state has -sqrt(2/3)|010>. q[1]=1. Ry(pi/2)|0> = 1/sqrt(2)|0> + 1/sqrt(2)|1>.
    *   So -sqrt(2/3)|010> becomes -sqrt(2/3) * (1/sqrt(2)|010> + 1/sqrt(2)|011>).
    *   State is now: sqrt(1/3)|100> - sqrt(1/3)|010> - sqrt(1/3)|011>. Wait, this creates a 1 on q[2] when q[1]=1, giving |011> (q[2]=1).
    *   Wait, look at the next gate: `ctrl X(q[2], q[1])`. This flips q[1] when q[2]=1.
    *   In the state -sqrt(1/3)|011>, q[2]=1, so q[1] (which is 1) flips to 0. |011>

## isqTrain/4085

- task_id: `isqTrain/4085`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3807`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[3];

unit grover_oracle(qbit q[3]) {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[2]);
    X(q[1]);
    X(q[0]);
} deriving gate

unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    grover_oracle(q);
    grover_diffusion(q);
    grover_oracle(q);
    grover_diffusion(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations applied**: This is Grover's algorithm on 3 qubits with 2 iterations. The oracle marks state |000⟩ using X gates surrounding a triple-controlled-Z (which effectively applies a phase flip to |000⟩). The diffusion operator performs reflection about the mean.

2. **State evolution**:
   - After initial Hadamards: |ψ⟩ = (1/√8)Σ|x⟩ (uniform superposition over all 8 states)
   - After 1st oracle: |000⟩ gets phase flip → amplitude -1/√8, others +1/√8
   - After 1st diffusion: amplitude of |000⟩ → 5/(2√8), others → 1/(2√8)
   - After 2nd oracle: amplitude of |000⟩ → -5/(2√8), others → 1/(2√8)
   - After 2nd diffusion: amplitude of |000⟩ → 11/(4√8), others → -1/(4√8)

3. **Final state before measurement**: |ψ⟩ = (11/(4√8))|000⟩ + Σ_{x≠000}(-1/(4√8))|x⟩

4. **Predicted probability distribution**:
   - P(000) = |11/(4√8)|² = 121/128 ≈ 94.5%
   - P(each of 7 other states) = |1/(4√8)|² =

### Reference answer

Deterministic output: state |000> with probability ~0.95

## isqTrain/2030

- task_id: `isqTrain/2030`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `4726`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
oracle bool[1] f(bool x[2]) {
    bool res[] = [x[0] && x[1]];
    return res;
}
qbit q[2];
qbit ancilla[1];
procedure main() {
    X(q[0]); X(q[1]);
    f(q, ancilla);
    M(q[0]); M(q[1]); M(ancilla[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Operations: Initialize $|00\rangle_q|0\rangle_a$, apply X to q[0] and q[1], apply oracle $f$ to compute AND into ancilla, then measure all.
2. State evolution: System starts as $|00\rangle|0\rangle$. After X gates, it becomes $|11\rangle|0\rangle$.
3. Oracle $f$ computes $x_0 \land x_1 = 1 \land 1 = 1$. It flips the ancilla state, resulting

### Reference answer

{'predicted_probs': {'111': 1.0}, 'explanation': 'isQ oracle keyword AND(1,1)=1: final state |111>, P=1.0.'}

## isqTrain/2802

- task_id: `isqTrain/2802`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1441`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;

bool m1, m2;
qbit q_1, q_2, q_3;

procedure Teleport(qbit qsrc, qbit qanc, qbit qdest) 
{
    // H(qanc); // BUG: missing Hadamard
    CNOT(qanc, qdest);
    CNOT(qsrc, qanc);
    H(qsrc);
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

The bug is that the Hadamard gate `H(qanc)` is commented out in the Teleport procedure. This gate is essential for creating the Bell pair (entanglement) between `qanc` and `qdest`.

Let me trace through the corrected circuit to confirm:

1. Initial state: q_1 = |1⟩, q_2 = |0⟩, q_3 = |0⟩ → |100⟩

2. H(qanc) = H(q_2): |1⟩⊗(|0⟩+|1⟩)/√2⊗|0⟩ = |100⟩+|110⟩)/√2

3. CNOT(qanc, qdest) = CNOT(q_2, q_3): (|100⟩+|111⟩)/√2 — Bell pair created between q_2 and q_3

4. CNOT(qsrc, qanc) = CNOT(q_1, q_2): (|100⟩+|011⟩+|111⟩+|000⟩)/2... wait let me redo this.

State after step 3: (|1,0,0⟩ + |1,1,1⟩)/√2

CNOT(q_1, q_2): control=q_1, target=q_2
|1,0,0⟩ → |1,1,0⟩ (q_1=1, so flip q_2)
|1,1,1⟩ → |1,0,1⟩ (q_1=1, so flip q_2)

State: (|1,1,0⟩ + |1,0,1⟩)/√2

5. H(qsrc) = H(q_1):
H on q_1: |1⟩ → (|0⟩-|1⟩)/√2

|1,1,0⟩ → (|0,1,0⟩ - |1,1,0⟩)/√2
|1,0,1⟩ → (|0,0,1⟩ - |1,0,1⟩)/√2

State: (|010⟩ - |110⟩ + |001⟩ - |101⟩)/2

6. m1 = M(q_1), m2 = M(q_2)

The four outcomes each with probability 1/4:
- m1=0, m2=0: |010⟩ → q_3 = |0⟩, no corrections needed → q_3 stays |0⟩... wait, but we want to teleport |1⟩

Hmm, let me re-examine. The initial state is |1⟩ on q_1. After teleportation, q_3 should be |1⟩.

Let me re-examine more carefully with the corrections:

- m1=0, m2=0: collapsed to |010⟩, q_3=|0⟩. Corrections: no X, no Z. q_3=|0⟩. That's wrong...

Wait, I think I need to be more careful. Let me redo.

Actually, let me index qubits as q_1, q_2, q_3 throughout.

Initial: |1⟩|0⟩|0⟩ = |100⟩

Step 1: H(q_2)
|1⟩ ⊗ (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|100⟩+|110⟩)/√2

Step 2: CNOT(q_2, q_3) — control=q_2, target=q_3
(|100⟩+|111⟩)/√2

Step 3: CNOT(q_1, q_2) — control=q_1, target=q_2
|100⟩ → |110⟩ (q_1=1 flips q_2: 0→1)
|111⟩ → |101⟩ (q_1=1 flips q_2: 1→0)
State: (|110⟩+|101⟩)/√2

Step 4: H(q_1)
H|1⟩ = (|0⟩-|1⟩)/√2
|110⟩ → (|010⟩-|110⟩)/√2
|101⟩ → (|001⟩-|101⟩)/√2

State: (|010⟩-|110⟩+|001⟩-|101⟩)/2 = (|001⟩+|010⟩-|101⟩-|110⟩)/2

Now measuring q_1 (m1) and q_2 (m2):

- m1=0, m2=0: state is |001⟩, q_3=|1⟩. Corrections: no X (m2=0), no Z (m1=0). q_3=|1⟩ ✓
- m1=0, m2=1: state is |010⟩, q

## isqExpand/algo/158

- task_id: `isqExpand/algo/158`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `Shor算法`, `量子相位估计`, `量子傅里叶变换`, `阶发现`, `连分数展开`, `模幂运算`, `量子因数分解`
- source: `qa_pipeline`
- dataset_index: `267`

### Prompt

解释Shor算法分解N=21的过程：选择a=2，如何通过量子相位估计找到周期r？

### Chain-of-thought reasoning

首先确认Shor算法的核心框架：将因数分解转化为阶（order）发现问题，再用QPE高效求解。对于N=21, a=2，手动验证2^6≡1(mod 21)，确定r=6。然后逐步解释QPE的量子线路：Hadamard叠加→受控模幂运算→逆QFT→测量。重点说明本征值e^(2πis/r)如何被编码和提取。最后解释经典后处理步骤：连分数展开恢复r，以及用r计算出gcd(a^(r/2)±1,N)得到因子3和7。整个推理链确保物理直觉和数学细节的完整性。

### Reference answer

Shor算法分解N=21，选择a=2的完整过程如下：

**第一步：经典预处理**
选择a=2，验证gcd(2,21)=1，满足条件。

**第二步：构造求阶问题**
我们需要找到最小正整数r，使得2^r ≡ 1 (mod 21)。这就是函数f(x)=2^x mod 21的周期。

**第三步：量子相位估计(QPE)核心过程**

1. **寄存器初始化**：使用两个量子寄存器。第一寄存器（控制寄存器）有t个量子比特（t需足够大以保证精度，通常t=2⌈log₂N⌉），第二寄存器有⌈log₂(21)⌉=5个量子比特，存储模运算结果。

2. **叠加态制备**：对第一寄存器所有量子比特施加Hadamard门，得到均匀叠加态：
(1/√2^t) Σ|x⟩|0⟩，其中x从0到2^t-1。

3. **受控模幂运算**：对第二寄存器施加受控的U^(2^x)运算，其中U|y⟩=|2y mod 21⟩。这一步将叠加态变为：
(1/√2^t) Σ|x⟩|2^x mod 21⟩
由于f(x)具有周期性，第二寄存器的测量会使第一寄存器坍缩为周期性态。

4. **逆量子傅里叶变换(QFT†)**：对第一寄存器施加逆QFT。QPE的原理是：算子U的本征值为e^(2πis/r)（s=0,1,...,r-1），逆QFT将相位信息编码到计算基态的振幅中。

5. **测量**：测量第一寄存器，以高概率得到接近某个j/2^t ≈ s/r的整数值j。

**第四步：经典后处理——连分数展开**
测量得到j后，通过连分数展开(continued fraction expansion)从j/2^t逼近s/r，从而提取出r。

对于a=2, N=21：
2^1=2, 2^2=4, 2^3=8, 2^4=16, 2^5=32≡11(mod 21), 2^6=64≡1(mod 21)
因此真正的周期r=6。

QPE测量结果j/2^t会接近某个s/6（s=0,1,2,3,4,5），例如可能测量到接近1/6≈0.1667、2/6≈0.3333、5/6≈0.8333等的值。通过连分数算法可以从这些近似值恢复出分母6。

**第五步：利用周期分解**
- r=6是偶数，满足Shor算法条件
- 计算 a^(r/2) = 2^3 = 8
- gcd(8-1, 21) = gcd(7, 21) = 7
- gcd(8+1, 21) = gcd(9, 21) = 3
- 因此 21 = 3 × 7，分解成功！

**关键点总结**：量子优势在于QPE能高效地估计U的本征相位s/r，而经典方法需要O(√r)次求值。QPE通过受控模幂运算和逆QFT，用O(t²)个量子门就能实现指数级加速。

## isqTrain/3071

- task_id: `isqTrain/3071`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `926`

### Prompt

Write an isQ program that initializes 4 qubits to the state |0011> using X gates and measures all.

Requirements:
- Declare `qbit q[4];` at global scope.
- Apply X to qubits that should be |1>.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Initialize 4 qubits to state |0011> and measure all qubits.
2. 4 qubits (q[0..3]) are used and all are measured.
3. Initial state: |0000>. X(q[2]) flips qubit 2 to |1>: |0010>. X(q[3]) flips qubit 3 to |1>: |0011>.
4. Since the final state is exactly |0011>, measurement yields |0011> with probability 1.0.

# ISQ training COT RAG corpus: quantum_algorithms shard 84

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1341

- task_id: `isqTrain/1341`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `qft_based_arithmetic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1590`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[3];

procedure qft2(qbit q0, qbit q1) {
    H(q0);
    ctrl Rz(pi/2.0, q1, q0);
    H(q1);

    CNOT(q0, q1);
    CNOT(q1, q0);
    CNOT(q0, q1);
}

procedure main() {
    X(q[0]); X(q[1]);
    qft2(q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the main program:**
    *   `qbit q[3]` initializes 3 qubits: $|q_0 q_1 q_2\rangle = |000\rangle$.
    *   `X(q[0]); X(q[1]);` changes the state to $|110\rangle$. (Wait, bit order: $q[0]$ is the first argument, usually treated as the most significant or just separate index, but the initial state is $|1\rangle_0 \otimes |1\rangle_1 \otimes |0\rangle_2$). Let's trace it as $q_0 = 1$, $q_1 = 1$, $q_2 = 0$.
    *   `qft2(q[0], q[1]);` is called on $q_0$ and $q_1$.
    *   $q_2$ is untouched and remains $|0\rangle$.

2.  **Analyze `qft2(q0, q1)`:**
    *   Input state: $|11\rangle_{01}$.
    *   `H(q0)`: $q_0$ goes from $|1\rangle$ to $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        State: $\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$.
    *   `ctrl Rz(pi/2.0, q1, q0)`: (Note the isQ syntax for controlled gates, wait, `ctrl Rz(pi/2.0, q1, q0)` usually means $q_1$ is the control and $q_0$ is the target? Or `ctrl` modifier applies to the next arguments? In isQ, `ctrl Rz(angle, control, target)`? Let's check typical isQ syntax: `ctrl Rz(angle, ctrl, target)`? No, typically `ctrl Rz(angle, target)`? No, `ctrl` applies to the gate. Wait, standard `Rz(theta, q)` means it's a single qubit gate. Adding `ctrl` to `Rz` in isQ means the previous or next? "ctrl Rz(pi/2.0, q1, q0)". If it's like other languages, it might mean $q_1$ is control, $q_0$ is target. Let's re-read isQ syntax.
        Wait, `ctrl Rz(pi/2.0, q1, q0)` in isQ: `ctrl` makes it controlled. `Rz(angle, target)` usually. If `ctrl Rz(pi/2.0, q1, q0)`, then $q_1$ is control, $q_0$ is target.
        Wait, if it's $q_1$ control, $q_0$ target:
        On $|01\rangle$, $q_1$ is 0, so nothing.
        On $|11\rangle$, $q_1$ is 1, so apply $R_z(\pi/2)$ to $q_0$.
        $|1\rangle$ gets $e^{-i\pi/4}$? No, $R_z(\theta) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\theta} \end{pmatrix}$. Wait, usually $R_z$ is $\begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$.
        Let's just track the phase. It applies a phase to $|11\rangle$. Let's assume it's just some Z rotation on $q_0$.
        Actually, let's look at the next gates: `CNOT(q0, q1); CNOT(q1, q0); CNOT(q0, q1);` This is a swap operation (three-CNOT decomposition)!
        So `qft2` applies:
        H(q0)
        CRz(q1, q0) (with angle pi/2)
        H(q1)
        swap(q0, q1) via three CNOTs
        Let's trace carefully.
        H(q0) on |11> -> |01> - |11> (phase -1 for |11>, since H|1> = |->).
        CRz(q1, q0) applies $R_z(\pi/2)$ on $q_0$ when $q_1$ is 1.
        $|11\rangle$ gets $R_z(\pi/2)$ on $q_0$. $R_z(\pi/2)|1\rangle = e^{i\pi/

### Reference answer

{'predicted_probs': {'0': 0.25, '2': 0.25, '4': 0.25, '6': 0.25}, 'explanation': 'Parametric variant of isqEval/487. Dimension: qubit_variant: q[2] -> q[3].'}

## isqTrain/4535

- task_id: `isqTrain/4535`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1160`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];

procedure main() {
    
    X(q[1]); T(q[1]);  // replaced H with X
    
    
    H(q[0]);
    
    CNOT(q[0], q[1]);
    inv T(q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the probability distribution of an isQ quantum program.
    *   Input: isQ code with 2 qubits, `X`, `T`, `H`, `CNOT`, `inv T`, `CNOT`, `H`, `M`.
    *   Format: Output ONLY "## Circuit Analysis", concise step-by-step reasoning using Dirac notation (3-15 lines), ending with the predicted probability distribution.
    *   predicted output: {|01>: 0.8535533905932737, |11>: 0.1464466094067262} (or similar formatting, wait, the reference gives specific numbers. 0.8535 is $0.5 + 0.5/\sqrt{2} = (1+1/\sqrt{2})/2 \approx 0.8535$. $0.1464$ is $0.5 - 0.5/\sqrt{2} = (1-1/\sqrt{2})/2 \approx 0.1464$).

2.  **Trace the Quantum State:**
    *   Initial state: $|00\rangle$
    *   `X(q[1])`: $|01\rangle$
    *   `T(q[1])`: $T$ acts on $|1\rangle$, giving $e^{i\pi/4}|01\rangle$. (Wait, global phase doesn't affect probabilities. Let's keep track of it just in case, or drop it).
    *   `H(q[0])`: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle) \otimes |1\rangle = \frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$
    *   `CNOT(q[0], q[1])`: Control is $q[0]$, target is $q[1]$. $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)$ (Wait: $|01\rangle$ means $q[0]=0, q[1]=1$. $|11\rangle$ means $q[0]=1, q[1]=1$. CNOT flips $q[1]$ if $q[0]=1$. So $|01\rangle \to |01\rangle$, $|11\rangle \to |10\rangle$. State is $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)$.
    *   `inv T(q[1])`: $T^\dagger$ on $q[1]$. $T^\dagger = \text{diag}(1, e^{-i\pi/4})$.
        *   $|01\rangle \to e^{-i\pi/4}|01\rangle$
        *   $|10\rangle \to |10\rangle$
        *   State is $\frac{1}{\sqrt{2}}(e^{-i\pi/4}|01\rangle + |10\rangle)$.
    *   `CNOT(q[0], q[1])`: Control $q[0]$, target $q[1]$.
        *   $|01\rangle \to |01\rangle$
        *   $|10\rangle \to |11\rangle$
        *   State is $\frac{1}{\sqrt{2}}(e^{-i\pi/4}|01\rangle + |11\rangle)$.
    *   `H(q[0])`:
        *   $|0\rangle \to \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        *   $|1\rangle \to \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        *   State: $\frac{1}{2} ( e^{-i\pi/4}(|01\rangle + |11\rangle) + |01\rangle - |11\rangle )$
        *   $= \frac{1}{2} ( (1 + e^{-i\pi/4})|01\rangle + (e^{-i\pi/4} - 1)|11\rangle )$
    *   **Probabilities:**
        *   $P(|01\rangle) = | \frac{1}{2} (1 + e^{-i\pi/4}) |^2 = \frac{1}{4} ( (1 + \cos(\pi/4))^2 + \sin^2(\pi/4) ) = \frac{1}{4} (1 + 2\cos(\pi/4) + \cos^2

### Reference answer

{'predicted_probs': {'01': 0.853553, '11': 0.146447}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 0.8536, P(|11>) = 0.1464.'}

## isqTrain/1142

- task_id: `isqTrain/1142`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5302`

### Prompt

帮我写一个isQ程序：implements the graph_state_preparation pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a graph state preparation circuit with reversed measurement order.

Let me trace through this circuit:
1. Initialize 3 qubits: |000⟩
2. Apply H to all: |+⟩|+⟩|+⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)
3. Apply CZ(q[0], q[1]): This applies a phase flip when both q[0] and q[1] are |1⟩
4. Apply CZ(q[1], q[2]): This applies a phase flip when both q[1] and q[2] are |1⟩

This creates a linear graph state with edges (0,1) and (1,2).

5. Apply H to all qubits again (measuring in X basis)
6. Measure in reversed order: M(q[2]), M(q[1]), M(q[0])

The resulting probabilities should be: {|000⟩: 0.25, |010⟩: 0.25, |101⟩: 0.25, |111⟩: 0.25}

Let me think about this more carefully. After the graph state preparation and applying H to all qubits, we're essentially measuring in the X basis.

The linear 3-qubit graph state |G⟩ is a stabilizer state with stabilizers: X₀Z₁, Z₀X₁Z₂, Z₁X₂

After applying H⊗³, we transform to the computational basis measurement. The state after H⊗³ on the graph state gives specific correlations.

The measurement order matters for the bitstring indexing. Since we measure q[2] first, then q[1], then q[0]:
- q[2] is the highest bit (bit 2)
- q[1] is the middle bit (bit 1)  
- q[0] is the lowest bit (bit 0)

Wait, let me reconsider. In isQ, "earlier measured qubit = higher bit". So:
- M(q[2]) is measured first → highest bit (bit 2)
- M(q[1]) is measured second → middle bit (bit 1)
- M(q[0]) is measured third → lowest bit (bit 0)

So the bitstring is q[2]q[1]q[0].

Let me trace the state evolution more carefully:

After H⊗³: |+⟩|+⟩|+⟩

After CZ₀₁: The state is (1/2)(|0⟩(|0⟩+|1⟩)|+⟩ + |1⟩(|0⟩-|1⟩)|+⟩)

After CZ₁₂: The state becomes (1/2)(|0⟩(|0⟩|+⟩ + |1⟩|−⟩) + |1⟩(|0⟩|+⟩ - |1⟩|−⟩))

Let me be more careful. Starting from |+⟩|+⟩|+⟩ = (1/√8)∑_{x,y,z∈{0,1}} |xyz⟩

After CZ₀₁: applies -1 when x=y=1
State = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ - |110⟩ - |111⟩)

After CZ₁₂: applies -1 when y=z=1
State = (1/√8)(|000⟩ + |001⟩ + |010⟩ - |011⟩ + |100⟩ + |101⟩ - |110⟩ + |111⟩)

Now apply H⊗³:
H|0⟩ = |+⟩, H|1⟩ = |−⟩

Let me compute term by term:
H⊗³|xyz⟩ = (H|x⟩)(H|y⟩)(H|z⟩)

For each basis state, H transforms:
|0⟩ → |+⟩ = (1/√2)(|0⟩ + |1⟩)
|1⟩ → |−⟩ = (1/√2)(|0⟩ - |1⟩)

So H⊗³|xyz⟩ = (1/√8)∑_{a,b,c} (-1)^(x·a + y·b + z·c)|abc⟩

The final state is:
(1/8)∑_{a,b,c} [∑_{x,y,z} (-1)^{xa + yb + zc + xy + yz}] |abc⟩

Let me compute the amplitude for each |abc⟩:

For |000⟩: phase factor = (-1)^(0+0+0+xy+yz) summed over x,y,z
= (1 + (-1)^{xy}) + (1 + (-1)^{xy

## isqTrain/3026

- task_id: `isqTrain/3026`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4194`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit q[4];
// GHZ-like state with X on q[1]
procedure main() {
    // H(q[0]); // BUG: missing Hadamard
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    X(q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. The bug is a missing `H(q[0])` gate, which is incorrectly commented out. Without it, all qubits remain in the initial basis state |0000>, failing to create the required quantum superposition.
2. The fix is to uncomment or add `H(q[0])` at the beginning of the circuit to initialize the superposition before entanglement.
3. In the corrected circuit, `H(q[0])` creates the state (|0> + |1>)/sqrt(2) ⊗ |000>. Subsequent CNOT gates entangle the qubits into a 4-qubit GHZ state: (|0000> + |1111>)/sqrt(2). Finally, the `X(q[1])` gate flips the second qubit, resulting in the correct expected final state: (|0100> + |1011>)/sqrt(2).

## isqTrain/310

- task_id: `isqTrain/310`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2980`

### Prompt

Write an isQ program that implements a variant of the oracle_boolean pattern using y[1] -> y[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a Deutsch algorithm variant with constant oracle f(x)=1 using an expanded 2-qubit y register, measuring x[0].

**Qubits:** x[1], y[2]; only x[0] is measured.

**State evolution:**
1. Initial: |0⟩|00⟩
2. X(y[0]): |0⟩|10⟩
3. H(x[0])H(y[0]): ½(|0⟩+|1⟩)(|0⟩-|1⟩)|0⟩
4. X(y[0]) oracle (f≡1 flips y[0]): -½(|0⟩+|1⟩)(|0⟩-|1⟩)|0⟩
5. H(x[0]): -½·√2|0⟩(|0⟩-|1⟩)|0⟩ = -(1/√2)|0⟩(|0⟩-|1⟩)|0⟩

**Result:** x[0] is in state |0⟩ (up to global phase), so measuring yields |0⟩ with probability 1.0.

## isqTrain/2957

- task_id: `isqTrain/2957`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3149`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;
qbit q[2];
// 2-layer H+CNOT circuit on 2 qubits
procedure main() {
    H(q[0]);
    H(q[1]);
    CNOT(q[0], q[1]);
    // CNOT(q[1], q[0]); // BUG: missing CNOT
    H(q[0]);
    H(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

The buggy code has a missing CNOT gate. Let me analyze this carefully.

Buggy code:

Fixed code adds the missing `CNOT(q[1], q[0])` after the first `CNOT(q[0], q[1])`.

Let me trace through the corrected circuit:

Starting state: |00>

After H(q[0]) ⊗ H(q[1]): |++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

After CNOT(q[0], q[1]): (1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩) = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

Wait, CNOT(q[0], q[1]) with q[0] as control, q[1] as target:
|00⟩ → |00⟩, |01⟩ → |01⟩, |10⟩ → |11⟩, |11⟩ → |10⟩

So (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩) → (1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩) = same thing, still |++⟩

Hmm, that's interesting. Let me reconsider.

Actually |+⟩ = (|0⟩ + |1⟩)/√2

|++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

CNOT(0,1) on |++⟩: |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩
Result: (1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩) = |++⟩

So CNOT on |++⟩ gives |++⟩. Now CNOT(q[1], q[0]) on |++⟩:
|00⟩→|00⟩, |01⟩→|11⟩, |10⟩→|10⟩, |11⟩→|01⟩
Result: (1/2)(|00⟩ + |11⟩ + |10⟩ + |01⟩) = |++⟩

So after the first layer, we still have |++⟩. This makes sense since H⊗H transforms CNOT.

Actually, let me think about this differently. The key property is that (H⊗H) CNOT_{01} (H⊗H) = CNOT_{10}, and (H⊗H) CNOT_{10} (H⊗H) = CNOT_{01}.

So the corrected circuit is:
Layer 1: H⊗H, CNOT(0,1), CNOT(1,0)
Layer 2: H⊗H, CNOT(0,1), CNOT(1,0)

Let me trace more carefully:

Start: |00⟩

H⊗H: |++⟩

CNOT(0,1): |++⟩ (as computed above)

CNOT(1,0) on |++⟩: q[1] is control, q[0] is target
|00⟩→|00⟩, |01⟩→|11⟩, |10⟩→|10⟩, |11⟩→|01⟩
(1/2)(|00⟩ + |11⟩ + |10⟩ + |01⟩) = |++⟩

H⊗H: |00⟩

Wait, H⊗H applied to |++⟩ = |00⟩. Yes!

CNOT(0,1) on |00⟩ = |00⟩
CNOT(1,0) on |00⟩ = |00⟩

Final state: |00⟩, measurement gives |00⟩ with probability 1. ✓

Now without the fix (buggy):

Start: |00⟩
H⊗H: |++⟩
CNOT(0,1): |++⟩
(Missing CNOT(1,0))
H⊗H: |00⟩
CNOT(0,1): |00⟩
CNOT(1,0): |00⟩

Wait, that also gives |00⟩? Let me re-examine.

Hmm, if the bug is in the first layer missing CNOT(1,0), and H⊗H applied to |++⟩ = |00⟩, then...

Actually wait. The circuit structure is different from what I initially thought. Let me re-read:

Corrected circuit

## isqTrain/311

- task_id: `isqTrain/311`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3613`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the oracle_boolean pattern using x[1] -> x[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a Deutsch-like oracle with constant function f(x)=1 using expanded qubit registers, demonstrating that constant functions yield predictable measurement outcomes.
2. **Qubits**: 4 qubits total (x[0], x[1], x[2], y[0]); measure x[0], x[1], x[2].
3. **State evolution**:
   - Initialize |0000⟩
   - X(y[0]) → |0001⟩
   - H(x[0]), H(y[0]) → (|0⟩+|1⟩)/√2 ⊗ |00⟩ ⊗ (|0⟩-|1⟩)/√2 = |+⟩|00⟩|−⟩
   - X(y[0]) applies oracle for f(x)=1, flipping phase: → |+⟩|00⟩|+⟩
   - H(x[0]) → |0⟩|00⟩|+⟩
4. **Expected probabilities**: Measuring x[0,1,2] yields |000⟩ with probability 1.0, since x[0] returns to |0⟩ (constant function property) and x[1], x[2] were never manipulated, remaining in |0⟩.

## isqTrain/340

- task_id: `isqTrain/340`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `571`

### Prompt

Create an isQ quantum circuit that implements a variant of the qft_subcircuit pattern using u[1] -> u[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit implements a Quantum Phase Estimation (QPE) variant with:
- q[2]: precision qubits (2 qubits)
- u[2]: eigenstate register (2 qubits, but only u[0] is used)

Step-by-step state evolution:

1. Initial state: |00⟩⊗|00⟩

2. X(u[0]): |00⟩⊗|10⟩

3. H(q[0]) and H(q[1]): (1/2)(|00⟩+|01⟩+|10⟩+|11⟩)⊗|10⟩

4. ctrl S(q[1], u[0]): This applies S to u[0] when q[1]=1. S|1⟩ = i|1⟩
   So: (1/2)(|00⟩|10⟩ + |01⟩·i|10⟩ + |10⟩|10⟩ + |11⟩·i|10⟩)
   = (1/2)(|00⟩ + i|01⟩ + |10⟩ + i|11⟩)⊗|10⟩

5. ctrl Z(q[0], u[0]): This applies Z to u[0] when q[0]=1. Z|1⟩ = -|1⟩
   = (1/2)(|00⟩ + i|01⟩ - |10⟩ - i|11⟩)⊗|10⟩
   = (1/2)(|00⟩ - |10⟩ + i|01⟩ - i|11⟩)⊗|10⟩
   = (1/2)((|0⟩-|1⟩)⊗|0⟩ + i(|0⟩-|1⟩)⊗|1⟩)⊗|10⟩
   
   Wait, let me be more careful. The precision register is q[0] (MSB) and q[1] (LSB).
   
   Actually, looking at the phase being estimated:
   - S has eigenvalue e^(iπ/2) = i, so the phase is 1/4
   - Z has eigenvalue e^(iπ) = -1, so the phase is 1/2
   
   But wait, the controlled operations are:
   - ctrl S(q[1], u[0]): This is S^1 on u[0] controlled by q[1]
   - ctrl Z(q[0], u[0]): This is S^2 = Z on u[0] controlled by q[0]
   
   In standard QPE, if q[0] is the most significant bit, we'd apply U^(2^(n-1)) to q[0], U^(2^(n-2)) to q[1], etc.
   
   For 2 qubits: q[0] gets U^2, q[1] gets U^1
   
   So the convention here seems to be:
   - q[0] (MSB) gets U^2 = Z
   - q[1] (LSB) gets U^1 = S
   
   The phase θ = 1/4 (from eigenvalue e^(2πiθ) = i, so θ = 1/4)
   
   In binary, θ = 0.01 (since 1/4 = 0*1/2 + 1*1/4)
   
   So we should measure |01⟩ where q[0]=0, q[1]=1.

Let me trace more carefully:

After X(u[0]): |00⟩|10⟩

After H on both q qubits: (1/2)(|00⟩+|01⟩+|10⟩+|11⟩)|10⟩

After ctrl S(q[1], u[0]): S|1⟩ = i|1⟩, so phase i when q[1]=1
(1/2)(|00⟩ + i|01⟩ + |10⟩ + i|11⟩)|10⟩

After ctrl Z(q[0], u[0]): Z|1⟩ = -|1⟩, so phase -1 when q[0]=1
(1/2)(|00⟩ + i|01⟩ - |10⟩ - i|11⟩)|10⟩

The precision register state is:
|ψ⟩ = (1/2)(|00⟩ + i|01⟩ - |10⟩ - i|11⟩)

Let me factor this:
|ψ⟩ = (1/2)(|0⟩(|0⟩ + i|1⟩) - |1⟩(|0⟩ + i|1⟩))
    = (1/2)(|0⟩ - |1⟩)(|0⟩ + i|1⟩)
    = (1/2)|−⟩(|0⟩ + i|1⟩)

Hmm, let me check: |−

## isqTrain/2635

- task_id: `isqTrain/2635`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `global_phase`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `327`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[3];

procedure main() {
    // Encode a = 3 (binary 11): set both bits
    X(q[0]);
    X(q[1]);
    // Threshold comparator: a >= 2 when MSB is set
    CNOT(q[1], q[2]);
    // Measure the result flag
    M(q[2]);
}

```

vs.

```isq
import std;
qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Encode a = 3 (binary 11): set both bits
    X(q[0]);
    X(q[1]);
    // Threshold comparator: a >= 2 when MSB is set
    CNOT(q[1], q[2]);
    // Measure the result flag
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes 3 qubits to |000⟩, applies X to q[0] and q[1] to encode the state |110⟩, and then applies a CNOT with q[1] as control and q[2] as target. Since q[1] is |1⟩, q[2] flips to |0⟩, resulting in the final state |110⟩.
2. **Program B** performs the exact same sequence of operations but includes an additional `GPhase(0.0)` at the beginning.
3. The key difference is the presence of `GPhase(0.0)` in Program B, which applies a trivial global phase factor of $e^{i \cdot 0} = 1$.
4. The measurement probability distributions are identical because a global phase of 0 has no effect on the quantum state's amplitudes or measurement probabilities.
5. Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/2907

- task_id: `isqTrain/2907`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3971`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```isq
import std;
oracle bool[1] g(bool a[3]) {
    bool s[] = [true, false, true];
    bool ba[] = s & a;
    bool res[1];
    res[0] = ba[0] != ba[1] != ba[2];
    return res;
}
qbit q[3];
qbit anc[1];

procedure main() {
    // X(anc); // BUG: missing initialization
    H(anc);
    H(q);
    g(q, anc);
    H(q);
    for i in 0:3 {
        M(q[i]);
    }
}

```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The ancilla qubit initialization `X(anc)` is commented out on line 18. For Bernstein-Vazirani, the ancilla must start in |1⟩ so that `H(anc)` produces |−⟩ = (|0⟩ − |1⟩)/√2. Without this, the ancilla is in |+⟩, and the oracle's phase kickback fails—the controlled operations cannot imprint the secret string `s` as phases on the main qubits.

2. **Fix**: Uncomment `X(anc)` before `H(anc)` so the ancilla enters the oracle in |−⟩.

3. **Corrected state evolution**:
   - |000⟩|0⟩ → X(anc) → |000⟩|1⟩
   - H(anc) → |000⟩|−⟩; H(q) → |+++⟩|−⟩
   - Oracle g encodes s=[1,0,1]: phase kickback via |−⟩ flips phase when s·x = 1, yielding Σₓ (-1)^(s·x)|x⟩|−⟩
   - H(q) → |101⟩|−⟩
   - Measure q → |101⟩ with probability 1.0

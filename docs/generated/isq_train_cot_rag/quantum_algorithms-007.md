# ISQ training COT RAG corpus: quantum_algorithms shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1233

- task_id: `isqTrain/1233`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2683`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;

// Shor subroutine: modular exponentiation 2^x mod 3
// x register: 1 qubit, work register: 2 qubits
qbit x[1];
qbit w[2];

procedure main() {
    // Initialize work register to |01> = decimal 1
    X(w[0]);
    // Put exponent in superposition
    H(x[0]);
    // When x=1: multiply by 2 mod 3
    // 2*1 mod 3 = 2 (binary 10), so swap w[0] and w[1]
    // Controlled-SWAP on the work register
    ctrl SWAP(x[0], w[0], w[1]);
    // Measure exponent and work register
    M(x[0]); M(w[0]); M(w[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Input:** An isQ program implementing a small Shor's subroutine (modular exponentiation $2^x \bmod 3$).
    *   **Task:** Predict the probability distribution of measurement outcomes, explain the reasoning step-by-step using Dirac notation, and format as requested ("## Circuit Analysis", no code blocks, specific ending).
    *   **Constraint:** Concise (3-15 lines), precise, use Dirac notation.

2.  **Analyze the Circuit:**
    *   `qbit x[1]; qbit w[2];` -> Initial state is $|000\rangle$ where order is $x_0, w_0, w_1$. Let's write it as $|x\rangle |w_0\rangle |w_1\rangle = |0\rangle|0\rangle|0\rangle = |000\rangle$.
    *   `X(w[0]);` -> Flips $w_0$.
        *   State: $|0\rangle|1\rangle|0\rangle = |010\rangle$.
    *   `H(x[0]);` -> Puts $x_0$ in superposition.
        *   State: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |1\rangle|0\rangle = \frac{1}{\sqrt{2}}(|010\rangle + |110\rangle)$.
    *   `ctrl swap (three-CNOT decomposition)(x[0], w[0], w[1]);` -> Conditioned on $x_0$ being 1, it swaps $w_0$ and $w_1$.
        *   For $|0\rangle_{x_0} \otimes |1\rangle_{w_0} |0\rangle_{w_1} \rightarrow |0\rangle_{x_0} \otimes |1\rangle_{w_0} |0\rangle_{w_1}$ (no change) = $|010\rangle$.
        *   For $|1\rangle_{x_0} \otimes |1\rangle_{w_0} |0\rangle_{w_1} \rightarrow |1\rangle_{x_0} \otimes |0\rangle_{w_0} |1\rangle_{w_1}$ (swapped) = $|101\rangle$.
        *   Combined state: $\frac{1}{\sqrt{2}}(|010\rangle + |101\rangle)$.
    *   `M(x[0]); M(w[0]); M(w[1]);` -> Measures all 3 qubits.

3.  **Determine Probabilities:**
    *   State is $\frac{1}{\sqrt{2}}(|010\rangle + |101\rangle)$.
    *   Probability of $|010\rangle = |1/2|^2 = 0.5$.
    *   Probability of $|101\rangle = |1/2|^2 = 0.5$.

4.  **Format Output:**
    *   Start with "## Circuit Analysis".
    *   Concise steps as requested.
    *   End with predicted probability distribution.
    *   Ensure no code blocks are generated.

5.  **Drafting the text:**
    ## Circuit Analysis
    1. **Initialization:** The 3-qubit system starts as $|000\rangle$ ($x_0, w_0, w_1$).
    2. **Work Register Setup:** `X(w[0])` flips the second qubit, evolving the state to $|010\rangle$.
    3. **Superposition:** `H(x[0])` puts the first qubit into an equal superposition: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |10\rangle = \frac{1}{\sqrt{2}}(|010\rangle + |110\rangle)$.
    4. **Controlled swap (three-CNOT decomposition):** `ctrl swap (three-CNOT decomposition)(x[0], w[0], w[1])` swaps $w_0$ and $w_1$ when $x_0$ is $|1\rangle$. This transforms $|110\rangle$ to $|101\rangle$.
    5. **Final State:** The state before measurement is $\frac{1}{\sqrt{2}}(|010\rangle + |101\rangle)$.
    
    Predicted probability distribution: {|010>: 0.5, |101>: 0.5}

6.  **Refining:** Looks solid, meets constraints perfectly. 5 steps, very clear, right notation.

### Reference answer

{'predicted_probs': {'2': 0.5, '5': 0.4999999999999999}, 'explanation': 'Parametric variant of isqEval/451. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1146

- task_id: `isqTrain/1146`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `data_encoding_qml`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `151`

### Prompt

Code this in isQ: implements a variant of the data_encoding pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze The implementation and understand what's happening.

The circuit uses 3 qubits (q[0], q[1], q[2]) and performs a variant of ZZ feature map data encoding.

Let me trace through the circuit:

1. Initial state: |000⟩

2. H(q[0]); H(q[1]);
   |000⟩ → (1/√2)(|0⟩ + |1⟩) ⊗ (1/√2)(|0⟩ + |1⟩) ⊗ |0⟩
   = (1/2)(|000⟩ + |010⟩ + |100⟩ + |110⟩)

3. Rz(0.78539816339745, q[0]); // Rz(π/4) on q[0]
   Rz(θ) applies phase e^{-iθ/2} to |0⟩ and e^{iθ/2} to |1⟩
   So |0⟩ → e^{-iθ/2}|0⟩, |1⟩ → e^{iθ/2}|1⟩
   
   For θ = π/4:
   Terms with q[0]=|0⟩ get multiplied by e^{-iπ/8}
   Terms with q[0]=|1⟩ get multiplied by e^{iπ/8}
   
   State becomes: (1/2)(e^{-iπ/8}|000⟩ + e^{-iπ/8}|010⟩ + e^{iπ/8}|100⟩ + e^{iπ/8}|110⟩)

4. Rz(1.57079632679490, q[1]); // Rz(π/2) on q[1]
   For θ = π/2:
   Terms with q[1]=|0⟩ get multiplied by e^{-iπ/4}
   Terms with q[1]=|1⟩ get multiplied by e^{iπ/4}
   
   State becomes: (1/2)(e^{-iπ/8}e^{-iπ/4}|000⟩ + e^{-iπ/8}e^{iπ/4}|010⟩ + e^{iπ/8}e^{-iπ/4}|100⟩ + e^{iπ/8}e^{iπ/4}|110⟩)
   
   = (1/2)(e^{-i3π/8}|000⟩ + e^{iπ/8}|010⟩ + e^{-iπ/8}|100⟩ + e^{i3π/8}|110⟩)

5. H(q[0]); H(q[1]);
   Apply H to both qubits. H|0⟩ = |+⟩, H|1⟩ = |-⟩
   
   Let me compute each term:
   - e^{-i3π/8}|000⟩: H⊗H on first two → e^{-i3π/8}|+⟩|+⟩|0⟩ = e^{-i3π/8}(1/2)(|0⟩+|1⟩)(|0⟩+|1⟩)|0⟩
     = e^{-i3π/8}(1/2)(|000⟩+|010⟩+|100⟩+|110⟩)
   
   - e^{iπ/8}|010⟩: → e^{iπ/8}|+⟩|−⟩|0⟩ = e^{iπ/8}(1/2)(|0⟩+|1⟩)(|0⟩−|1⟩)|0⟩
     = e^{iπ/8}(1/2)(|000⟩−|010⟩+|100⟩−|110⟩)
   
   - e^{-iπ/8}|100⟩: → e^{-iπ/8}|−⟩|+⟩|0⟩ = e^{-iπ/8}(1/2)(|0⟩−|1⟩)(|0⟩+|1⟩)|0⟩
     = e^{-iπ/8}(1/2)(|000⟩+|010⟩−|100⟩−|110⟩)
   
   - e^{i3π/8}|110⟩: → e^{i3π/8}|−⟩|−⟩|0⟩ = e^{i3π/8}(1/2)(|0⟩−|1⟩)(|0⟩−|1⟩)|0⟩
     = e^{i3π/8}(1/2)(|000⟩−|010⟩−|100⟩+|110⟩)

   Combining:
   |000⟩ coefficient: (1/4)(e^{-i3π/8} + e^{iπ/8} + e^{-iπ/8} + e^{i3π/8})
   |010⟩ coefficient: (1/4)(e^{-i3π/8} - e^{i

## isqExpand/algo/46

- task_id: `isqExpand/algo/46`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `3qubit`, `oracle`, `bug_fix`
- source: `isq_expansion`
- dataset_index: `3760`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```isq
import std;
qbit q[3];

procedure oracle() {
    X(q[0]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[0]);
}

procedure diffusion() {
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
}

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    oracle();
    diffusion();
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

Target state: |100> (q[0]=1, q[1]=0, q[2]=0).

The buggy oracle applies X(q[0]) to flip q[0] before CCZ. This means CCZ fires when q[0]=0 (flipped to 1), q[1]=1, q[2]=1 — marking |011>, not |100>.

To mark |100>: we need CCZ to fire when q[0]=1, q[1]=0, q[2]=0.
- q[0] is already 1 in |100>, no flip needed.
- q[1] is 0, needs X: X(q[1]).
- q[2] is 0, needs X: X(q[2]).

Fix: Replace X(q[0]) with X(q[1]) and X(q[2]) before and after CCZ.

After fix, |100> (index 4) gets P = 0.78125, others get 0.03125.

## isqExpand/algo/48

- task_id: `isqExpand/algo/48`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `3qubit`, `diffusion_operator`, `bug_fix`
- source: `isq_expansion`
- dataset_index: `2441`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
qbit q[3];

procedure oracle() {
    ctrl ctrl Z(q[0], q[1], q[2]);
}

procedure diffusion() {
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
}

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    oracle();
    diffusion();
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

The 3-qubit diffusion operator requires the phase flip to act only on |000> (which becomes |111> after X gates), so a 3-qubit controlled-Z (CCZ) is needed.

The buggy code uses CZ(q[0], q[1]) which is only a 2-qubit controlled-Z. It flips the phase of any state where both q[0]=1 AND q[1]=1, regardless of q[2]. After X transforms, this means it flips |110> and |111> instead of just |111>.

Fix: Replace CZ(q[0], q[1]) with ctrl @[q[0], q[1]] Z(q[2]).

With the correct CCZ in diffusion and the oracle for |111>, P(|111>) = 25/32 = 0.78125 after 1 iteration.

## isqTrain/4503

- task_id: `isqTrain/4503`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2322`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;

qbit q[2];

procedure main() {
    
    H(q[0]); H(q[1]);
    
    
    CZ(q[0], q[1]);
    
    
    H(q[0]); H(q[1]);
    
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    
    H(q[0]); H(q[1]);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, step-by-step analysis of an isQ quantum program to predict the final probability distribution, based on the specific rules provided.

2.  **Analyze the isQ Code:**
    *   Initialization: 2 qubits, $|00\rangle$.
    *   Step 1: `H(q[0]); H(q[1]);` -> Applies Hadamard to both -> $|++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   Step 2: `CZ(q[0], q[1]);` -> Controlled-Z gate. $|11\rangle$ gets a -1 phase. State is $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle) = |--\rangle$.
    *   Step 3: `H(q[0]); H(q[1]);` -> Applies Hadamard to both. State goes from $|--\rangle$ to $|11\rangle$.
    *   Step 4: `X(q[0]); X(q[1]); CZ(q[0], q[1]); X(q[0]); X(q[1]);` -> Applies X to both, then CZ, then X to both. Let's simplify.
        *   $X_0 X_1 CZ_{01} X_0 X_1$
        *   Since $X \otimes X$ flips both bits, $X_0 X_1 |11\rangle = |00\rangle$.
        *   $CZ_{01} |00\rangle = |00\rangle$ (no change).
        *   $X_0 X_1 |00\rangle = |11\rangle$.
        *   Wait, let's double check. A CZ flanked by Xs on both qubits is effectively a CZ with negative controls, or applying it on the computational basis state $|11\rangle$ becomes $|11\rangle \xrightarrow{X \otimes X} |00\rangle \xrightarrow{CZ} |00\rangle \xrightarrow{X \otimes X} |11\rangle$. So it just leaves $|11\rangle$ unchanged. (Actually, $(-1)^{(1-x)(1-y)} = (-1)^{1 - x - y + xy}$ which adds a global phase, so $|11\rangle$ is unchanged up to a phase). Let's explicitly trace:
        *   $|11\rangle \xrightarrow{X \otimes X} |00\rangle$
        *   $|00\rangle \xrightarrow{CZ} |00\rangle$
        *   $|00\rangle \xrightarrow{X \otimes X} |11\rangle$.
        *   Yes, state is still $|11\rangle$.
    *   Step 5: `H(q[0]); H(q[1]);` -> Applies Hadamard to both. State goes to $|--\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
    *   Step 6: `X(q[0]);` -> Flips qubit 0. State goes from $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$ to $\frac{1}{2}(|10\rangle + |11\rangle + |00\rangle - |01\rangle) = \frac{1}{2}(|00\rangle - |01\rangle + |10\rangle + |11\rangle) = |-+\rangle$.
    *   Wait, let's re-evaluate Step 4:
        State before Step 4 is $|11\rangle$.
        `X(q[0]) X(q[1])` gives $|00\rangle$.
        `CZ(q[0], q[1])` leaves it as $|00\rangle$ (since $CZ|00\rangle = |00\rangle$).
        `X(q[0]) X(q[1])` brings it back to $|11\rangle$.
        So the state is exactly $|11\rangle$.
    *   Step 5: `H(q[0]); H(q[1]);`
        $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        So $|11\rangle \to |--\rangle = \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 1.0000.'}

## isqTrain/1206

- task_id: `isqTrain/1206`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `superposition`
- source: `isq_train_cot`
- dataset_index: `279`

### Prompt

Code this in isQ: implements a variant of the quantum_random_walk pattern using c[1] -> c[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Analyzing the circuit requirements, I need to understand what it does:

1. It has a coin qubit register `c[2]` (but only uses `c[0]`)
2. It has a position register `p[2]` (2 qubits for 4 positions)
3. The quantum walk on a 4-node cycle with one step

Let me trace through the circuit:

Initial state: |0⟩_c ⊗ |00⟩_p = |000⟩

1. H(c[0]): Creates |+⟩_c ⊗ |00⟩_p = (|0⟩ + |1⟩)/√2 ⊗ |00⟩

2. ctrl CNOT(c[0], p[0], p[1]): When c[0]=|1⟩, apply CNOT(p[0], p[1])
   - |0⟩⊗|00⟩ → |0⟩⊗|00⟩ (no change)
   - |1⟩⊗|00⟩ → |1⟩⊗|00⟩ (CNOT with p[0]=0 doesn't flip p[1])
   State: (|0⟩ + |1⟩)/√2 ⊗ |00⟩

3. ctrl X(c[0], p[0]): When c[0]=|1⟩, apply X to p[0]
   - |0⟩⊗|00⟩ → |0⟩⊗|00⟩
   - |1⟩⊗|00⟩ → |1⟩⊗|10⟩
   State: (|0⟩⊗|00⟩ + |1⟩⊗|10⟩)/√2

4. nctrl X(c[0], p[0]): When c[0]=|0⟩, apply X to p[0]
   - |0⟩⊗|00⟩ → |0⟩⊗|10⟩
   - |1⟩⊗|10⟩ → |1⟩⊗|10⟩
   State: (|0⟩⊗|10⟩ + |1⟩⊗|10⟩)/√2 = |+⟩⊗|10⟩

Wait, that doesn't seem right. Let me re-check the increment/decrement logic.

Actually, for a quantum walk, the increment and decrement operations should give different results. Let me trace more carefully.

For the increment (when coin=|1⟩):
- We want to add 1 mod 4 to the position
- Increment from |00⟩: |00⟩ → |01⟩
- But with carry: CNOT(p[0], p[1]) flips p[1] when p[0]=1, then X(p[0]) flips p[0]

Wait, I need to think about binary encoding:
- |00⟩ = 0
- |01⟩ = 1
- |10⟩ = 2
- |11⟩ = 3

Increment by 1:
- 0 → 1: |00⟩ → |01⟩ (flip p[0])
- 1 → 2: |01⟩ → |10⟩ (flip p[0] from 1 to 0, carry to p[1])
- 2 → 3: |10⟩ → |11⟩ (flip p[0])
- 3 → 0: |11⟩ → |00⟩ (flip p[0] from 1 to 0, carry to p[1])

So the increment is: CNOT(p[0], p[1]) first (to handle carry), then X(p[0]).

Actually, let me think again. If p[0] is the LSB:
- Increment = add 1 to the binary number
- For binary addition: flip LSB, and carry to next bit if LSB was 1

So the order should be:
1. First apply CNOT(p[0], p[1]) - this propagates the carry (if p[0]=1, flip p[1])
2. Then apply X(p[0]) - flip the LSB

This matches the reference code's ctrl section.

For decrement (when coin=|0⟩):
- Decrement by 1 is the same as add 3 mod 4
- Or we can think of it as: flip p[0] first, then handle the borrow

Decrement:
- 0 → 3: |00⟩ → |11⟩ (flip p[0] to 1, borrow: flip p[1] since p[0] was 0)
- 1 → 0: |01⟩ → |00⟩ (flip p[0] to 0)
- 2 → 1: |10⟩ → |01⟩ (flip p[0] to 1)
- 3 → 2: |11⟩ → |10⟩ (flip p[0] to 0, no borrow needed since p[0] was 1)

Hmm, this is getting complex

## isqTrain/3045

- task_id: `isqTrain/3045`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_inv`, `measurement_order`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2263`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    H(q[0]);
    CNOT(q[0], q[1]);
    inv CNOT(q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis

**Gate sequence:** X(q[0]), H(q[0]), CNOT(q[0], q[1]), inv CNOT(q[0], q[1]), H(q[0])

**State evolution:**
1. Initial state: |00⟩
2. X(q[0]): |10⟩
3. H(q[0]): (|0⟩ − |1⟩)/√2 ⊗ |0⟩ = (|00⟩ − |10⟩)/√2
4. CNOT(q[0], q[1]): (|00⟩ − |11⟩)/√2
5. inv CNOT(q[0], q[1]): (|00⟩ − |10⟩)/√2 = (|0⟩ − |1⟩)/√2 ⊗ |0⟩
6. H(q[0]): |1⟩ ⊗ |0⟩ = |10⟩

**Final state:** |10⟩

**Predicted probability distribution:** {'10': 1.0}

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2038

- task_id: `isqTrain/2038`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `hamiltonian_simulation`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2034`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];
procedure main() {
    X(q[1]);
    CNOT(q[0], q[1]);
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State:** The 2-qubit system starts in the ground state $|00\rangle$.
2. **X Gate:** An X gate is applied to $q[1]$, flipping its state from $|0\rangle$ to $|1\rangle$. The state becomes $|01\rangle$.
3. **First CNOT Gate:** A CNOT gate with control $q[0]$ and target $q[1]$ is applied. Since the control qubit $q[0]$ is in the state $|0\rangle$, the target qubit is unchanged. The state remains $|01\rangle$.
4. **Rz Gate:** An Rz gate with angle $\pi/2$ (1.570796...) is applied to $q[1]$. This adds a global phase to the state $|01\rangle$, but does not change the measurement probabilities.
5. **Second CNOT Gate:** Another CNOT gate with control $q[0]$ and target $q[1]$ is applied. Again, the control is $|0\rangle$, leaving the state unchanged as $|01\rangle$.
6. **Final State:** The system is in the state $|01\rangle$.

Predicted probabilities:
- '01': 1.0

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'ZZ evolution on eigenstate |01>: global phase only, P(|01>)=1.0.'}

## isqExpand/algo/215

- task_id: `isqExpand/algo/215`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `ghz_state`, `entanglement`, `hadamard_gate`, `cnot_gate`, `measurement_probabilities`
- source: `isq_expansion`
- dataset_index: `4137`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
}
```

### Chain-of-thought reasoning

Step 1: Initial state is |000⟩ (all qubits in |0⟩). Step 2: Apply H(q[0]). This puts qubit 0 into superposition (|0⟩+|1⟩)/√2, so the full state becomes (|000⟩+|100⟩)/√2. Step 3: Apply CNOT(q[0],q[1]). The control is qubit 0, target is qubit 1. When qubit 0 is |1⟩, qubit 1 flips. State becomes (|000⟩+|110⟩)/√2. Step 4: Apply CNOT(q[1],q[2]). The control is qubit 1, target is qubit 2. When qubit 1 is |1⟩, qubit 2 flips. State becomes (|000⟩+|111⟩)/√2. This is the 3-qubit GHZ state. Step 5: Measurement probabilities. The state is an equal superposition of |000⟩ and |111⟩ only. Each has amplitude 1/√2, so probability |1/√2|² = 0.5. Therefore P(000)=0.5, P(111)=0.5, all other outcomes have probability 0.

### Reference answer

{'predicted_probs': {'000': 0.5, '001': 0.0, '010': 0.0, '011': 0.0, '100': 0.0, '101': 0.0, '110': 0.0, '111': 0.5}, 'explanation': 'The GHZ circuit starts with all qubits in |000⟩. H(q[0]) creates (|000⟩+|100⟩)/√2. CNOT(q[0],q[1]) entangles qubits 0 and 1, yielding (|000⟩+|110⟩)/√2. CNOT(q[1],q[2]) spreads entanglement to qubit 2, producing the maximally entangled GHZ state (|000⟩+|111⟩)/√2. Measurement yields equal 50/50 probability for bitstrings 000 and 111.'}

## isqQA/quantum_algorithms/37_principle_advantage

- task_id: `isqQA/quantum_algorithms/37_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `principle_advantage`, `algorithm`, `Deutsch算法`
- source: `qa_pipeline`
- dataset_index: `2796`

### Prompt

请通俗易懂地解释一下Deutsch（德义奇）算法的基本原理。相比于经典算法，它的量子加速来源是什么？在评估黑盒函数时，经典计算和量子计算的时间复杂度有怎样的对比？

### Reference answer

Deutsch算法是量子计算中最基础的算法之一，它展示了量子计算如何打破经典计算的某些局限。

**1. 宏观原理**
Deutsch算法解决的核心问题是：给定一个未知的黑盒函数 $f: \{0, 1\} \rightarrow \{0, 1\}$，我们需要判断这个函数是“常数函数”（即 $f(0)=f(1)$）还是“平衡函数”（即 $f(0) \neq f(1)$）。在量子线路中，该算法利用了两个量子比特。首先，将第一个量子比特初始化为 $|0\rangle$，第二个初始化为 $|1\rangle$。接着，对这两个量子比特施加Hadamard（H）门，使它们进入状态的均匀叠加态。随后，我们将黑盒函数封装为一个量子酉算子（通常称为Oracle）作用于这个叠加态。由于量子态具有叠加特性，Oracle在一次运算中就同时处理了输入0和1的情况。最后，再次对第一个量子比特施加Hadamard门，利用量子干涉效应将相位差转化为可测量的概率幅差异。此时只需测量第一个量子比特：如果测量结果为0，说明是常数函数；如果结果为1，则是平衡函数。

**2. 时间复杂度对比**
在经典计算模型中，要想知道 $f(0)$ 和 $f(1)$ 的关系，我们别无他法，必须分别向黑盒输入0和1，即进行**2次查询**。而Deutsch算法利用量子计算机，**只需要进行1次查询**。这表明在解决此类黑盒全局属性查询问题时，量子计算的时间复杂度从经典情况下的 $O(2)$ 成功降低到了 $O(1)$。

**3. 量子加速来源**
Deutsch算法之所以能实现指数级的加速（从2次到1次），核心来源有两个：一是**量子并行性**，通过Hadamard门创造的叠加态，使得单次量子Oracle操作就能同时“计算”出 $f(0)$ 和 $f(1)$ 的隐藏信息；二是**量子干涉**，仅仅同时得出结果是不够的，因为直接测量会导致状态随机坍缩，无法直接比较。算法巧妙地利用了第二个量子比特引入的相对相位变化，结合最后一次Hadamard门的干涉作用，消除了具体的局部函数值，将我们关心的全局属性（函数是否平衡）完美地转化为了第一个量子比特的测量概率。这种从“提取局部数据”到“直接提取全局结构特征”的转变，正是量子加速的本质。

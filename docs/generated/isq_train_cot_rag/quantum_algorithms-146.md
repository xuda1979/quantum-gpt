# ISQ training COT RAG corpus: quantum_algorithms shard 146

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3576

- task_id: `isqTrain/3576`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `hamiltonian_simulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5397`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should QAOA MaxCut on 4-node path graph.

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug identification:**
In the Edge (0,1) block, the first CNOT has reversed arguments: `CNOT(q[1], q[0])` uses q[1] as control and q[0] as target, while the third line uses `CNOT(q[0], q[1])` with q[0] as control and q[1] as target. A proper ZZ interaction via CNOT-Rz-CNOT requires both CNOTs to have the **same** control and target. The two mismatched CNOTs do **not** implement $e^{-i\gamma Z_0 Z_1}$.

**2. Fix:**
Change the first line of Edge (0,1) from `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`, matching the third line. This yields the standard ZZ decomposition: CNOT(0,1) → Rz(γ, target) → CNOT(0,1), which applies $R_z(2\gamma)$ when both qubits differ (computing XOR into target via CNOT, phase-shifting, then uncomputing).

**3. Corrected state evolution:**
- After H gates: $|++++\rangle$ (uniform superposition).
- Each edge block applies $e^{-i\gamma Z_i Z_j}$: CNOT computes parity into target → $R_z$ phases $|11\rangle$ and $|10\rangle$ by $e^{\mp i\gamma}$ → CNOT uncomputes. This enforces the MaxCut cost Hamiltonian on edges (0,1), (1,2), (2,3).
- Mixer: $R_x(2\beta=0.6)$ on each qubit rotates toward cut solutions.
- Final probabilities match the expected distribution, peaked at $|0000\rangle$ and $|1111\rangle$ (~0.176 each), which are degenerate MaxCut cuts (though not maximal—those are antiferromagnetic like $|0101\rangle$ which has lower probability here due to the single-QAOA-layer approximation with these γ, β values).

## isqTrain/2565

- task_id: `isqTrain/2565`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `global_phase`, `interference`, `isq_syntax_arrays`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3939`

### Prompt

判断以下两段isQ代码是否产生相同的测量结果：

代码1：
```isq
import std;

qbit q[2];
qbit a[2];

procedure my_oracle() {
    CNOT(q[1], a[1]);
}

procedure main() {
    H(q[0]); H(q[1]);
    my_oracle();
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}

```

代码2：
```isq
import std;

qbit q[2];
qbit a[2];

procedure my_oracle() {
    CNOT(q[1], a[1]);
}

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]); H(q[1]);
    my_oracle();
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes two qubit arrays, applies H to `q[0]` and `q[1]` to put them in a superposition, applies a CNOT from `q[1]` to `a[1]`, and then applies H again to `q[0]` and `q[1]` before measuring them.
2. **Program B** performs the exact same operations but adds a `GPhase(0.0)` gate at the beginning of the main procedure.
3. **Key difference**: Program B introduces a global phase gate `GPhase(0.0)` before executing the same quantum circuit as Program A.
4. **Measurement probabilities**: The measurement probabilities are exactly the same. A global phase of 0.0 corresponds to a complex exponential of $e^{i \cdot 0} = 1$, which acts as an identity operation. Thus, it has no effect on the quantum state or the resulting measurement distribution.
5. **Verdict**: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/3915

- task_id: `isqTrain/3915`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `3490`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// Inverse QFT on 3 qubits with input |110>
qbit q[3];

procedure main() {
    // Prepare input
    X(q[0]);
    Y(q[1]);

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    // Measure after inverse QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze this bug carefully.

The task is to implement a 3-qubit inverse QFT with input |110>.

The buggy code has:

But the corrected version should be:

Let me think about this:

1. The input should be |110>, which means q[0]=0, q[1]=1, q[2]=1.

Wait, let me reconsider. In quantum computing, the state |110> means:
- q[0] (least significant bit) = 0
- q[1] = 1  
- q[2] (most significant bit) = 1

So to prepare |110>:
- q[0] should be |0> (no gate needed, it's already |0>)
- q[1] should be |1> (apply X)
- q[2] should be |1> (apply X)

But wait, looking at the code, it applies X(q[0]) and Y(q[1]). Let me reconsider the bit ordering.

Actually, in isQ and many quantum frameworks, the bit ordering might be different. Let me look at the predicted output: equal superposition over all 3-qubit states.

The inverse QFT of |110> should give us a computational basis state that encodes the frequency information. Actually, let me think again...

Wait, QFT transforms from computational basis to Fourier basis. So QFT|000> gives equal superposition. Inverse QFT of |110> would give some specific basis state.

Hmm, but the expected measurement probabilities show equal probability for all states. That seems wrong for inverse QFT of |110>.

Let me reconsider. Maybe the task description and the actual circuit don't match perfectly, or I'm misunderstanding something.

Actually, looking at the code more carefully:
- X(q[0]) prepares q[0] to |1>
- X(q[1]) or Y(q[1]) prepares q[1] to |1> or some other state

If we use X(q[0]) and X(q[1]), we get |011> (q[0]=1, q[1]=1, q[2]=0).

The inverse QFT circuit in the code looks like it's operating on the qubits in reverse order from what I'd expect.

Let me trace through the circuit with the bug fix (X(q[0]) and X(q[1])):

After preparation: |011>

The circuit then does swap (three-CNOT decomposition) operations (the three CNOTs), which swaps q[0] and q[2].
After swap (three-CNOT decomposition)(q[0], q[2]): |110>

Then the inverse QFT proceeds:
- H(q[2])
- ctrl Rz(-2π/4, q[2], q[1])
- H(q[1])
- ctrl Rz(-2π/8, q[2], q[0])
- ctrl Rz(-2π/4, q[1], q[0])
- H(q[0])

This looks like the standard inverse QFT circuit operating from the highest bit to lowest.

For inverse QFT on |110>:
- |110> = |6> in decimal

QFT formula: QFT|j> = (1/√N) Σ_k e^(2πijk/N) |k>

So QFT|j> = |j> transformed to Fourier basis.

Inverse QFT would be: QFT†|k> = |some basis state>

Actually, the equal superposition output suggests that the input state might be an eigenstate or something special.

Wait, looking at the predicted output again: equal probability for all 8 states. This would be the result of QFT|000> or inverse QFT of equal superposition.

Let me reconsider. If we apply QFT to |6> = |110>, we get:
QFT|6> = (1/√8) Σ_{k=0}^{7} e^(2πi·6·k/8) |k>

And inverse QFT|6> would give:
QFT†|6> = (1/√8) Σ_{k=0}^{7} e^(-2πi·6·k/8) |k>

Neither of these gives equal superposition unless there's something special.

Hmm, I think I might be overcomplicating this. The key bug is:
- Y(q[1]) should be X(q[1])

The Y gate is [[0,-i],[i,0]], which transforms |0> to i|1>, not just |1>. This introduces an incorrect phase.

The X gate is [[0,1],[1,0]], which transforms |0> to |1>.

So the bug is using Y instead of X for q[

## isqTrain/3571

- task_id: `isqTrain/3571`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `644`

### Prompt

Fix the bug in the following isQ program.

Bug description: Missing Hadamard gate

The program should 6-qubit GHZ state.

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug Identification:**
The comment `// Superposition on first qubit` indicates an H gate should be applied to `q[0]`, but the actual `H(q[0]);` line is missing. Without it, `q[0]` remains in |0⟩, so every CNOT control is |0⟩ and no target qubit flips — the state stays |000000⟩.

**2. Fix:**
Insert `H(q[0]);` immediately before the CNOT chain, turning the comment into a realized operation.

**3. Corrected State Evolution (6 qubits):**
- **Init:** |000000⟩
- **H(q[0]):** (|000000⟩ + |100000⟩)/√2
- **CNOT(q[0],q[1]):** (|000000⟩ + |110000⟩)/√2
- **CNOT(q[0],q[2]):** (|000000⟩ + |111000⟩)/√2
- **CNOT(q[0],q[3]):** (|000000⟩ + |111100⟩)/√2
- **CNOT(q[0],q[4]):** (|000000⟩ + |111110⟩)/√2
- **CNOT(q[0],q[5]):** (|000000⟩ + |111111⟩)/√2 = **6-qubit GHZ state** ✓

Expected measurement: {|000000⟩: 0.5, |111111⟩: 0.5} — confirmed.

## isqTrain/3521

- task_id: `isqTrain/3521`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `ancilla_usage`, `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `5084`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```
import std;

qbit q[2];
qbit anc[1];

procedure main() {
    X(anc[0]);
    H(anc[0]);

    H(q[0]); H(q[1]);

    CNOT(q[0], anc[0]);
    CNOT(q[1], anc[0]);

    H(q[0]); H(q[1]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ program with 3 qubits (q[0], q[1], anc[0]).
    *   Task: Predict the output probability distribution (list basis states with non-zero probability for measured qubits).
    *   Constraints: "Generate a circuit analysis section that explains...", "concise, precise step-by-step reasoning", "3-8 lines for simple circuits, up to 15 for complex ones", "Use Dirac notation".

2.  **Analyze the isQ Program:**
    
    *   Qubits: $q_0, q_1, a_0$. Initial state: $|000\rangle$ (in order $q_0, q_1, a_0$).
    *   `X(a_0); H(a_0);` -> $a_0$ is in $|1\rangle \xrightarrow{H} |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   `H(q_0); H(q_1);` -> $q_0, q_1$ are in $|+\rangle|+\rangle$.
    *   Current state: $\frac{1}{2} (|00\rangle + |01\rangle + |10\rangle + |11\rangle)_{q} \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_{a}$.
    *   `CNOT(q_0, a_0); CNOT(q_1, a_0);`:
        *   $|x\rangle |y\rangle |z\rangle \xrightarrow{CNOT_{x,a}} |x\rangle |y\rangle |z \oplus x\rangle \xrightarrow{CNOT_{y,a}} |x\rangle |y\rangle |z \oplus x \oplus y\rangle$.
        *   Since $z = 0$ initially (before $X$ it was 0, let's trace amplitude):
        *   Amplitude for $|x,y\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = \frac{1}{2\sqrt{2}} |x,y\rangle (|0\rangle - |1\rangle)$.
        *   After CNOTs: $\frac{1}{2\sqrt{2}} |x,y\rangle (|0 \oplus x \oplus y\rangle - |1 \oplus x \oplus y\rangle)$.
        *   Notice that $|0 \oplus c\rangle - |1 \oplus c\rangle$ is $(-1)^c (|0\rangle - |1\rangle)$.
        *   So state becomes $\frac{1}{2} \sum_{x,y} (-1)^{x \oplus y} |x,y\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   Specifically:
            *   $|00\rangle \to (-1)^0 |00\rangle |-\rangle = |00\rangle |-\rangle$
            *   $|01\rangle \to (-1)^1 |01\rangle |-\rangle = -|01\rangle |-\rangle$
            *   $|10\rangle \to (-1)^1 |10\rangle |-\rangle = -|10\rangle |-\rangle$
            *   $|11\rangle \to (-1)^0 |11\rangle |-\rangle = |11\rangle |-\rangle$
        *   Overall state of $q_0, q_1$ is $\frac{1}{2} (|00\rangle - |01\rangle - |10\rangle + |11\rangle)$.
    *   `H(q_0); H(q_1);`:
        *   Apply H to $q_0, q_1$. H maps $|0\rangle \to |+\rangle, |1\rangle \to |-\rangle$.
        *   Actually, $H^{\otimes 2}$ on $\frac{1}{2} (|00\rangle - |01\rangle - |10

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'The output is |11> with probability 1.0'}

## isqTrain/917

- task_id: `isqTrain/917`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1314`

### Prompt

Help me write isQ code that implements a variant of the boolean_synthesis pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a Boolean XNOR synthesis circuit computing `XNOR(a,b) = NOT(XOR(a,b))` for inputs `a=1, b=1`, storing the result in `q[2]` using a 4-qubit register.

2. **Qubits**: 4 qubits (`q[0]` to `q[3]`), all measured. Inputs are `q[0]=1`, `q[1]=1`; `q[2]` holds the XNOR result; `q[3]` remains unused.

3. **State evolution**:
   - Start: `|0000>`
   - `X(q[0]); X(q[1])`: `|1100>` (set inputs a=1, b=1)
   - `CNOT(q[0], q[2])`: `|1110>` (q[2] flips because q[0]=1)
   - `CNOT(q[1], q[2])`: `|1100>` (q[2] flips again because q[1]=1, XOR(1,1)=0)
   - `X(q[2])`: `|1110>` (negate XOR to get XNOR: NOT(0)=1)

4. **Final measurement**: State `|1110>` yields probability `{|1110>: 1.0}`, confirming XNOR(1,1)=1.

## isqTrain/3484

- task_id: `isqTrain/3484`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `hamiltonian_simulation`
- source: `isq_train_cot`
- dataset_index: `4887`

### Prompt

Code this in isQ: 2-layer QAOA for MaxCut on a triangle graph in isQ.

Layer 1: gamma1=0.4, beta1=0.3
Layer 2: gamma2=0.6, beta2=0.5

For each layer: ZZ on all edges, then Rx mixer.
Declare 3 qubits, measure all.

### Chain-of-thought reasoning

Let me analyze this 2-layer QAOA circuit for MaxCut on a triangle graph.

The triangle graph has 3 edges: (0,1), (0,2), (1,2).

Initial state: |000>
After H on all: |+++> = (1/√8)(|000>+|001>+|010>+|011>+|100>+|101>+|110>+|111>)

Layer 1 (γ₁=0.4, β₁=0.3):
- ZZ on edges: applies e^{-iγZ⊗Z/2} via CNOT-Rz(2γ)-CNOT (but here Rz(0.4) = Rz(2*0.2)? Wait, let me check.

Actually, the standard QAOA cost unitary is exp(-iγΣ Z_iZ_j/2). The decomposition CNOT-Rz(2γ)-CNOT gives exp(-iγ Z_control Z_target). So with Rz(0.4), we get ZZ with γ=0.4.

Wait, CNOT-Rz(θ)-CNOT gives exp(-iθ/2 Z_control Z_target). So with θ=0.4, we get γ=0.2? No...

Let me reconsider. CNOT(a,b); Rz(θ,b); CNOT(a,b) applies exp(-iθ/2)(I - ZaZb)/2... Actually:

CNOT(a,b) maps |0a>|ψb> → |0a>|ψb> and |1a>|ψb> → |1a>X|ψb>

So CNOT-Rz(θ)-CNOT on |00> stays |00> (with phase from Rz(0)), on |01> stays |01> (with phase from Rz(0)), on |10> → |11> → e^{-iθ/2}|11> → e^{-iθ/2}|10>, on |11> → |10> → e^{iθ/2}|10> → e^{iθ/2}|11>.

So the unitary is diag(1, 1, e^{-iθ/2}, e^{iθ/2}) in the computational basis, which equals exp(-iθ/2 Z_a Z_b).

So with θ=0.4, we get exp(-i0.2 Z_a Z_b).

For the triangle, edges are (0,1), (0,2), (1,2).

The cost Hamiltonian for MaxCut is C = Σ_{edges} (I - Z_i Z_j)/2 = 3/2 - (Z₀Z₁ + Z₀Z₂ + Z₁Z₂)/2.

The QAOA applies exp(-iγC) = exp(-iγ 3/2) exp(iγ(Z₀Z₁ + Z₀Z₂ + Z₁Z₂)/2).

Each ZZ term contributes. The state after layer 1 ZZ operations on |+++>:

For a basis state |abc>, the phase accumulated from the three ZZ edges is:
- From Z₀Z₁: if ab same, +1; if different, -1
- From Z₀Z₂: if ac same, +1; if different, -1  
- From Z₁Z₂: if bc same, +1; if different, -1

So for |000>: all same → phase = -0.4/2 × 3 = -0.6? Wait let me be more careful.

The phase from exp(-iγ/2 Z_i Z_j) on |abc>:
- If Zi and Zj eigenvalues are the same (both +1 or both -1), eigenvalue of ZiZj is +1, so phase = -iγ/2 × 1 = -iγ/2
- If different, eigenvalue is -1, phase = -iγ/2 × (-1) = iγ/2

With γ = 0.2 (since Rz(0.4) gives factor 0.2):

Actually wait, I need to reconsider. In the code, Rz(0.4, q) is used. The Rz gate is Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}). So CNOT-Rz(0.4)-CNOT gives diag(1, 1, e^{-i0.2}, e^{i0.2}) = exp(-i0.2 Z⊗Z).

So the effective gamma for each ZZ interaction is 0.2.

Hmm, but the problem says gamma1=0.4. Let me re-read... "Layer 1: gamma1=0.4". And the code uses Rz(0.4). So in the QAOA convention, the cost unitary parameter is being

## isqTrain/4553

- task_id: `isqTrain/4553`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `isq_syntax_for_loop`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3161`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];

procedure main() {
    
    X(q[1]);  // target different qubit

    
    
    
    

    
    CNOT(q[0], q[1]);
    
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);

    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);

    
    CNOT(q[0], q[1]);
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);

    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);

    
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |00⟩

1. X(q[1]): Apply X to qubit 1
   State: |01⟩

2. CNOT(q[0], q[1]): Control q[0], target q[1]
   Since q[0] = 0, no flip on q[1]
   State: |01⟩

3. Rz(π/2, q[1]): Apply Rz(π/2) to qubit 1
   Rz(θ) = [[1,0],[0,e^(iθ)]]
   |01⟩ → e^(iπ/2)|01⟩ = i|01⟩
   State: i|01⟩

4. CNOT(q[0], q[1]): Control q[0], target q[1]
   Since q[0] = 0, no flip
   State: i|01⟩

5. H(q[0]); H(q[1]):
   H⊗H applied to i|01⟩
   H|0⟩ = |+⟩, H|1⟩ = |-⟩
   H⊗H |01⟩ = |+⟩|-⟩
   State: i|+⟩|-⟩

6. CNOT(q[0], q[1]): Control q[0], target q[1]
   CNOT (H⊗H) on |01⟩:
   Actually, let me think more carefully.
   
   i|+⟩|-⟩ = i * (|00⟩ - |01⟩ + |10⟩ - |11⟩)/2
   
   CNOT: |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩
   
   After CNOT: i * (|00⟩ - |01⟩ + |11⟩ - |10⟩)/2
   = i * (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2
   
7. Rz(π/2, q[1]): Apply phase to qubit 1
   |00⟩ → |00⟩
   |01⟩ → i|01⟩
   |10⟩ → |10⟩
   |11⟩ → i|11⟩
   
   State: i * (|00⟩ - i|01⟩ - |10⟩ + i|11⟩)/2
   = i/2 * (|00⟩ - i|01⟩ - |10⟩ + i|11⟩)
   = (i|00⟩ + |01⟩ - i|10⟩ - |11⟩)/2

8. CNOT(q[0], q[1]):
   |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩
   
   State: (i|00⟩ + |01⟩ - i|11⟩ - |10⟩)/2

9. H(q[0]); H(q[1]):
   H⊗H applied to (i|00⟩ + |01⟩ - i|11⟩ - |10⟩)/2
   
   Let me compute H⊗H on each basis state:
   H⊗H|00⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2
   H⊗H|01⟩ = (|00⟩-|01⟩+|10⟩-|11⟩)/2
   H⊗H|10⟩ = (|00⟩+|01⟩-|10⟩-|11⟩)/2
   H⊗H|11⟩ = (|00⟩-|01⟩-|10⟩+|11⟩)/2
   
   Result:
   i/2 * (|00⟩+|01⟩+|10⟩+|11⟩)/2 = i/4 * (|00⟩+|01⟩+|10⟩+|11⟩)
   + 1/2 * (|00⟩-|01⟩+|10⟩-|11⟩)/2 = 1/4 * (|00⟩-|01⟩+|10⟩-|11⟩)
   - i/2 * (|00⟩+|01⟩-|10⟩-|11⟩)/2 = -i/4 * (|00⟩+|01⟩-|10⟩-|11⟩)
   - 1/2 * (|00⟩-|01⟩-|10⟩+|11⟩)/2 = -1/4 * (|00⟩-|01⟩-|10⟩+|11⟩)
   
   Adding up:
   |00⟩: (i + 1 - i - 1)/4 = 0
   |01⟩: (i - 1 - i + 1)/4

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|10>) = 1.0000.'}

## isqTrain/4546

- task_id: `isqTrain/4546`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `975`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[3];

procedure main() {
    
    X(q[0]);  // replaced H with X
    H(q[1]);
    
    CNOT(q[1], q[2]);
    
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants an analysis of an isQ quantum program to predict its measurement probability distribution. The analysis needs to be concise (3-15 lines), use Dirac notation, explain state evolution, and end with the predicted probabilities.

2.  **Analyze the isQ code**:
    *   `qbit q[3];`: Initializes 3 qubits in the state |000>.
    *   `X(q[0]);`: Applies X gate to q[0]. State changes from |000> to |100>.
    *   `H(q[1]);`: Applies H gate to q[1]. State changes to |100> $\otimes$ ( (|0> + |1>)/$\sqrt{2}$ ) $\otimes$ |0> = (1/$\sqrt{2}$) (|100> + |110>).
    *   `CNOT(q[1], q[2]);`: Applies CNOT with control q[1] and target q[2].
        *   If q[1] is |0>, q[2] is |0> -> |00> on (q[1], q[2])
        *   If q[1] is |1>, q[2] is flipped from |0> to |1> -> |11> on (q[1], q[2])
        *   Overall state becomes (1/$\sqrt{2}$) (|100> + |111>).
    *   `M(q[2]);`: Measures q[2]. (Actually, standard output prediction for these systems tracks all qubits). The problem says "Number of qubits measured: 3" in the reference, but `M(q[2])` only measures 1 qubit. Wait, The implementation says: "Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}". Let me re-read carefully.
    *   *Correction/Refinement on circuit implementation*:
        The code applies:
        `X(q[0])` -> |100>
        `H(q[1])` -> 1/sqrt(2) (|100> + |110>)
        `CNOT(q[1], q[2])` -> 1/sqrt(2) (|100> + |111>)
        The implementation says `Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}`. Wait! If q[0] is |1>, the bitstrings should be `|100>` and `|111>`. Why does the reference say `|000>` and `|001>`?
        Let's look at the standard bit ordering in isQ. Sometimes it's little-endian for bitstrings, or I might have misread the reference. Ah, "earlier measured qubit = higher bit" is the `--probs` rule.
        Wait, `M(q[2])` is the *only* measurement in the code. But the reference says 3 qubits are measured and lists {|000>: 0.5, |001>: 0.5}. This implies The implementation might be from a template and might be factually wrong about the probabilities matching *this* exact code, OR the bit ordering is q[0] is the *least* significant bit (rightmost).
        Let's recalculate with q[0] as LSB (index 0 = bit 0):
        |q[2] q[1] q[0]>
        Initial: |000>
        X(q[0]): |001>
        H(q[1]): 1/sqrt(2)(|001> + |011>)
        CNOT(q[1], q[2]): control is q[1], target is q[2].
        When q[1] is 1 (in |011>), q[2] flips from 0 to 1. So |011> becomes |111>.
        State: 1/sqrt(2)(|001> + |111>).
        Measurement: 50% chance |001>, 50% chance |111>.
        Why does the reference say `{|000>: 0.5, |001>: 0.5}`? Let's look at the prompt's reference: "circuit implementation / circuit code: ... Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}". This might be a bug in the reference prompt where it failed to update the probabilities after replacing `H(q[0])` with `X(q[0])` (as hinted by the comment `// replaced H with X`).
        If it was `H(q[0])`, initial is |000> -> 1/sqrt(2)(|000> + |001>).
        H(q[1]) -> 1/

### Reference answer

{'predicted_probs': {'000': 0.5, '001': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.5000, P(|001>) = 0.5000.'}

## isqTrain/3021

- task_id: `isqTrain/3021`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2456`

### Prompt

Implement a quantum circuit in isQ: creates a 4-qubit GHZ state and then applies an X gate to qubit 0.

Requirements:
- Declare `qbit q[4];` at global scope.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a 4-qubit GHZ state, then apply an X gate to qubit 0.
Four qubits `q[0..3]` are declared globally; all 4 are measured at the end.
Step-by-step state evolution:
- Initial: `|0000>`
- After `H(q[0])`: `(|0000> + |1000>) / √2`
- After `CNOT(q[0], q[1])`: `(|0000> + |1100>) / √2`
- After `CNOT(q[1], q[2])`: `(|0000> + |1110>) / √2`
- After `CNOT(q[2], q[3])`: `(|0000> + |1111>) / √2` (standard GHZ state)
- After `X(q[0])`: `(|1000> + |0111>) / √2`
Expected probabilities: {|0111>: 0.5, |1000>: 0.5}, as the final state is an equal superposition of these two computational basis states.

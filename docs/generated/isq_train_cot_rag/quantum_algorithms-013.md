# ISQ training COT RAG corpus: quantum_algorithms shard 13

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4362

- task_id: `isqTrain/4362`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `794`

### Prompt

What does this isQ program output when measured?

```isq
import std;

qbit q[2];

procedure main() {
    // Apply Hadamard to both qubits
    H(q[0]);
    H(q[1]);
    // Encode quadratic form via CZ
    CZ(q[0], q[1]);
    // Transform back
    H(q[0]);
    H(q[1]);
    // Measure
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ code**:
    *   Initialize 2 qubits `q[0]` and `q[1]` in `|00>`.
    *   Apply `H(q[0])` and `H(q[1])`. State becomes `|+> |+> = 0.5 (|00> + |01> + |10> + |11>)`.
    *   Apply `CZ(q[0], q[1])`. State becomes `0.5 (|00> + |01> + |10> - |11>)`.
    *   Apply `H(q[0])` and `H(q[1])`. State becomes `1/sqrt(2) (|00> - |01>)` ? Let's trace carefully.
        *   CZ maps `|+>|+>` to `1/2(|0>|0> + |0>|1> + |1>|0> - |1>|1>)`.
        *   Apply H to q[0]: `1/2 ( (|0>+|1>)|0> + (|0>+|1>)|1> + (|0>-|1>)|0> - (|0>-|1>)|1> ) / sqrt(2)` -> wait, H applied to superposition:
            *   `|00> + |01> + |10> - |11>` -> apply H on qubit 0.
            *   `q[0]` in `|0>` goes to `|+>`, `q[0]` in `|1>` goes to `|->`.
            *   Wait, let's use identities: `H \otimes H (CZ) H \otimes H`.
            *   Since `H Z H = X`, `H_1 H_0 CZ H_0 H_1` = `H_0 H_1 CZ H_0 H_1`.
            *   CZ applies Z on target. `H_1 CZ_{0,1} H_1` -> applies HZH = X on target if control is 1 -> CNOT.
            *   Then `H_0 CNOT_{0,1} H_0` -> H on control of CNOT. CNOT with H on control and target swaps control and target (up to CNOTs). Actually, `H_0 H_1 CZ H_0 H_1` is just `CNOT_{0,1}`.
            *   Let's re-evaluate: `H_1 H_0 CZ H_0 H_1 = H_1 (H_0 CZ H_0) H_1`. Wait, CZ is diagonal, so it commutes with `H_0`? No, CZ applies `|11><11|` minus phase.
            *   Let's just trace the state vector.
            *   Initial: `|00>`
            *   After `H(q[0]), H(q[1])`: `1/2(|00> + |01> + |10> + |11>)`
            *   After `CZ`: `1/2(|00> + |01> + |10> - |11>)`
            *   After `H(q[0]), H(q[1])`:
                *   Apply H to q[1]: `|0> -> |+>`, `|1> -> |->`.
                *   State: `1/2 * 1/\sqrt{2} (|0>(|0>+|1>) + |0>(|0>-|1>) + |1>(|0>+|1>) - |1>(|0>-|1>))` -> `1/2\sqrt{2} (|0>|0> + |0>|1> + |0>|0> - |0>|1> + |1>|0> + |1>|1> - |1>|0> + |1>|1>)`
                *   Simplify: `1/2\sqrt{2} (2|0>|0> + 2|1>|1>) = 1/\sqrt{2}(|00> + |11>)`. This is a Bell state!
            *   Let me re-read this.
            *   `H_0` on `1/2 (|00> + |01> + |10> - |11>)`:
                *   `1/2\sqrt{2} [ (|0>+|1>)|0> + (|0>+|1>)|1> + (|0>-|1>)|0> - (|0>-|1>)|1> ]`
                *   `= 1/2\sqrt{2} [ |0>|0> + |1>|0

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.2500, P(|01>) = 0.2500, P(|10>) = 0.2500, P(|11>) = 0.2500.'}

## isqTrain/4366

- task_id: `isqTrain/4366`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1582`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

// Superdense coding: transmit message '11'
qbit q[2];

procedure main() {
    // Create Bell pair between Alice and Bob
    H(q[0]);
    CNOT(q[0], q[1]);
    // Alice encodes '11': apply Z then X
    // Z flips the phase, X flips the bit
    Z(q[0]);
    X(q[0]);
    // Bob decodes by reversing Bell circuit
    CNOT(q[0], q[1]);
    H(q[0]);
    // Measurement yields the transmitted bits
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The task is to analyze an isQ program, predict its measurement outcomes, provide a step-by-step quantum state evolution using Dirac notation, and output the analysis in a specific format ending with the predicted probability distribution.

2.  **Analyze the isQ program**:
    *   Initialization: `qbit q[2]` -> $|00\rangle$
    *   `H(q[0])` -> $|+0\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
    *   `CNOT(q[0], q[1])` -> $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ (Bell state $\Phi^+$)
    *   `Z(q[0])` -> $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$ (Bell state $\Psi^+$... wait, Z on q0 changes $|1\rangle$ to $-|1\rangle$, so $|00\rangle - |11\rangle$, which is $\Phi^-$)
    *   `X(q[0])` -> $\frac{1}{\sqrt{2}}(|10\rangle - |01\rangle) = \frac{1}{\sqrt{2}}(-|01\rangle + |10\rangle)$ (Bell state $\Psi^+$)
    *   `CNOT(q[0], q[1])` -> $\frac{1}{\sqrt{2}}(-|01\rangle + |10\rangle) \xrightarrow{CNOT} \frac{1}{\sqrt{2}}(-|11\rangle + |11\rangle)$ Wait!
        Let's re-evaluate:
        State before CNOT is $|\psi\rangle = \frac{1}{\sqrt{2}}(-|01\rangle + |10\rangle)$.
        Apply CNOT(0,1): Control is q[0], target is q[1].
        $|01\rangle$ (q0=0, q1=1) -> $|01\rangle$
        $|10\rangle$ (q0=1, q1=0) -> $|11\rangle$
        So state becomes $\frac{1}{\sqrt{2}}(-|01\rangle + |11\rangle)$.
    *   `H(q[0])` ->
        Apply H to q0:
        $-|01\rangle \rightarrow -\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$
        $|11\rangle \rightarrow \frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$
        Sum: $\frac{1}{\sqrt{2}} [ -\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle) + \frac{1}{\sqrt{2}}(|01\rangle - |11\rangle) ]$
        $= \frac{1}{2} [ -|01\rangle - |11\rangle + |01\rangle - |11\rangle ] = \frac{1}{2} [ -2|11\rangle ] = -|11\rangle$.
        Wait, let's carefully re-evaluate `Z(q[0])` and `X(q[0])`.
        Standard superdense coding for '11' applies X then Z or Z then X?
        In the prompt: `Z(q[0]); X(q[0]);`
        Initial Bell state: $|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$
        Apply Z to q0: $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle) = |\Phi^-\rangle$
        Apply X to q0: $\frac{1}{\sqrt{2}}(|10\rangle - |01\rangle) = -\frac{1}{\sqrt{2}}(|01\rangle - |10\rangle) = -|\Psi^+\rangle$
        Let's trace this carefully.
        X on q0 swaps $|0\rangle$ and $|1\rangle$.
        $Z(q0) \rightarrow |\Phi^-\rangle = \frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$.
        $X(q0) \rightarrow \frac{1}{\sqrt{2}}(|10\rangle - |01\rangle)$.
        Now Bob's decoding:
        `CNOT(q[0], q[1])`:
        Control is q0. Target is q1.
        $|10\rangle \rightarrow |11\rangle$
        $

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 1.0000.'}

## isqTrain/2870

- task_id: `isqTrain/2870`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4567`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];
procedure main() {
    X(q[1]);
    H(q[0]);
    ctrl Z(q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |00⟩. `X(q[1])` flips the second qubit to |01⟩.
2. `H(q[0])` puts the first qubit in superposition, creating (|01⟩ + |11⟩)/√2.
3. `ctrl Z(q[0], q[1])` applies a Z gate to q[1] conditioned on q[0]. Since Z|1⟩ = -|1⟩, it flips the phase of the |11⟩ component, resulting in (|01⟩ - |11⟩)/√2.
4. `H(q[0])` is applied again, transforming |0⟩ to (|0⟩ + |1⟩)/√2 and |1⟩ to (|0⟩ - |1⟩)/√2.
5. The state becomes: 1/2 * ((|01⟩ + |11⟩) - (|01⟩ - |11⟩)) = |11⟩.
6. Both qubits are measured, deterministically yielding the state |11⟩.

[0.0, 0.0, 0.0, 1.0]

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2568

- task_id: `isqTrain/2568`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `global_phase`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5200`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;

qbit q[3];

procedure main() {
    X(q[1]);
    
    // QFT
    H(q[2]);
    ctrl S(q[1], q[2]);
    ctrl T(q[0], q[2]);
    
    H(q[1]);
    ctrl S(q[0], q[1]);
    
    H(q[0]);
    
    // SWAP
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    
    M(q[0]); M(q[1]); M(q[2]);
}

```

Circuit 2:
```isq
import std;

qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    X(q[1]);
    
    // QFT
    H(q[2]);
    ctrl S(q[1], q[2]);
    ctrl T(q[0], q[2]);
    
    H(q[1]);
    ctrl S(q[0], q[1]);
    
    H(q[0]);
    
    // SWAP
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes 3 qubits to $|000\rangle$, applies an $X$ gate to $q[1]$ to create the state $|010\rangle$, performs a standard 3-qubit Quantum Fourier Transform (QFT) followed by a swap (three-CNOT decomposition) of $q[0]$ and $q[2]$, and measures the qubits.
2. **Program B** performs the exact same initialization, state preparation, QFT, swap (three-CNOT decomposition), and measurement operations as Program A. 
3. The only difference is the addition of the `GPhase(0.0)` gate at the beginning of Program B.
4. The `GPhase(0.0)` gate applies a global phase factor of $e^{i \cdot 0} = 1$, which is mathematically equivalent to the identity operation. It leaves the quantum state completely unchanged.
5. Because both programs evolve the quantum state identically, their measurement probability distributions are exactly the same.

Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/80

- task_id: `isqTrain/80`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4293`

### Prompt

帮我写一个isQ程序：implements a variant of the gate_decomposition pattern using q[1] -> q[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this task carefully.

The task asks for a variant of the "gate_decomposition" pattern using q[1] -> q[3] with an expanded qubit register.

Analyzing the circuit requirements:
- It has 3 qubits (q[0], q[1], q[2])
- It applies X(q[0]) then H(q[0]) then H(q[0]) again on q[0]
- Measures all 3 qubits
- Expected outcome: |100> with probability 1.0

The implementation essentially does:
1. X(q[0]) -> |1>
2. H(q[0]) -> |-> (which is (|0> - |1>)/sqrt(2))
3. H(q[0]) -> back to |1>

So the final state is |100> and measurement gives |100> with probability 1.

Now I need to create a variant that:
1. Uses q[1] -> q[3] (so the operations are on q[1] instead of q[0]? Or uses qubits q[1], q[2], q[3]?)
2. Has a significantly expanded qubit register
3. Additional qubits left in ground state
4. Expected measurement probabilities: {|100>: 1.0}

Wait, but if I use q[1] -> q[3] and have more qubits, the measurement result would be different...

Let me re-read: "implements a variant of the gate_decomposition pattern using q[1] -> q[3]"

I think this means:
- Use qubits q[1], q[2], q[3] for the operations (shifted from q[0], q[1], q[2])
- Have additional qubits beyond those (expanded register)
- The predicted output still |100>: 1.0

If I have more qubits, say 5 qubits (q[0] to q[4]), and I operate on q[1], q[2], q[3]:
- q[0] stays in |0>
- q[1] gets the X and H operations
- q[2] stays in |0>
- q[3] stays in |0>
- q[4] stays in |0>

The final state would be |0>|1>|0>|0>|0> = |01000>

But the expected measurement is |100>: 1.0

Hmm, let me think about the measurement ordering. The prompt says "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."

So if I measure q[0], q[1], q[2], q[3], q[4] in that order:
- q[0] = higher bit (bit 4 in a 5-bit number)
- q[1] = next bit
- etc.

Wait, but The predicted output only 3 qubits are measured, and the result is |100>.

Maybe the task is:
- Have an expanded register (say 5 qubits)
- Only measure 3 of them (q[1], q[2], q[3])
- The result should be |100> for those measured qubits

Let me re-read the task again...

"Number of qubits measured: 3" - so only 3 qubits are measured.

If I operate on q[1] (X then H then H), and measure q[1], q[2], q[3]:
- q[1] ends up as |1> after X, H, H
- q[2] is |0>
- q[3] is |0>

The measurement bitstring for q[1], q[2], q[3] would be:
- q[1] is the earlier measured qubit = higher bit
- So |100> means q[1]=1, q[2]=0, q[3]=0

That matches! So the circuit should:
1. Have an expanded register (e.g., q[5])
2. Apply X, H, H to q[1]
3. Measure q[1], q[2], q[3]
4. Leave q[0] and q[4] unmeasured (in ground state)

Wait, but The predicted output "{|100>: 1.0}" - is this considering all qubits or just measured ones?

Actually, Analyzing the circuit requirements again:
- It has 3 qubits
- It measures all 3
- Result is |100> = q[0]=1, q[1]=0, q[2]=0

So for my variant:
- I should have more qubits (expanded register)
- Operate on q[1] instead of q[0]
- The measurement result should still be |100>

## isqTrain/3024

- task_id: `isqTrain/3024`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1469`

### Prompt

用isQ实现creates a 4-qubit GHZ state and then applies an X gate to qubit 1.

Requirements:
- Declare `qbit q[4];` at global scope.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a 4-qubit GHZ state and then apply an X gate to qubit 1, yielding a Bell-like superposition of |0100⟩ and |1011⟩.
2. **Qubits**: 4 qubits declared globally (`qbit q[4]`); all 4 are measured.
3. **State evolution**:
   - Start: |0000⟩
   - H(q[0]): (1/√2)(|0000⟩ + |1000⟩)
   - CNOT(q[0], q[1]): (1/√2)(|0000⟩ + |1100⟩)
   - CNOT(q[1], q[2]): (1/√2)(|0000⟩ + |1110⟩)
   - CNOT(q[2], q[3]): (1/√2)(|0000⟩ + |1111⟩) — standard GHZ state
   - X(q[1]): (1/√2)(|0100⟩ + |1011⟩)
4. **Measurement**: The final state is an equal superposition of |0100⟩ and |1011⟩, each with amplitude 1/√2, giving probabilities {|0100⟩: 0.5, |1011⟩: 0.5}.

## isqTrain/1169

- task_id: `isqTrain/1169`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3116`

### Prompt

I need an isQ program to implements the iqp_circuit pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze the IQP circuit pattern step by step.

The circuit has 3 qubits and follows the pattern: H layer → diagonal gates → H layer, with an identity X-X pair added before measurement.

Step-by-step state evolution:

1. Initial state: |000⟩

2. First H layer: H(q[0]), H(q[1]), H(q[2])
   |000⟩ → |+++⟩ = (1/√8)(|0⟩+|1⟩)⊗(1/√8)(|0⟩+|1⟩)⊗(1/√8)(|0⟩+|1⟩)
   = (1/2√2) Σ|x⟩ for x ∈ {0,1}³

3. Diagonal layer:
   - T(q[0]): applies phase e^(iπ/4) when q[0] is |1⟩
   - T(q[1]): applies phase e^(iπ/4) when q[1] is |1⟩
   - T(q[2]): applies phase e^(iπ/4) when q[2] is |1⟩
   - CZ(q[0], q[1]): applies -1 phase when both q[0] and q[1] are |1⟩
   - CZ(q[1], q[2]): applies -1 phase when both q[1] and q[2] are |1⟩

4. Second H layer: transforms back to computational basis

5. X(q[0]) followed by X(q[0]): identity operation, cancels out

6. Measurements on all qubits

Let me calculate the predicted output more carefully.

After H⊗³: |ψ⟩ = (1/2√2) Σ_x |x⟩

After diagonal gates, each basis state |x⟩ = |x₂x₁x₀⟩ gets phase:
φ(x) = π/4 * (x₀ + x₁ + x₂) + π * (x₀·x₁ + x₁·x₂)

Wait, let me be more careful. T applies phase π/4 to |1⟩ component, so:
- T(q[0]): phase π/4 * x₀
- T(q[1]): phase π/4 * x₁  
- T(q[2]): phase π/4 * x₂
- CZ(q[0], q[1]): phase π * x₀ * x₁
- CZ(q[1], q[2]): phase π * x₁ * x₂

So φ(x₀,x₁,x₂) = π/4 * (x₀ + x₁ + x₂) + π * (x₀x₁ + x₁x₂)

|ψ⟩ = (1/2√2) Σ_x e^(iφ(x)) |x⟩

Then H⊗³ is applied. The amplitude of |z⟩ after H⊗³ is:
a(z) = (1/2√2) * (1/2√2) Σ_x (-1)^(z·x) e^(iφ(x))
     = (1/8) Σ_x (-1)^(z·x) e^(iφ(x))

The X-X pair cancels, so the final state before measurement is this.

Let me compute |a(z)|² for each z:

For z = 000: a = (1/8) Σ_x e^(iφ(x)) where all x ∈ {0,1}³

φ(000) = 0
φ(001) = π/4
φ(010) = π/4
φ(011) = π/4 + π/4 + π = 3π/4 + π = 3π/2... wait let me recalculate

x₀ = first qubit (q[0]), x₁ = second qubit (q[1]), x₂ = third qubit (q[2])

For |x₂x₁x₀⟩:
- x = 000: φ = 0
- x = 001: φ = π/4 (only x₀=1)
- x = 010: φ = π/4 (only x₁=1)
- x = 011: φ = π/4 + π/4 + π·1·1 = π/2 + π = 3π/2
- x = 100: φ = π/4 (only x₂=1)
- x = 101: φ = π/4 + π/4 = π/2 (x₀=1, x₂=1, no CZ applies)
- x = 110: φ = π/4 + π/4 + π = 3π/2 (x₁=1, x₂=1, CZ(q[1],q[2]) applies)
- x = 111: φ = 3·π

## isqQA/quantum_algorithms/46_principle_advantage

- task_id: `isqQA/quantum_algorithms/46_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `principle_advantage`, `algorithm`, `HHL线性方程组算法`
- source: `qa_pipeline`
- dataset_index: `55`

### Prompt

请详细解析HHL算法求解线性方程组 $Ax=b$ 的宏观原理，并深入对比其与经典算法的时间复杂度。HHL算法为何能实现指数级加速？这种加速优势在物理和数学上受制于哪些底层前提？

### Reference answer

HHL算法（由Harrow、Hassidim和Lloyd提出）是量子线性系统求解领域的里程碑算法。其宏观原理并不是像经典算法那样逐个计算出解向量 $x$ 的每个元素，而是利用量子态的叠加特性，将解编码到一个量子态 $|x\rangle$ 中，使其满足 $A|x\rangle = |b\rangle$（其中 $A$ 是厄米矩阵，$|b\rangle$ 是通过量子态制备的输入向量）。

在数学原理上，HHL算法主要包含三个核心步骤：
1. **量子相位估计（QPE）**：将矩阵 $A$ 的特征分解量子化。通过QPE，可以将态 $|b\rangle$ 在 $A$ 的特征基下展开，并将对应的特征值 $\lambda_j$ 提取到辅助寄存器中，系统状态变为 $\sum_j \beta_j |u_j\rangle |\lambda_j\rangle$，其中 $u_j$ 是特征向量。
2. **受控旋转**：引入另一个辅助比特，根据提取出的特征值 $\lambda_j$ 的倒数进行受控旋转。这一步的目的是在量子态的振幅中引入 $1/\lambda_j$ 的比例关系，系统状态变为 $\sum_j \beta_j |u_j\rangle |\lambda_j\rangle (\sqrt{1 - C^2/\lambda_j^2}|0\rangle + C/\lambda_j|1\rangle)$。
3. **逆量子相位估计与测量**：执行逆QPE解除特征值寄存器的纠缠，并对辅助旋转比特进行测量。当测量结果为 $|1\rangle$ 时，系统的状态将以极高的概率坍缩为与 $A^{-1}|b\rangle$ 成正比的量子态，即成功制备出 $|x\rangle$。

**时间复杂度对比与加速来源：**
假设矩阵 $A$ 是一个规模为 $N \times N$ 的 $s$-稀疏矩阵（每行非零元素最多为 $s$），条件数为 $\kappa$。求解此类问题的最佳经典算法（如共轭梯度法）的时间复杂度通常为 $O(N s \kappa \log(1/\epsilon))$。
相比之下，HHL算法的时间复杂度大约为 $O(\log(N) s^2 \kappa^2 / \epsilon)$。
HHL算法的指数级加速 $O(N) \to O(\log(N))$ 来源于量子态的指数级编码能力。经典计算机需要 $O(N)$ 的内存来存储长度为 $N$ 的向量，而量子计算机仅需 $O(\log N)$ 个量子比特即可表示包含 $N$ 个振幅的叠加态。量子门操作作用于整个叠加态上，实现了并行计算。

**底层前提与局限性：**
这种指数级加速并非无条件的。首先，HHL算法对 $\epsilon$（精度）的依赖是多项式级的 $O(1/\epsilon)$，而某些经典算法对精度是对数依赖的。其次，算法的复杂度随矩阵条件数 $\kappa$ 呈平方级恶化。更致命的限制在于数据的输入与输出（I/O瓶颈）：
- **输入限制**：如果要从经典数据制备量子态 $|b\rangle$，通常需要 $O(N)$ 的时间，这会直接抹杀量子加速。因此，HHL算法仅适用于 $|b\rangle$ 能够被量子电路高效生成（如QRAM或特定物理态）的场景。
- **输出限制**：由于量子态无法直接被全部读取（读取整个态会导致 $O(N)$ 的坍缩），我们无法通过HHL算法获得经典向量 $x$ 的全貌。因此，HHL算法通常只能作为更大量子算法的子程序，用于计算解向量 $x$ 的某个统计期望值，如 $\langle x|M|x\rangle$。只有在这些特定的应用上下文中，HHL算法的指数级加速才具有实质性的物理和工程意义。

## isqTrain/2652

- task_id: `isqTrain/2652`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `global_phase`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2736`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[4];

procedure main() {
    // Put input a in superposition, set b=1
    H(q[0]);
    X(q[1]);
    // Half adder: sum = a XOR b
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    // Carry = a AND b
    Toffoli(q[0], q[1], q[3]);
    // Measure sum and carry
    M(q[2]);
    M(q[3]);
}

```

Second program:
```isq
import std;
qbit q[4];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Put input a in superposition, set b=1
    H(q[0]);
    X(q[1]);
    // Half adder: sum = a XOR b
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    // Carry = a AND b
    Toffoli(q[0], q[1], q[3]);
    // Measure sum and carry
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A** implements a half adder: H(q[0]) creates superposition on input `a`, X(q[1]) sets input `b=1`, then CNOTs compute sum = a XOR b on q[2], and Toffoli computes carry = a AND b on q[3]. Final state: (|0110> + |1101>)/√2, giving 50% chance each for (q[2],q[3]) = (1,0) or (0,1).

2. **Program B** applies exactly the same circuit as Program A, preceded by GPhase(0.0).

3. **Key difference**: Program B adds `GPhase(0.0)` at the beginning, which applies a global phase of e^(i·0) = 1 (the identity).

4. **Measurement probabilities**: GPhase(0.0) is mathematically trivial—it multiplies the entire state by 1, changing nothing. Both programs produce the identical quantum state before measurement, and thus identical measurement distributions.

5. **Verdict**: Yes, the programs are equivalent.

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/2710

- task_id: `isqTrain/2710`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_if_else`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5021`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

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

1.  **Analyze the Request:**
    *   Task: Explain the given isQ quantum circuit and predict its output probability distribution.
    *   Circuit: A quantum teleportation circuit.
    *   Initial state: `X(q_1)` applied to `|000>`.
    *   Qubits: `q_1` (qsrc), `q_2` (qanc), `q_3` (qdest).
    *   Operations: `X(q_1)` -> `H(q_2)` -> `CNOT(q_2, q_3)` -> `CNOT(q_1, q_2)` -> `H(q_1)` -> `M(q_1)`, `M(q_2)` -> conditional `X(q_3)`, `Z(q_3)` based on measurements.
    *   Output: `M(q_3)` is printed.
    *   Expected Probabilities: `{'001': 0.25, '010': 0.25, '101': 0.25, '110': 0.25}` (Wait, let me carefully check the indexing for `M(q_3)`. The prompt says "List the probability for every basis state in order from |0...0> to |1...1>." And then The resulting probabilities should be given as `{'001': 0.25, '010': 0.25, '101': 0.25, '110': 0.25}`. This means *all three qubits* are being measured, or at least the output format requires the 3-qubit state probabilities. Wait, the code only prints `M(q_3)`, but the expected is a 3-qubit distribution. Ah, `--probs` mode tracks the probabilities of all qubits in a bitstring. But Let me re-analyze the: `{'001': 0.25, '010': 0.25, '101': 0.25, '110': 0.25}`. Wait, if `q_1` and `q_2` are measured *mid-circuit*, they collapse! And then their collapsed values are used for classical control.
    Let's trace carefully.

2.  **Trace the State:**
    *   Initial: $|000\rangle$ (q_1, q_2, q_3)
    *   `X(q_1)`: State becomes $|100\rangle$
    *   `H(q_2)`: State becomes $\frac{1}{\sqrt{2}}(|100\rangle + |110\rangle)$
    *   `CNOT(q_2, q_3)`: State becomes $\frac{1}{\sqrt{2}}(|100\rangle + |111\rangle)$
    *   `CNOT(q_1, q_2)`: State becomes $\frac{1}{\sqrt{2}}(|110\rangle + |101\rangle)$
    *   `H(q_1)`:
        *   $|11\rangle \to \frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$
        *   $|10\rangle \to \frac{1}{\sqrt{2}}(|00\rangle - |10\rangle)$
        *   Total state: $\frac{1}{2}(|010\rangle - |110\rangle + |001\rangle - |101\rangle)$
    *   `m1 = M(q_1)`, `m2 = M(q_2)`:
        *   The state collapses. There are 4 equally probable outcomes for `(q_1, q_2)`:
            *   `00`: $q_3$ is in state $|1\rangle$. Measured state $|001\rangle$ (prob 0.25).
            *   `01`: $q_3$ is in state $|1\rangle$. Measured state $|011\rangle$? No, let's look at the total state: $\frac{1}{2}(|01\rangle_{12}|0\rangle_3 - |11\rangle_{12}|0\rangle_3 + |00\rangle_{12}|1\rangle_3 - |10\rangle_{12}|1\rangle_3)$.
            Wait! Let me re-evaluate `H(q_1)` and `CNOT(q_1, q_2)` on $\frac{1}{\sqrt{2}}(|100\rangle + |111\rangle)$.
            Let's write it as $|1\rangle_1 (\frac{1}{\sqrt{2}}(|00\rangle_{23} + |11\rangle_{23}))$. This is correct.
            Then `CNOT(q_1, q_2)`: $

### Reference answer

{'predicted_probs': {'001': 0.25, '010': 0.25, '101': 0.25, '110': 0.25}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

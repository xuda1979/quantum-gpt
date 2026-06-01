# ISQ training COT RAG corpus: state_preparation shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4317

- task_id: `isqTrain/4317`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3171`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[3];

procedure main() {
    // Prepare state |101>
    X(q[0]);
    X(q[2]);
    // Measure all qubits
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 3 qubits in the state |000>, then applies X gates to q[0] and q[2] to prepare the state |101>.
2. On q[0], the sequence H, Z, H is applied. The comment correctly notes that HZH = X. 
3. Applying this X gate to q[0] flips its state from |1> to |0>, changing the global state to |001> (ignoring a global phase).
4. Finally, all three qubits are measured in the computational basis.

Predicted probability distribution: {|001>: 1.0}

### Reference answer

{'predicted_probs': {'001': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|001>) = 1.0000.'}

## isqTrain/2587

- task_id: `isqTrain/2587`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4154`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;

qbit q[1];

procedure main() {
    // cos(pi/8)|0> + sin(pi/8)|1>
    Ry(pi/4.0, q[0]);
    M(q[0]);
}

```

Second program:
```isq
import std;

qbit q[1];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // cos(pi/8)|0> + sin(pi/8)|1>
    Ry(pi/4.0, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes a qubit in |0> and applies a rotation gate Ry(pi/4), preparing the state cos(pi/8)|0> + sin(pi/8)|1>. 
2. **Program B** initializes a qubit in |0>, applies a global phase gate GPhase(0.0), and then applies the same Ry(pi/4) gate.
3. The only difference between the two programs is the GPhase(0.0) operation in Program B, which introduces a global phase of $e^{i \cdot 0} = 1$.
4. Because a global phase of 1 is physically meaningless and does not alter the quantum state vector, both programs prepare the exact same final state.
5. Therefore, the measurement probability distributions are identical.

Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1443

- task_id: `isqTrain/1443`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3689`

### Prompt

Code this in isQ: Prepare the computational basis state |0001> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare the computational basis state |0001> on 4 qubits and measure them.
2. Qubits: Requires 4 qubits (q[0] to q[3]), all of which are measured.
3. Evolution:
   - Initial state is |0000>.
   - Applying X(q[3]) flips the 4th qubit from |0> to |1>, resulting in the state |0001>.
4. Probabilities: The state is exactly |0001>, so measurement yields `0001` with a probability of 1.0.

## isqTrain/4784

- task_id: `isqTrain/4784`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `isq_syntax_while_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `3179`

### Prompt

Write isQ code for the following quantum task: implements: while-loop counter variant 0. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a quantum circuit with Hadamard gate and measurement alongside a classical while-loop counter.
2. One qubit q[0] is used and measured.
3. State evolution: |0⟩ → H → |+⟩ = (|0⟩ + |1⟩)/√2.
4. Measurement collapses |+⟩ to |0⟩ or |1⟩, each with probability 0.5.
5. The while-loop only increments a classical counter (count from 0 to 2) and doesn't affect quantum state.
6. Final expected probabilities: {|0⟩: 0.5, |1⟩: 0.5}.

## isqTrain/1366

- task_id: `isqTrain/1366`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2009`

### Prompt

用isQ实现Prepare a GHZ state on 4 qubits, then apply a Z gate to the first qubit to create a relative phase. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to create a 4-qubit GHZ state, apply a Z gate to the first qubit to introduce a relative phase, and measure all qubits.
Four qubits are used, and all four are measured.
Starting in |0000>, applying H to q[0] yields (|0000> + |1000>)/√2.
Three CNOT gates (controlled by q[0]) entangle all qubits into the GHZ state: (|0000> + |1111>)/√2.
Applying the Z gate to q[0] flips the phase of the |1> component, resulting in (|0000> - |1111>)/√2.
Since the global and relative phases do not affect measurement probabilities, the final outcomes are |0000> and |1111>, each with a probability of 0.5.

## isqTrain/3392

- task_id: `isqTrain/3392`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1840`

### Prompt

用isQ实现an isQ program: in a 4-qubit register, apply X then H to q[2] only. Other qubits stay |0>. Measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply X then H to q[2] in a 4-qubit register, leaving others in |0>, then measure all.

All 4 qubits are measured: q[0], q[1], q[2], q[3].

State evolution:
- Initial: |0000⟩
- X(q[2]): |0010⟩ (flips q[2] from |0⟩ to |1⟩)
- H(q[2]): H|1⟩ = (|0⟩ − |1⟩)/√2, so state becomes (|0000⟩ − |0010⟩)/√2

Expected probabilities: {|0000⟩: 0.5, |0010⟩: 0.5} — equal superposition of q[2] being |0⟩ or |1⟩, with all other qubits remaining |0⟩.

## isqTrain/3226

- task_id: `isqTrain/3226`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1101`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: apply Ry(1*pi/4) to q[0] and Ry(1*pi/4) to q[1], then measure both (no entanglement).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize a 2-qubit system and apply independent $R_y(\pi/4)$ rotations to each qubit.
2. **Qubits**: Requires 2 qubits (`q[0]` and `q[1]`), both of which are measured.
3. **State Evolution**: 
   - Both qubits start in the ground state $|00\rangle$.
   - Applying $R_y(\pi/4)$ to `q[0]` puts it in the state $\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle$. 
   - Applying $R_y(\pi/4)$ to `q[1]` puts it in the identical superposition $\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle$.
   - The final combined quantum state is $(\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle) \otimes (\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle)$.
4. **Probabilities**: Since the qubits are unentangled, measurement probabilities are the products of the individual qubit probabilities. The probability of measuring $|0\rangle$ is $\cos^2(\pi/8) \approx 0.8535$ and $|1\rangle$ is $\sin^2(\pi/8) \approx 0.1464$. This yields $P(|00\rangle) \approx 0.7286$, $P(|01\rangle) = P(|10\rangle) \approx 0.125$, and $P(|11\rangle) \approx 0.0214$.

## isqTrain/3231

- task_id: `isqTrain/3231`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4230`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply Ry(1*pi/6) to q[0] and Ry(1*pi/3) to q[1], then measure both (no entanglement).

### Chain-of-thought reasoning

The goal is to create a reasoning section for the isQ quantum program.
1. Goal: Apply independent Ry rotations to two qubits and measure them.
2. Qubits: 2 qubits, q[0] and q[1], both measured.
3. State evolution:
   - Initial state: |00>
   - Apply Ry(pi/6) to q[0]: cos(pi/12)|0> + sin(pi/12)|1> = cos(15°)|0> + sin(15°)|1>
   - Apply Ry(pi/3) to q[1]: cos(pi/6)|0> + sin(pi/6)|1> = cos(30°)|0> + sin(30°)|1>
   - State of system: (cos(15°)|0> + sin(15°)|1>) (cos(30°)|0> + sin(30°)|1>)
   - cos(15°) = sqrt((1+cos(30°))/2) = sqrt((1+sqrt(3)/2)/2) ≈ 0.9659
   - sin(15°) = sqrt((1-cos(30°))/2) = sqrt((1-sqrt(3)/2)/2) ≈ 0.2588
   - cos(30°) = sqrt(3)/2 ≈ 0.8660
   - sin(30°) = 1/2 = 0.5
4. Expected probabilities:
   - P(|00>) = cos²(15°) * cos²(30°) ≈ 0.9330 * 0.75 = 0.6998
   - P(|01>) = cos²(15°) * sin²(30°) ≈ 0.9330 * 0.25 = 0.2333
   - P(|10>) = sin²(15°) * cos²(30°) ≈ 0.0670 * 0.75 = 0.0502
   - P(|11>) = sin²(15°) * sin²(30°) ≈ 0.0670 * 0.25 = 0.0167
   Wait, in `--probs` mode, earlier measured qubit = higher bit. So M(q[0]) then M(q[1]). `q[0]` is the higher bit. The prompt says `P(|00>) = 0.6998`. Let me check the math.
   `q[0]` corresponds to the left bit in `|00>`.
   cos²(pi/12) * cos²(pi/6) = (1/4)(2 + sqrt(3)) * 3/4 = 3/16 (2 + sqrt(3)) = 3/16 (3.732) = 0.69975.
   cos²(pi/12) * sin²(pi/6) = (1/4)(2 + sqrt(3)) * 1/4 = (2 + sqrt(3))/16 = 0.23325.
   sin²(pi/12) * cos²(pi/6) = (1/4)(2 - sqrt(3)) * 3/4 = 3/16 (2 - sqrt(3)) = 3/16 (0.268) = 0.0502.
   sin²(pi/12) * sin²(pi/6) = (1/4)(2 - sqrt(3)) * 1/4 = (2 - sqrt(3))/16 = 0.01675.

Let's write down the reasoning:
## Reasoning
1. **Goal:** Independently rotate two qubits using Ry gates and measure their states.
2. **Qubits:** Requires 2 qubits, `q[0]` and `q[1]`, both of which are measured.
3. **State Evolution:**
   - Initialize both to |00>.
   - Apply `Ry(pi/6)` to `q[0]`: yields `cos(pi/12)|0> + sin(pi/12)|1>` for the first qubit.
   - Apply `Ry(pi/3)` to `q[1]`: yields `cos(pi/6)|0> + sin(pi/6)|1>` for the second qubit.
   - The combined unentangled state is `(cos(pi/12)|0> + sin(pi/12)|1>) ⊗ (cos(pi/6)|0> + sin(pi/6)|1>)`.
4. **Probabilities:** Since the state is unentangled, measurement probabilities are the product of individual qubit probabilities. `P(|00>) = cos^2(pi/12)cos

## isqTrain/1370

- task_id: `isqTrain/1370`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `4255`

### Prompt

I need an isQ program to Prepare a GHZ state on 5 qubits and measure all qubits in the X basis (apply H before measurement).

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. Goal: Prepare a 5-qubit GHZ state and measure all qubits in the X basis.

2. Qubits: 5 qubits (q[0] through q[4]), all measured.

3. State evolution:
- Start: |00000⟩
- H(q[0]): (|00000⟩ + |10000⟩)/√2
- CNOT(q[0], q[1]): (|00000⟩ + |11000⟩)/√2
- CNOT(q[0], q[2]): (|00000⟩ + |11100⟩)/√2
- CNOT(q[0], q[3]): (|00000⟩ + |11110⟩)/√2
- CNOT(q[0], q[4]): (|00000⟩ + |11111⟩)/√2

Now we have the GHZ state: (|00000⟩ + |11111⟩)/√2

For X-basis measurement, apply H to all qubits:
H⊗5 (|00000⟩ + |11111⟩)/√2

H⊗5|00000⟩ = |+++++⟩ = sum over all even parity states (even number of 1s)
H⊗5|11111⟩ = |----- ⟩ = sum over even parity minus odd parity

Actually let me be more careful. H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = |−⟩ = (|0⟩ - |1⟩)/√2

H⊗5|00000⟩ = |+++++⟩ = (1/√2)⁵ Σ|x⟩ for all x ∈ {0,1}⁵ = (1/4√2) Σ|x⟩

H⊗5|11111⟩ = |-----⟩ = (1/√2)⁵ Σ (-1)^x₁+x₂+x₃+x₄+x₅ |x⟩ = (1/4√2) Σ (-1)^|x| |x⟩

So the final state is:
(1/2)(H⊗5|00000⟩ + H⊗5|11111⟩) = (1/2) · (1/4√2) [Σ|x⟩ + Σ(-1)^|x||x⟩]

The terms add for even parity (|x| even) and cancel for odd parity.

So probability = (1/2 · 1/4√2 · 2)² = (1/4)² · (1/2) = 1/32 × 2... wait let me recalculate.

The normalization: (1/2) · (1/4√2) · 2 = 1/(4√2) for each even parity state.

Probability for each even parity state: (1/(4√2))² = 1/32

There are 2⁴ = 16 even parity states (C(5,0) + C(5,2) + C(5,4) = 1 + 10 + 5 = 16).
Total probability = 16 × 1/32 = 1/2. That's not right.

Let me redo. The GHZ state is (|00000⟩ + |11111⟩)/√2.

After applying H to all 5 qubits:
(1/√2)(H⊗5|00000⟩ + H⊗5|11111⟩)
= (1/√2)((1/√2)⁵ Σ_all x |x⟩ + (1/√2)⁵ Σ_all x (-1)^|x| |x⟩)
= (1/√2)(1/4√2)(Σ|x⟩ + Σ(-1)^|x||x⟩)
= (1/8)(Σ_even |x⟩ · 2)
= (1/4) Σ_even |x⟩

Wait, that doesn't normalize properly either. Let me be more careful.

H⊗5|00000⟩ = (1/√2)⁵ Σ_x |x⟩ = (1/4√2) Σ_x |x⟩

There are 32 terms, each with amplitude 1/(4√2). Check: 32 × (1/(4√2))² = 32/(32) = 1. Good.

H⊗5|11111⟩ = (1/√2)⁵ Σ_x (-1)^|x| |x⟩ = (1/4√2) Σ_x (-1)^|x| |x⟩

Final state = (1/√2)[(1/4√2) Σ_x |x⟩ + (1/4√2) Σ_x (-1)^|x| |x⟩]
= (1/√2)(1/4

## isqTrain/4749

- task_id: `isqTrain/4749`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4888`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    X(q[0]); // additional bit flip
    M(q[0]); M(q[1]);
}

```

Second program:
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    H(q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** applies a Hadamard gate to q0, followed by a CNOT with q0 as control and q1 as target, creating the Bell state $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$. It then applies an X gate to q0, resulting in the final state $\frac{1}{\sqrt{2}}(|10\rangle + |01\rangle)$.
2. **Program B** applies a Hadamard gate to both q0 and q1, resulting in the separable uniform superposition $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
3. **Key difference**: Program A generates an entangled state, while Program B generates a separable product state. Additionally, the X gate in Program A flips the q0 state, removing the $|00\rangle$ and $|11\rangle$ components.
4. **Measurement probabilities**: Program A has a 50% chance of measuring $|01\rangle$ and a 50% chance of measuring $|10\rangle$. Program B has a 25% chance for each of the four possible basis states ($|00\rangle$, $|01\rangle$, $|10\rangle$, $|11\rangle$).
5. **Verdict**: Not equivalent.

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'01': 0.5, '10': 0.5}, 'probs_b': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}}

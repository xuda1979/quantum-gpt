# ISQ training COT RAG corpus: state_preparation shard 36

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1751

- task_id: `isqTrain/1751`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2657`

### Prompt

Write an isQ program that Prepare a 7-qubit GHZ state: (|0000000> + |1111111>) / sqrt(2). Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare a 7-qubit GHZ state (|0000000⟩ + |1111111⟩)/√2 and measure all qubits.

Quantum state evolution:
1. Initialize 7 qubits: |ψ⟩ = |0000000⟩
2. H(q[0]): |ψ⟩ = (|0000000⟩ + |1000000⟩)/√2
3. CNOT(q[0], q[1]): |ψ⟩ = (|0000000⟩ + |1100000⟩)/√2
4. CNOT(q[0], q[2]): |ψ⟩ = (|0000000⟩ + |1110000⟩)/√2
5. CNOT(q[0], q[3]): |ψ⟩ = (|0000000⟩ + |1111000⟩)/√2
6. CNOT(q[0], q[4]): |ψ⟩ = (|0000000⟩ + |1111100⟩)/√2
7. CNOT(q[0], q[5]): |ψ⟩ = (|0000000⟩ + |1111110⟩)/√2
8. CNOT(q[0], q[6]): |ψ⟩ = (|0000000⟩ + |1111111⟩)/√2

All 7 qubits are measured. Since the final state is an equal superposition of |0000000⟩ and |1111111⟩, measurement yields each outcome with probability 0.5.

## isqTrain/3227

- task_id: `isqTrain/3227`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5458`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply Ry(1*pi/3) to q[0] and Ry(1*pi/4) to q[1], then measure both (no entanglement).

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task type: `code_generation` (but the output should be *only* the reasoning).
    *   Input prompt: Write an isQ program applying $R_y(1\pi/3)$ to $q[0]$ and $R_y(1\pi/4)$ to $q[1]$, measure both.
    *   Target output format: "## Reasoning" followed by 3-8 lines explaining the circuit's goal, qubits used, state evolution, and probability derivation.
    *   Specific rules: Use Dirac notation. No isQ code blocks. Concise.

2.  **Deconstruct the Quantum Circuit:**
    *   Initial state: $|00\rangle$
    *   Gate 1: $R_y(\pi/3)$ on $q[0]$.
        *   $R_y(\theta)|0\rangle = \cos(\theta/2)|0\rangle + \sin(\theta/2)|1\rangle$.
        *   State of $q[0]$ becomes $\cos(\pi/6)|0\rangle + \sin(\pi/6)|1\rangle = \frac{\sqrt{3}}{2}|0\rangle + \frac{1}{2}|1\rangle$.
    *   Gate 2: $R_y(\pi/4)$ on $q[1]$.
        *   State of $q[1]$ becomes $\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle$.
    *   Combined state: $(\frac{\sqrt{3}}{2}|0\rangle + \frac{1}{2}|1\rangle) \otimes (\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle)$.

3.  **Calculate Probabilities (to match reasoning):**
    *   $P(|00\rangle) = |\frac{\sqrt{3}}{2} \cos(\pi/8)|^2 = \frac{3}{4} \cdot \frac{1+\sqrt{2}/2}{2} = \frac{3}{8} (1 + \frac{1}{\sqrt{2}}) \approx 0.6402$
    *   $P(|01\rangle) = |\frac{\sqrt{3}}{2} \sin(\pi/8)|^2 = \frac{3}{4} \cdot \frac{1-\sqrt{2}/2}{2} = \frac{3}{8} (1 - \frac{1}{\sqrt{2}}) \approx 0.1098$
    *   $P(|10\rangle) = |\frac{1}{2} \cos(\pi/8)|^2 = \frac{1}{4} \cdot \frac{1+\sqrt{2}/2}{2} = \frac{1}{8} (1 + \frac{1}{\sqrt{2}}) \approx 0.2134$
    *   $P(|11\rangle) = |\frac{1}{2} \sin(\pi/8)|^2 = \frac{1}{4} \cdot \frac{1-\sqrt{2}/2}{2} = \frac{1}{8} (1 - \frac{1}{\sqrt{2}}) \approx 0.0366$
    *   Wait, the prompt says "array indexed by measurement bitstring (earlier measured qubit = higher bit)". If q[0] is measured first, it's the higher bit. So $q[0]$ determines the first bit. So $q[0]$ has prob $3/4$ for $|0\rangle$ and $1/4$ for $|1\rangle$. This matches the calculated values above.

4.  **Draft the Reasoning Section:**
    *   *Goal*: Apply independent Ry rotations to two qubits and measure them.
    *   *Qubits*: 2 qubits ($q[0], q[1]$), both are measured.
    *   *Evolution*:
        *   Start at $|00\rangle$.
        *   Apply $R_y(\pi/3)$ to $q[0]$: $\frac{\sqrt{3}}{2}|0\rangle + \frac{1}{2}|1\rangle$.
        *   Apply $R_y(\pi/4)$ to $q[1]$: $\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle$.
        *   Final state: $\left(\frac{\sqrt{3}}{2}|0\rangle + \frac{1}{2}|1\rangle\right) \otimes \left

## isqTrain/3842

- task_id: `isqTrain/3842`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5396`

### Prompt

Code this in isQ: Prepare the graph state for a complete 4 graph with 4 nodes and edges [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]. Apply Hadamard to all qubits, then CZ for each edge. Measure all 4 qubits.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate reasoning for a quantum circuit in isQ.
    *   Circuit: Graph state for K4 (complete graph with 4 nodes). H on all qubits, then CZ on all edges [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]. Measure all.
    *   Format: Start with "## Reasoning". Do not include the code. Use Dirac notation.
    *   Expected Probabilities: Equal probability for all 16 states (0.0625 each).
    *   Constraint: 3-8 lines for simple circuits, up to 15 for complex ones.

2.  **Deconstruct the Circuit:**
    *   Initial state: |0000>
    *   After H on all: |++++> = 1/4 (|0000> + |0001> + ... + |1111>)
    *   Graph state: CZ gates on all pairs. CZ|00>=|00>, CZ|01>=|01>, CZ|10>=|10>, CZ|11>=-|11>.
    *   Since we apply CZ on *all* pairs, any basis state with an even number of 1s (0, 2, 4) gets a + sign, any with an odd number of 1s (1, 3) gets a - sign.
    *   Let's check the signs:
        *   |0000>: 0 ones -> (+)
        *   1 one (e.g., |0001>): 3 CZs touching the '1' -> (-)
        *   2 ones (e.g., |0011>): 1 CZ on that pair, others don't affect -> (-) Wait. 2 ones: there's 1 edge between the two 1s. Wait, what about edges to 0s? CZ|10> with control 0 = |10>. So only edges between 1s matter. 2 ones -> 1 edge -> (-).
        *   3 ones (e.g., |0111>): 3 edges among the 1s -> (-)
        *   4 ones (|1111>): 6 edges among the 1s -> (+)
    *   So the state is (1/4) * sum_{x in {0,1}^4} (-1)^{|x| + (|x| mod 2 == 2 ? 1 : 0 ? Wait.}
    *   Actually, the sign is (-1)^(number of edges between 1s).
    *   Let's trace:
        *   |0000> (0 edges): +
        *   1 one (0 edges): +
        *   2 ones (1 edge): -
        *   3 ones (3 edges): -
        *   4 ones (6 edges): +
    *   Wait, let's re-evaluate the phase of 1 one. If |0001>, qubit 3 is 1, others 0. Edges between 1s: 0. So sign is +. But earlier I said CZ touches it... wait! CZ *control* does not apply a phase. CZ applies phase to BOTH if both are 1.
    *   Ah! CZ(a,b) applies -1 *only* if BOTH a and b are 1.
    *   So the sign is (-1)^(number of edges with both ends = 1).
    *   For K4:
        *   0 ones: 0 edges -> +1
        *   1 one: 0 edges -> +1
        *   2 ones: 1 edge -> -1
        *   3 ones: 3 edges -> -1
        *   4 ones: 6 edges -> +1
    *   Let's check: sum of amplitudes squared.
    *   Amplitudes are +/- 1/4.
    *   Squared: 1/16 = 0.0625 for ALL basis states.
    *   Therefore, the measurement outcome has equal probability for all 16 states.

3.  **Draft the Reasoning:**
    *   *Goal*: Create a 4-qubit complete graph state by applying H gates followed by CZ gates on all 6 edges, then measure.
    *   *State Evolution*:
        1.  Start with |0000>, apply H to all qubits -> |++++> = 1/4 Σ |x> (for all 4-bit strings x).
        2.  Apply CZ on all edges. The state becomes 1/4 Σ (-1)^(|x|(|x|-1)/2) |x>, because there are |x|(|

## isqTrain/151

- task_id: `isqTrain/151`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4285`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/3.0, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes one qubit `q[0]` in the |0> state, applies an Rx rotation gate with an angle of $\pi/3$, and then measures the qubit.
2. **State Evolution**: 
   - Initial state: $|0\rangle$
   - The $R_x(\pi/3)$ gate rotates the state around the X-axis of the Bloch sphere by $\pi/3$ radians, resulting in the state $\cos(\pi/6)|0\rangle - i\sin(\pi/6)|1\rangle$.
3. **Final State**: $|\psi\rangle = \frac{\sqrt{3}}{2}|0\rangle - \frac{i}{2}|1\rangle$
4. **Probabilities**: The probability of measuring the |0> state is the square of the amplitude: $|\frac{\sqrt{3}}{2}|^2 = 0.75$. The probability of measuring the |1> state is $|- \frac{i}{2}|^2 = 0.25$.

Predicted probability distribution: {|0>: 0.75, |1>: 0.25}

### Reference answer

{'predicted_probs': {'0': 0.7500000000000001, '1': 0.24999999999999994}, 'explanation': 'Parametric variant of isqHumanEval/51. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1377

- task_id: `isqTrain/1377`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3197`

### Prompt

Code this in isQ: Prepare the state |10>, apply a SWAP gate, and measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare the state |10>, swap the states of the two qubits, and measure them.
Qubits: 2 qubits are required, and both are measured.
Evolution:
1. Initialize the 2-qubit system to the ground state |00>.
2. Apply an X gate to q[0], flipping the first qubit to yield the state |10>.
3. Apply a swap operation (three-CNOT decomposition) to q[0] and q[1], exchanging their quantum states to yield |01>.
Probabilities: The final state of the system is deterministically |01>, so the measurement yields the bitstring '01' with a probability of 1.0.

## isqTrain/1450

- task_id: `isqTrain/1450`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3538`

### Prompt

Create an isQ quantum circuit that Prepare the computational basis state |1001> on 4 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare the 4-qubit state |1001> by applying X gates to the appropriate qubits.
Qubits: 4 qubits (q[0] to q[3]), all of which are measured.
Evolution:
- Initialize the 4-qubit system to the ground state |0000>.
- Apply an X gate to q[0] (the least significant bit), flipping it to |1> and evolving the state to |0001>.
- Apply an X gate to q[3] (the most significant bit), flipping it to |1> and evolving the state to |1001>.
Probabilities: The circuit deterministically prepares the basis state |1001>, so measurement yields the bitstring '1001' with a probability of 1.0.

## isqTrain/2582

- task_id: `isqTrain/2582`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `global_phase`, `isq_syntax_arrays`
- source: `isq_train_cot`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;

qbit q[3];

procedure main() {
    // Exact 3-qubit W state |001> + |010> + |100>
    q = [0.0, 0.5773502691896257, 0.5773502691896257, 0.0, 0.5773502691896257, 0.0, 0.0, 0.0];
    
    M(q[0]); M(q[1]); M(q[2]);
}

```

Program B:
```isq
import std;

qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Exact 3-qubit W state |001> + |010> + |100>
    q = [0.0, 0.5773502691896257, 0.5773502691896257, 0.0, 0.5773502691896257, 0.0, 0.0, 0.0];
    
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A**: Explicitly initializes the 3-qubit state to the array `[0.0, 0.577..., 0.577..., 0.0, 0.577..., 0.0, 0.0, 0.0]`, representing the exact W state $\frac{1}{\sqrt{3}}(|001\rangle + |010\rangle + |100\rangle)$, and measures all three qubits.
2. **Program B**: Applies a `GPhase(0.0)` gate, then identically initializes the 3-qubit state to the W state and measures all three qubits.
3. **Key difference**: Program B applies `GPhase(0.0)` before the state initialization.
4. **Probability comparison**: The `GPhase(0.0)` gate applies a trivial global phase factor of $e^{i \cdot 0} = 1$. Furthermore, explicitly setting the state array completely overrides any previous operations. Both programs produce the exact same quantum state prior to measurement, resulting in identical probability distributions (1/3 probability for 001, 010, and 100).
5. **Verdict**: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/149

- task_id: `isqTrain/149`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3547`

### Prompt

Write isQ code for the following quantum task: implements the state_preparation pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Prepare a quantum state via Rx rotation, then demonstrate gate cancellation with an H-H identity pair before measurement.

**Qubits**: 1 qubit q[0], measured at the end.

**State evolution**:
- |0⟩ → Rx(π/3) → cos(π/6)|0⟩ − i·sin(π/6)|1⟩ = (√3/2)|0⟩ − (i/2)|1⟩
- H gate: (1/√2)[(√3/2 − i/2)|0⟩ + (√3/2 + i/2)|1⟩]
- H gate again: H² = I, so state returns to (√3/2)|0⟩ − (i/2)|1⟩
- The H-H pair cancels, demonstrating gate cancellation awareness.

**Measurement probabilities**: P(|0⟩) = |√3/2|² = 0.75, P(|1⟩) = |−i/2|² = 0.25.

## isqTrain/3955

- task_id: `isqTrain/3955`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2488`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// Graph state for ring_3 topology
// Edges: [(0, 1), (1, 2), (0, 2)]
qbit q[3];

procedure main() {
    // Step 1: Hadamard on all qubits (|+>^n)
    H(q[0]);
    H(q[1]);
    H(q[2]);
    // Step 2: CZ for each edge
    CNOT(q[0], q[1]);  // edge (0,1)
    CZ(q[1], q[2]);  // edge (1,2)
    CZ(q[0], q[2]);  // edge (0,2)
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: Line 15 uses `CNOT(q[0], q[1])` instead of `CZ(q[0], q[1])` for edge (0,1). Graph state construction requires CZ gates for all edges, not CNOT.

2. **Fix**: Replace `CNOT(q[0], q[1])` with `CZ(q[0], q[1])`.

3. **State evolution**:
   - After Hadamards: |+⟩|+⟩|+⟩ = equal superposition of all 8 basis states
   - CZ(q[0], q[1]): applies Z to q[1] when q[0]=|1⟩, entangling qubits 0,1
   - CZ(q[1], q[2]): entangles qubits 1,2
   - CZ(q[0], q[2]): entangles qubits 0,2, completing the ring
   - The CZ gates introduce phase factors but preserve the equal-amplitude superposition across all computational basis states
   - Measurement yields uniform 0.125 probability for each of the 8 outcomes

## isqTrain/4770

- task_id: `isqTrain/4770`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `1713`

### Prompt

Help me write isQ code that implements: classical var variant 0. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a classical conditional circuit that applies an X gate if an integer is greater than 0.
2. **Qubits**: 1 global qubit (`q[0]`), which is measured.
3. **State Evolution**: The qubit `q[0]` starts in the initial state |0>. Because the classical variable `val = 1` evaluates `val > 0` to true, the `X` gate is applied, changing the state to |1>.
4. **Expected Probabilities**: The final state is exactly |1>, so measurement yields |1> with probability 1.0.

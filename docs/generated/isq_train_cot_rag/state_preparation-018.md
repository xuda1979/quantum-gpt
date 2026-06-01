# ISQ training COT RAG corpus: state_preparation shard 18

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/560

- task_id: `isqTrain/560`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1696`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[5];

procedure main() {
    X(q[1]);
    X(q[2]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State**: The circuit starts with 5 qubits, all initialized to the ground state: $|00000\rangle$.
2. **Operations**: 
   - `X(q[1])`: Applies a Pauli-X gate to qubit 1, flipping it from $|0\rangle$ to $|1\rangle$. The state becomes $|00010\rangle$.
   - `X(q[2])`: Applies a Pauli-X gate to qubit 2, flipping it from $|0\rangle$ to $|1\rangle$. The state becomes $|00110\rangle$.
3. **Final State**: The quantum state before measurement is exactly $|00110\rangle$.
4. **Measurement**: Measuring all qubits in the computational basis deterministically yields the classical bitstring `00110`.

Predicted probability distribution: {|00110>: 1.0}

### Reference answer

{'predicted_probs': {'6': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/179. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1463

- task_id: `isqTrain/1463`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5368`

### Prompt

Implement the following in isQ: Prepare the computational basis state |01001> on 5 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the 5-qubit computational basis state |01001⟩.
2. **Qubits:** 5 qubits (q[0]–q[4]), all measured.
3. **State evolution:**
   - Initialize all qubits: |00000⟩
   - Apply X(q[1]): flips q[1] → |01000⟩
   - Apply X(q[4]): flips q[4] → |01001⟩
4. **Measurement:** The final state is exactly |01001⟩, yielding measurement outcome `01001` with probability 1.0.

## isqTrain/4664

- task_id: `isqTrain/4664`
- task_type: `code_equivalence`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1584`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

**Program A** applies H to q[0], then CNOT(q[0], q[1]), then CNOT(q[1], q[2]), producing the GHZ state: |ψ⟩ = (|000⟩ + |111⟩)/√2. Measurement yields 50% |000⟩ and 50% |111⟩.

**Program B** applies the same first three gates, reaching the same GHZ state, but then applies H(q[0]) again. This transforms the state to:
|ψ⟩ = (|000⟩ + |100⟩ + |011⟩ − |111⟩)/2

yielding 25% each for |000⟩, |100⟩, |011⟩, and |111⟩.

**Key difference:** The extra H(q[0]) in Program B destroys the GHZ entanglement structure, producing a different superposition with four equally likely outcomes versus two.

**Verdict: Not equivalent**

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'000': 0.5, '111': 0.5}, 'probs_b': {'000': 0.25, '011': 0.25, '100': 0.25, '111': 0.25}}

## isqTrain/3973

- task_id: `isqTrain/3973`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4050`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// Entangled 2-qubit state via Ry(1.571) + CNOT
qbit q[2];

procedure main() {
    // Create entangled state
    Ry(1.571, q[0]);
    CNOT(q[1], q[0]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: In the CNOT gate call, the control and target qubits are swapped. `CNOT(q[1], q[0])` uses q[1] (always |0⟩) as control and q[0] as target, which produces no entanglement since q[1] never triggers the NOT.

2. **Fix**: Swap the arguments to `CNOT(q[0], q[1])`, making q[0] the control and q[1] the target.

3. **State evolution (corrected)**:
   - |00⟩ → Ry(1.571≈π/2, q[0]) → ≈(|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2
   - → CNOT(q[0], q[1]) → (|00⟩+|11⟩)/√2
   - Measurements yield ≈50% |00⟩ and ≈50% |11⟩, matching predicted output.

## isqTrain/3359

- task_id: `isqTrain/3359`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `109`

### Prompt

I need an isQ program to an isQ program: H(q[0]) then cascade CNOT through 5 qubits. This creates a cascading entanglement pattern.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a 5-qubit GHZ state using a Hadamard gate and a CNOT cascade.
Qubits: 5 qubits required, all measured.
1. Initial state: |00000>
2. H(q[0]): (|00000> + |10000>) / √2
3. CNOT(q[0], q[1]): (|00000> + |11000>) / √2
4. CNOT(q[1], q[2]): (|00000> + |11100>) / √2
5. CNOT(q[2], q[3]): (|00000> + |11110>) / √2
6. CNOT(q[3], q[4]): (|00000> + |11111>) / √2
Measurement probabilities are 0.5 for |00000> and 0.5 for |11111> due to equal superposition.

## isqTrain/4800

- task_id: `isqTrain/4800`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_if_else`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `770`

### Prompt

实现以下量子计算任务（使用isQ）：implements: for-loop with if-break at i=3. Declare a global qbit array q of 4 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply X gates to qubits q[0], q[1], q[2] via a for-loop that breaks at i=3, leaving q[3] untouched.

Four qubits are declared globally; all four are measured at the end.

State evolution (starting from |0000⟩):
- i=0: X(q[0]) flips qubit 0 → |1000⟩
- i=1: X(q[1]) flips qubit 1 → |1100⟩
- i=2: X(q[2]) flips qubit 2 → |1110⟩
- i=3: break condition met, loop exits without applying X(q[3])

Final state is |1110⟩, giving measurement probability {|1110⟩: 1.0} since all qubits are in definite computational basis states.

## isqTrain/3378

- task_id: `isqTrain/3378`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2525`

### Prompt

用isQ实现an isQ program: 3-layer circuit with H and CZ on 3 qubits. Each layer: H on all, then CZ between adjacent.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has 3 qubits, with 3 layers each consisting of H on all qubits followed by CZ between adjacent qubits.

Initial state: |000>

Layer 1:
- H on all 3 qubits: |000> → (1/√8)(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)
  This is actually |+++> = H⊗H⊗H|000>
- CZ(q[0], q[1]): applies phase -1 when both q[0] and q[1] are |1>
- CZ(q[1], q[2]): applies phase -1 when both q[1] and q[2] are |1>

Let me trace this more carefully.

After H on all: (1/√8) Σ_{x∈{0,1}^3} |x>

After CZ(q[0], q[1]): terms where q[0]=1 AND q[1]=1 get -1 phase. So |110> and |111> get -1.
State: (1/√8)(|000> + |001> + |010> + |011> + |100> + |101> - |110> - |111>)

After CZ(q[1], q[2]): terms where q[1]=1 AND q[2]=1 get -1 phase. So |011>, |111> get flipped sign.
State: (1/√8)(|000> + |001> + |010> - |011> + |100> + |101> - |110> + |111>)

Wait, |111> was already -1, so now it becomes +1.

Layer 2:
- H on all qubits again
- Then CZ(q[0], q[1]) and CZ(q[1], q[2])

Layer 3:
- H on all qubits again
- Then CZ(q[0], q[1]) and CZ(q[1], q[2])

This is getting complex to trace by hand. Let me think about it differently.

The pattern H...H followed by CZ on adjacent qubits creates a type of "cluster state" operation. 

Actually, Let me verify the output. The resulting probabilities should be uniform: 0.125 for all 8 states.

Let me check if the final state before measurement is indeed a uniform superposition or if the measurements give uniform probabilities.

If the final state is (1/√8) Σ|x>, then yes, all probabilities are 0.125.

But wait, after the last CZ gates, there should be some phases. However, H gates at the beginning of each layer might be converting those phases.

Actually, I need to think about this more carefully. The circuit is:
Layer 1: H⊗H⊗H, then CZ(0,1), CZ(1,2)
Layer 2: H⊗H⊗H, then CZ(0,1), CZ(1,2)  
Layer 3: H⊗H⊗H, then CZ(0,1), CZ(1,2)
Then measure all.

Actually wait - The circuit should the measurements happen after the 3rd layer of H gates, not after CZ gates. Let me re-read...

No, looking at the code:

So the structure is:
- H, H, H, CZ, CZ (layer 1)
- H, H, H, CZ, CZ (layer 2)
- H, H, H (layer 3, no CZ after)
- Measure all

Wait, that's not quite 3 layers of "H on all, then CZ between adjacent". Layer 3 has only H gates, no CZ after them. Let me re-read the problem statement.

"3-layer circuit with H and CZ on 3 qubits. Each layer: H on all, then CZ between adjacent."

But The circuit should:
Layer 1: H all, CZ adjacent
Layer 2: H all, CZ adjacent
Layer 3: H all (no CZ after)

Hmm, but looking at the predicted output, they're uniform at 0.125 each. Let me verify this makes sense.

If the final operation is just H⊗H⊗H (with no CZ after),

## isqTrain/4257

- task_id: `isqTrain/4257`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4775`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

qbit q[1];

procedure main() {
    // |+> state
    H(q[0]);
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); // prob 0.5, 0.5
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit `q[0]` in the |0> state and applies an initial H gate followed by the sequence H, Z, H.
2. Initial state: |0>.
3. After the first `H(q[0])` gate, the state evolves to |+> = (1/sqrt(2))|0> + (1/sqrt(2))|1>.
4. The subsequent sequence `H(q[0]); Z(q[0]); H(q[0])` is mathematically equivalent to the Pauli-X gate (HZH = X).
5. Applying the X gate to the |+> state leaves it unchanged, as |+> is an eigenstate of X with eigenvalue +1.
6. The final state before measurement is |+> = (1/sqrt(2))|0> + (1/sqrt(2))|1>.
7. Measuring in the computational basis gives an equal probability for both classical outcomes.

Predicted probability distribution: {|0>: 0.5, |1>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.5000, P(|1>) = 0.5000.'}

## isqTrain/1431

- task_id: `isqTrain/1431`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3110`

### Prompt

Write an isQ program that Prepare the state W-like state |01>+|10> and measure all qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to prepare the 2-qubit W-like entangled state |01> + |10> and measure both qubits.
Starting from |00>, apply H(q[0]) to create the superposition (|00> + |10>)/√2.
Applying CNOT(q[0], q[1]) entangles the qubits, flipping the target to form a Bell state (|00> + |11>)/√2.
Applying X(q[0]) flips the first qubit, transforming the state into (|10> + |01>)/√2.
Measuring both qubits collapses the superposition, yielding an equal 50% probability for both |01> and |10>.

## isqTrain/3218

- task_id: `isqTrain/3218`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4001`

### Prompt

Code this in isQ: an isQ program: apply Rx(1*pi/4) then Ry(1*pi/2) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply Rx(π/4) then Ry(π/2) to a single qubit starting in |0⟩, then measure.

**Qubits:** 1 qubit, measured at the end.

**State evolution:**
1. Start: |0⟩
2. After Rx(

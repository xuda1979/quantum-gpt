# ISQ training COT RAG corpus: state_preparation shard 26

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/573

- task_id: `isqTrain/573`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3938`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[5];

procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[4]);
    M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 5 qubits to |00000>, then applies X gates to q[0], q[1], and q[4].
2. X(q[0]) flips qubit 0: |00000> → |00001>.
3. X(q[1]) flips qubit 1: |00001> → |00011>.
4. X(q[4]) flips qubit 4: |00011> → |10011>.
5. The final state before measurement is |10011>.
6. Measurement yields this basis state with certainty.

Predicted probability distribution: {|10011>: 1.0}

### Reference answer

{'predicted_probs': {'19': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/192. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3199

- task_id: `isqTrain/3199`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4585`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: apply Ry(1*pi/16) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a Y-rotation of π/16 to a single qubit and measure the resulting state.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Initialize: |ψ⟩ = |0⟩
   - Apply Ry(π/16): |ψ⟩ = cos(π/32)|0⟩ + sin(π/32)|1⟩
4. **Probabilities**: P(|0⟩) = cos²(π/32) ≈ 0.9904, P(|1⟩) = sin²(π/32) ≈ 0.0096, following from Born's rule on the final state amplitudes.

## isqTrain/1437

- task_id: `isqTrain/1437`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1302`

### Prompt

I need an isQ program to Put 5 qubits in |+> state, then create a CZ entanglement chain (CZ between consecutive pairs). Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize a 5-qubit graph state with a linear entanglement topology via an H-and-CZ chain, then measure all qubits.
2. **Qubits**: 5 qubits are required (`q[5]`), and all are measured, yielding a 5-bit string.
3. **State Evolution**:
   - Start in the ground state: $|00000\rangle$.
   - Apply H to all qubits to create a uniform superposition: $|+\rangle^{\otimes 5} = \frac{1}{\sqrt{32}} \sum_{x=0}^{31} |x\rangle$.
   - Apply CZ between consecutive pairs (q[0]-q[1], q[1]-q[2], q[2]-q[3], q[3]-q[4]).
   - Each CZ gate introduces a relative phase of $-1$ to the components where both interacting qubits are in the $|1\rangle$ state.
4. **Probabilities**: The CZ gates only alter the phases of the basis states, leaving their magnitudes unchanged at $1/\sqrt{32}$. Thus, the probability of each of the 32 possible measurement outcomes is exactly $0.03125$.

## isqTrain/3220

- task_id: `isqTrain/3220`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1600`

### Prompt

Write an isQ program that an isQ program: apply Rx(1*pi/3) then Ry(1*pi/3) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply sequential Rx(π/3) and Ry(π/3) rotations to a single qubit and measure.
One qubit needed (q[0]), which is measured.

State evolution:
- |ψ₀⟩ = |0⟩
- After Rx(π/3): |ψ₁⟩ = cos(π/6)|0⟩ - i·sin(π/6)|1⟩ = (√3/2)|0⟩ - i(1/2)|1⟩
- After Ry(π/3): |ψ₂⟩ = [(3+i)/4]|0⟩ + [√3(1-i)/4]|1⟩

Probabilities: P(|0⟩) = |(3+i)/4|² = 10/16 = 0.625, P(|1⟩) = |√3(1-i)/4|² = 6/16 = 0.375

## isqTrain/1368

- task_id: `isqTrain/1368`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2056`

### Prompt

Write an isQ program that Prepare a GHZ state on 5 qubits: (|00000> + |11111>) / sqrt(2). Measure all qubits.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a "Reasoning" section for an isQ quantum program that prepares a 5-qubit GHZ state and measures all qubits.
    *   Input: The prompt, circuit implementation, expected probabilities, and isQ syntax.
    *   Output constraints: ONLY the reasoning section, starting with "## Reasoning". No code blocks. Concise (3-15 lines). Use Dirac notation.

2.  **Deconstruct the Circuit (5-qubit GHZ state):**
    *   *Goal:* Create a 5-qubit GHZ state $(|00000\rangle + |11111\rangle)/\sqrt{2}$.
    *   *Initial state:* $|00000\rangle$
    *   *Step 1:* Apply Hadamard ($H$) to $q_0$. State becomes $(|0\rangle + |1\rangle)/\sqrt{2} \otimes |0000\rangle = (|00000\rangle + |10000\rangle)/\sqrt{2}$.
    *   *Step 2:* Apply CNOT($q_0$, $q_1$). State becomes $(|00000\rangle + |11000\rangle)/\sqrt{2}$.
    *   *Step 3:* Apply CNOT($q_0$, $q_2$). State becomes $(|00000\rangle + |11100\rangle)/\sqrt{2}$.
    *   *Step 4:* Apply CNOT($q_0$, $q_3$). State becomes $(|00000\rangle + |11110\rangle)/\sqrt{2}$.
    *   *Step 5:* Apply CNOT($q_0$, $q_4$). State becomes $(|00000\rangle + |11111\rangle)/\sqrt{2}$.
    *   *Step 6:* Measure all 5 qubits.
    *   *Probabilities:* The final state is an equal superposition of $|00000\rangle$ and $|11111\rangle$. Measurement yields $|00000\rangle$ with 50% probability and $|11111\rangle$ with 50% probability.

3.  **Draft the Reasoning Section (incorporating rules):**
    *   *Rule 1:* Start with "## Reasoning"
    *   *Rule 2 & 3:* One line goal, qubits, state evolution.
    *   *Rule 4:* Why probabilities follow.

    *Drafting:*
    ## Reasoning
    The goal is to prepare a 5-qubit GHZ state, $(|00000\rangle + |11111\rangle)/\sqrt{2}$, and measure all qubits.
    We need 5 qubits, and all 5 are measured at the end.
    1. Start with initial state $|00000\rangle$.
    2. Apply $H$ to $q_0$, putting it in superposition: $(|00000\rangle + |10000\rangle)/\sqrt{2}$.
    3. Apply CNOTs from $q_0$ to $q_1, q_2, q_3$, and $q_4$ sequentially.
    4. Each CNOT entangles the target qubit with the control, copying the $|0\rangle$ or $|1\rangle$ state to produce $(|00000\rangle + |11111\rangle)/\sqrt{2}$.
    Because the final state is an equally weighted superposition of exactly two basis states, measurement yields $|00000\rangle$ with probability 0.5 and $|11111\rangle$ with probability 0.5.

4.  **Review against constraints:**
    *   Starts with "## Reasoning"? Yes.
    *   No isQ code? Yes.
    *   Concise? Yes, 7 lines.
    *   Dirac notation used correctly? Yes.
    *   Explains goal, qubits, evolution, probabilities? Yes.

5.  **Final Polish:** Keep it crisp.
    "## Reasoning
    The goal is to prepare a 5-qubit GHZ state $(|00000\rangle + |11111\rangle)/\sqrt{2}$ and measure all qubits. We require 5 qubits, and all 5 are measured.
    - Initial state is $|00000\rangle$.
    - $H(q[0])$ creates a superposition: $(|00000\rangle + |10000\rangle)/\sqrt{2}$.
    - Sequential CNOTs from $q[0]$ to $q[1]$ through $q[4]$ propagate the entanglement.
    - After CNOT($q

## isqTrain/3844

- task_id: `isqTrain/3844`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2007`

### Prompt

Write an isQ program that Prepare the graph state for a star 5 graph with 5 nodes and edges [(0, 1), (0, 2), (0, 3), (0, 4)]. Apply Hadamard to all qubits, then CZ for each edge. Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Prepare and measure the graph state for a star-5 graph (qubit 0 connected to qubits 1-4).

**Qubits:** 5 qubits (q[0]–q[4]), all measured.

**State evolution:**
1. Initial: |00000⟩
2. After H on all: |+++++⟩ = (1/√32) Σ_{x∈{0,1}⁵} |x⟩ (uniform superposition)
3. CZ(q[0],q[1]) applies phase -1 when both are |1⟩, i.e., multiplies |x⟩ by (-1)^{x₀x₁}
4. Sequential CZ on edges (0,2), (0,3), (0,4) accumulates phase (-1)^{x₀(x₁+x₂+x₃+x₄)}
5. Final state: |G⟩ = (1/√32) Σ_x (-1)^{x₀·Σᵢxᵢ} |x⟩

**Measurement probabilities:** All 32 amplitudes have equal magnitude 1/√32, so each computational basis state has probability 1/32 = 0.03125, regardless of the phase structure.

## isqTrain/4788

- task_id: `isqTrain/4788`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`, `isq_syntax_while_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `3236`

### Prompt

Write isQ code for the following quantum task: implements: while-loop counter variant 4. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a while-loop counter pattern with a Hadamard gate on a single qubit, then measure.
2. One qubit (q[0]) is used and measured.
3. Initial state: |0⟩. After H(q[0]): |+⟩ = (1/√2)(|0⟩ + |1⟩). Measurement collapses to |0⟩ or |1⟩. The while-loop only increments a classical counter (count 0→5) and doesn't affect the quantum state.
4. Expected probabilities: P(|0⟩) = 0.5, P(|1⟩) = 0.5, since |+⟩ has equal amplitude for both computational basis states.

## isqTrain/569

- task_id: `isqTrain/569`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5676`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[5];

procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    M(q);
}
```

### Chain-of-thought reasoning

- The circuit applies four X gates to qubits q[0], q[1], q[2], and q[3].
- The initial state of the 5 qubits is |00000>.
- X(q[0]) flips q[0] to |1>, making the state |00001>.
- X(q[1]) flips q[1] to |1>, making the state |00011>.
- X(q[2]) flips q[2] to |1>, making the state |00111>.
- X(q[3]) flips q[3] to |1>, making the state |01111>.
- Qubit q[4] is left in the |0> state.
- The final state before measurement is |01111>.
- Measurement of all qubits will yield the bitstring 01111 with a probability of 1.0.
- The output format specifies "earlier measured qubit = higher bit", so M(q) measures q[0] as the highest bit, down to q[4] as the lowest bit. The state |q[3]q[2]q[1]q[0]q[4]> -> Wait, if earlier measured qubit = higher bit, M(q) measures q[0] to q[4]. So q[0] is the highest bit.
Wait, "earlier measured qubit = higher bit".
q[0] is the highest bit (bit 4), q[4] is the lowest bit (bit 0).
So q[3]=1, q[2]=1, q[1]=1, q[0]=1, q[4]=0.
Bitstring is q[0]q[1]q[2]q[3]q[4] = 11110?
Wait, let's re-read the prompt: "Expected measurement probabilities: {|01111>: 1.0}"
Ah, in the prompt's circuit implementation: "Expected measurement probabilities: {|01111>: 1.0}"
But wait! If q[0]=1, q[1]=1, q[2]=1, q[3]=1, q[4]=0.
If q[0] is the highest bit (bit 4), the bitstring is 11110.
Why does The implementation say |01111>?
Let me check the index order.
Maybe q[4] is the highest bit? No, "earlier measured qubit = higher bit".
If M(q) measures q[0] first, q[0] is the highest bit.
Wait, if it's |01111>, then q[4] (measured last) is 0, and it's the highest bit?
No, wait. If M(q) measures from q[0] to q[4], maybe "earlier measured qubit" means smaller index is higher bit?
Wait, if it's |01111>, the first character is 0. That means the highest bit is 0. The highest bit is q[0] (measured first).
So q[0] must be 0!
But the code applies X(q[0]), X(q[1]), X(q[2]), X(q[3]).
This makes q[0]=1, q[1]=1, q[2]=1, q[3]=1, q[4]=0.
If q[0] is the highest bit, the bitstring should be 11110.
Why does the reference say {|01111>: 1.0}?
Could it be that "earlier measured qubit = higher bit" means q[4] is higher bit?
Wait, the prompt says: "Expected measurement probabilities: {|01111>: 1.0}".
Wait, maybe q[0] is the LOWEST bit?
"earlier measured qubit = higher bit".
If earlier measured qubit is higher bit, and M(q) measures q[0], then q[1], etc.
So q[0] is bit 4, q[1] is bit 3, q[2] is bit 2, q[3] is bit 1, q[4] is bit 0.
So bitstring is 11110.
But the reference says {|01111>: 1.0}. Wait, maybe my reference is flipped?
Let's check the reference again. "Expected measurement probabilities: {|01111>: 1.0}".
Wait, in isQ, does M(q) measure from highest index to lowest?
Let's think. If M(q) returns an integer, and it's 01111 (which is 15).
If q[0]=1, q[1]=1, q[2]=1, q[3]=1, q[4]=0.
If it's 15, then q[0]

### Reference answer

{'predicted_probs': {'15': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/188. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4810

- task_id: `isqTrain/4810`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_switch`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `711`

### Prompt

帮我写一个isQ程序：uses switch on a computed classical value. Declare 2 global qubits. Create int a=1 and int b=0. Compute int c = a + b. Use switch(c): case 0 applies H(q[0]) and H(q[1]), case 1 applies X(q[0]), case 2 applies X(q[0]) and X(q[1]). Since c=1, case 1 executes (and falls through to case 2). X(q[0]) from case 1, then X(q[0]) and X(q[1]) from case 2. q[0] gets X twice (back to |0>), q[1] gets X once (|1>). Measure both. Expected: |01>.

### Chain-of-thought reasoning

## Reasoning

This circuit uses a classical switch statement on a computed value (c=1) to conditionally apply quantum gates, with fall-through behavior.

Two global qubits q[0], q[1] are declared; both are measured.

**State evolution:**
- Initial state: |00⟩
- c = a + b = 1 + 0 = 1, so switch enters case 1
- case 1: X(q[0]) → |10⟩
- case 2 (fall-through): X(q[0]) and X(q[1]) → X(q[0]) flips q[0]

## isqTrain/3742

- task_id: `isqTrain/3742`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5630`

### Prompt

I need an isQ program to Prepare a 2-qubit product state by applying Ry(1.5) to q[0] and Ry(0.0) to q[1]. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare a 2-qubit product state via independent Ry rotations on each qubit.
2. Two qubits q[0] and q[1] are allocated; both are measured.
3. Initial state: |00⟩.
4. Ry(1.5) on q[0]: cos(0.75)|0⟩ + sin(0.75)|1⟩; Ry(0.0) on q[1] leaves it as |0⟩.
5. Final state: cos(0.75)|00⟩ + sin(0.75)|10⟩ ≈ 0.7317|00⟩ + 0.6816|10⟩.
6. Probabilities: P(|00⟩)=cos²(0.75)≈0.5354, P(|10⟩)=sin²(0.75)≈0.4646.

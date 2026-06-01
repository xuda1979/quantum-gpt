# ISQ training COT RAG corpus: quantum_algorithms shard 15

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3717

- task_id: `isqTrain/3717`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `293`

### Prompt

Implement a quantum circuit in isQ: QAOA (p=1) for the MaxCut problem on a 3-node path graph with edges [(0, 1), (1, 2)]. Use parameters gamma=0.785 and beta=0.393. The circuit:
1. Initialize all qubits in superposition
2. Apply cost unitary: for each edge, use CNOT-Rz-CNOT
3. Apply mixer: Rx(2*beta) on each qubit
4. Measure all 3 qubits

### Chain-of-thought reasoning

The user wants me to explain a QAOA p=1 circuit for MaxCut on a 3-node path graph.
1. Goal: Implement QAOA p=1 for MaxCut on a 3-node path graph.
2. Qubits: 3 qubits, all measured.
3. Evolution:
   - Initial state: |000>
   - Hadamards: (|0>+|1>)^3 / sqrt(8) = 1/sqrt(8) sum_z |z>
   - Cost unitary U_C: applies phase exp(-i*gamma*(Z_i Z_j)) for each edge (0,1) and (1,2).
     - Edge (0,1) CNOT-Rz(2*0.785)-CNOT applies exp(-i*0.785 Z_0 Z_1).
     - Edge (1,2) CNOT-Rz(2*0.785)-CNOT applies exp(-i*0.785 Z_1 Z_2).
     - Overall phase for state |z_0 z_1 z_2> is exp(-i*0.785*(Z_0 Z_1 + Z_1 Z_2)).
   - Mixer U_M: applies Rx(2*0.393) to all qubits, equivalent to exp(-i*0.393 X).
   - Final state is a superposition.
4. Probabilities: The resulting probabilities should be derived from the QAOA state preparation, weighting cut states (like |000> and |111>) higher than uncut states (like |010> and |101>). Let's briefly trace the weights.
   - For cut states (e.g., |101>, or |010> in a 3-node path, wait, |101> has edges (0,1)=cut, (1,2)=cut -> 2 cuts. |010> has edges (0,1)=cut, (1,2)=cut -> 2 cuts. Wait, |010> means 0->0, 1->1, 2->0. Edges (0,1) is cut. Edge (1,2) is cut. So |010> and |101> are max cuts.
   - |000>, |011> (0->0,1->1,2->1), edge (0,1) cut, edge (1,2) not cut -> 1 cut.
   - Wait, the reference output gives |000> and |111> probability ~0.31, and |010> and |101> ~0.062.
   - Let's check the Cost Hamiltonian: C = 0.5*(I-Z_0 Z_1) + 0.5*(I-Z_1 Z_2).
   - U_C = exp(-i * gamma * C). So U_C adds phase exp(-i*gamma*0.5*(I-Z_0 Z_1 + I-Z_1 Z_2)) = exp(-i*gamma) exp(i*0.5*gamma*(Z_0 Z_1 + Z_1 Z_2)).
   - Wait, the reference code does CNOT, Rz(2*0.785), CNOT. This applies exp(-i*0.785*Z_0 Z_1). This corresponds to U_C = exp(-i*gamma * Z_0 Z_1).
   - If U_C = exp(-i*gamma * Z_0 Z_1 - i*gamma * Z_1 Z_2), then for state |000> or |111>, Z_0 Z_1 = 1, Z_1 Z_2 = 1, phase is exp(-2*i*gamma).
   - For |010> or |101>, Z_0 Z_1 = -1, Z_1 Z_2 = -1, phase is exp(2*i*gamma).
   - For |011> or |100>, Z_0 Z_1 = -1, Z_1 Z_2 = 1, phase is 1.
   - For |001> or |110>, Z_0 Z_1 = 1, Z_1 Z_2 = -1, phase is 1.
   - Since the problem is MaxCut, we want to maximize edges cut. But this Hamiltonian Z_0 Z_1 + Z_1 Z_2 is actually *minimized* for |010> and |101> (gives -2) and *maximized* for |000> and |111> (gives +2).
   - So this QAOA is finding the *minimum* of Z_0 Z_1 + Z_1 Z_2. Thus it amplifies |000> and |111>. (Which makes sense, if it's finding

## isqTrain/4326

- task_id: `isqTrain/4326`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1126`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

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
    X(q[0]); // flip qubit 0 before measurement
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of an isQ quantum program that predicts the probability distribution of measurement outcomes. The analysis should be step-by-step, use Dirac notation, and follow the specific formatting rules (start with "## Circuit Analysis", no code blocks, end with predicted probabilities). Constraint: 3-8 lines for simple, up to 15 for complex.

2.  **Analyze the isQ Code:**
    *   `qbit q[4];` -> Initial state: $|0000\rangle$ (q[3], q[2], q[1], q[0])
    *   `H(q[0]);` -> Apply Hadamard to q[0]. State: $\frac{1}{\sqrt{2}}(|0000\rangle + |0001\rangle)$
    *   `X(q[1]);` -> Apply X to q[1]. State: $\frac{1}{\sqrt{2}}(|0010\rangle + |0011\rangle)$
        *   Let's trace inputs: $a = q[0]$, $b = q[1]$. So $(a,b) \in \{(0,1), (1,1)\}$.
    *   `CNOT(q[0], q[2]);` -> Sum step 1: $q[2] = q[2] \oplus q[0]$.
    *   `CNOT(q[1], q[2]);` -> Sum step 2: $q[2] = q[2] \oplus q[1]$.
        *   Total $q[2] = 0 \oplus a \oplus b = a \oplus b$.
    *   `Toffoli(q[0], q[1], q[3]);` -> Carry step: $q[3] = q[3] \oplus (a \cdot b) = a \cdot b$.
    *   *State before X(q[0])*:
        *   If $(a,b) = (0,1)$, $q[2] = 1, q[3] = 0$. State: $|q[3]q[2]q[1]q[0]\rangle = |0110\rangle$.
        *   If $(a,b) = (1,1)$, $q[2] = 0, q[3] = 1$. State: $|q[3]q[2]q[1]q[0]\rangle = |1011\rangle$.
        *   Superposition: $\frac{1}{\sqrt{2}}(|0110\rangle + |1011\rangle)$
    *   `X(q[0]);` -> Flips q[0].
        *   $|0110\rangle \rightarrow |0111\rangle$
        *   $|1011\rangle \rightarrow |1010\rangle$
    *   Final State: $\frac{1}{\sqrt{2}}(|0111\rangle + |1010\rangle)$

3.  **Refine Output Format:**
    *   Line 1: Initial state and H/X setup.
    *   Line 2: CNOT/Toffoli logic (half adder).
    *   Line 3: Final X gate flip.
    *   Line 4: Measurement probability conclusion.
    *   Let's trace the exact bitstring to match standard notation (q[3] is MSB, q[0] is LSB).
    *   $|0111\rangle$ is decimal 7. $|1010\rangle$ is decimal 10.

4.  **Drafting the response:**
    ## Circuit Analysis
    - Initial state is |0000>. H(q[0]) puts q[0] in superposition, and X(q[1]) sets q[1] to |1>, resulting in (|0010> + |0011>)/√2. Let q[0]=a, q[1]=b.
    - CNOT(q[0], q[2]) and CNOT(q[1], q[2]) compute the sum q[2] = a ⊕ b. Toffoli(q[0], q[1], q[3]) computes the carry q[3] = a ∧ b.
    - For (a,b) = (0,1), sum=1, carry=0 -> |0110>. For (a,b) = (1,1), sum=0, carry=1 -> |1011>. State is (|0110> + |1011>)/√2.
    - The final X(q[0]) flips the input qubit q[0] in both

### Reference answer

{'predicted_probs': {'0001': 0.5, '0010': 0.5}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0001>) = 0.5000, P(|0010>) = 0.5000.'}

## isqTrain/3810

- task_id: `isqTrain/3810`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `729`

### Prompt

Create an isQ quantum circuit that the swap test to compare states |+> vs |+>. Use:
1. q[0] as ancilla, q[1] for state A, q[2] for state B
2. A controlled-SWAP (Fredkin) gate via CNOT+Toffoli
3. Hadamard on ancilla before and after CSWAP
4. Measure all 3 qubits. P(ancilla=0) = (1+|<A|B>|²)/2.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Code generation (isQ) for a swap test comparing $|+\rangle$ vs $|+\rangle$.
    *   Structure: Need to implement a `cswap` unit (controlled-swap operation (three-CNOT decomposition) using CNOT + Toffoli), prepare $|+\rangle$ on q[1] and q[2], apply H on q[0] (ancilla), Cswap (three-CNOT decomposition), H on q[0], and measure all qubits.
    *   Output constraint: ONLY the reasoning section, starting with "## Reasoning". No isQ code.
    *   Reasoning contents: Goal, qubits/measured, step-by-step state evolution (Dirac notation), explanation of expected probabilities.
    *   Length: 3-15 lines.

2.  **Draft the Reasoning Steps:**
    *   *Goal:* Implement the swap test circuit to compare two identical states $|+\rangle$ and $|+\rangle$ using an ancilla qubit.
    *   *Qubits:* 3 qubits (q[0] ancilla, q[1] state A, q[2] state B). All 3 are measured.
    *   *State evolution:*
        *   Initial: $|000\rangle$
        *   State prep (H on q1, q2): $|0\rangle_{anc} \otimes |+\rangle_A \otimes |+\rangle_B = \frac{1}{2}|0\rangle(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        *   First H on anc: $\frac{1}{2}(|0\rangle + |1\rangle)(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        *   Cswap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)): swaps q1 and q2 if anc is $|1\rangle$. Since $|01\rangle$ and $|10\rangle$ swap, the state is $\frac{1}{2}|0\rangle(|00\rangle + |01\rangle + |10\rangle + |11\rangle) + \frac{1}{2}|1\rangle(|00\rangle + |10\rangle + |01\rangle + |11\rangle)$. The state is unchanged because $|+\rangle|+\rangle$ is symmetric under swap.
        *   Second H on anc: Transforms $|0\rangle \to |+\rangle$ and $|1\rangle \to |-\rangle$. The ancilla state becomes $\frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) \otimes |+\rangle|+\rangle$, dropping a global phase. Thus, the ancilla is completely unentangled and in state $|0\rangle$ (with probability 1) before measurement if measured in Z-basis. Wait, H on $|+\rangle$ gives $|0\rangle$.
    *   *Probabilities:* The final state is $|0\rangle \otimes |+\rangle \otimes |+\rangle$. Measuring in Z-basis gives P(ancilla=0) = 1. The remaining qubits are in $|+\rangle$, so q[1] and q[2] each have 0.5 probability of being 0 or 1. Overall probabilities are 0.25 for |000>, |001>, |010>, |011>.

3.  **Refine and Format:**
    *   Check line count: 6-7 lines.
    *   Check constraints: Starts with "## Reasoning", no code block.
    *   Dirac notation check: $|0\rangle$, $|+\rangle$, etc.

    *Drafting the text:*
    ## Reasoning
    The goal is to perform a swap test to compare two identical quantum states, $|+\rangle$ and $|+\rangle$, to demonstrate that their overlap is 1.
    The circuit uses 3 qubits: q[0] as the ancilla, q[1] for state A, and q[2] for state B, and all 3 are measured.
    Initial state $|000\rangle$ evolves to $|0\rangle \otimes |+\rangle \otimes |+\rangle$ after preparing states A and B with Hadamard gates.
    Applying the first Hadamard to the ancilla gives $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |+\rangle \otimes |+\rangle$.
    The controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) gate swaps q[1] and q[2] when the ancilla is $|1\rangle$, but since $|+\rangle \otimes |+\rangle$ is

## isqTrain/3468

- task_id: `isqTrain/3468`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5803`

### Prompt

Help me write isQ code that the Fredkin gate and verify that when the control qubit is |0>, no swap occurs.

Test: q[0]=|0>, q[1]=|1>, q[2]=|0>. Expected: |010> (no swap).

Declare 3 qubits, measure all.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) gate and verify that when control qubit q[0]=|0>, no swap occurs between q[1] and q[2].
2. Three qubits q[0], q[1], q[2] are used and all are measured.
3. State evolution:
   - Initialize |000⟩, apply X(q[1]) → |010⟩.
   - CNOT(q[2], q[1]): control q[2]=|0⟩, no flip → |010⟩.
   - Toffoli (ctrl ctrl X) on (q[0], q[1], q[2]): controls q[0]=|0⟩ and q[1]=|1⟩; since q[0]=|0⟩, Toffoli doesn't fire → |010⟩.
   - CNOT(q[2], q[1]): control q[2]=|0⟩, no flip → |010⟩.
4. Final state is |010⟩ with probability 1.0, confirming no swap occurred because the control qubit was |0⟩.

## isqTrain/980

- task_id: `isqTrain/980`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5034`

### Prompt

Implement the following in isQ: implements a variant of the suzuki_trotter pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user is asking for a reasoning section, not code.
The goal is to implement a Suzuki-Trotter pattern variant between q[2] and q[3] of an expanded register (4 qubits total).
Wait, The circuit should q[0] and q[1] for the ZZ and XX interactions, and has a 3-qubit register. The resulting probabilities should be for |010> and |100>, with 3 measured qubits.
Let me carefully read the prompt and circuit implementation.
The prompt says: "Write an isQ program that implements a variant of the suzuki_trotter pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version."
Wait, The circuit should `q[2]` -> wait, no. The implementation says:

But it has a 3-qubit register and measures all three: `M(q[0]); M(q[1]); M(q[2]);`
Wait, if the prompt asks for "q[2] -> q[3]", and 4 qubits (an expanded register), The implementation provided in the prompt doesn't match the prompt description?
Wait! In code generation tasks, The implementation provided in the prompt description often is just a template or it's a mismatched example. But wait, the Expected measurement probabilities are `{|010>: 0.14644660940672613, |100>: 0.8535533905932738}`.
In `--probs` mode, the bitstring is formed by the order of measurement. "earlier measured qubit = higher bit".
If `M(q[0])`, `M(q[1])`, `M(q[2])` are measured, the bitstring is `q[0] q[1] q[2]`.
Expected: |010> (q[0]=0, q[1]=1, q[2]=0) and |100> (q[0]=1, q[1]=0, q[2]=0).
Wait, The implementation says:

So q[2] is never touched, stays |0>. So the bit ends with 0.
Wait, what if the prompt says "using q[2] -> q[3]" but the reference uses `q[0] -> q[1]`? I must match the *circuit implementation* exactly if it's provided, but the prompt instructions are a bit confusing.
Wait, the instruction says: "Generate a reasoning section that explains: ... Do NOT include the isQ code".
Let's trace The implementation to be safe, or trace a generic Suzuki-Trotter.
circuit implementation state evolution:
Initial: |000>
X(q[0]) -> |100>
ZZ(t/2):
CNOT(0, 1) -> |100>
Rz(0.3927, 1) -> e^{-i 0.196} |100>
CNOT(0, 1) -> e^{-i 0.196} |100>
XX(t):
H(0), H(1) -> e^{-i 0.196} (|00> + |10>) / sqrt(2) = e^{-i 0.196} (|0> + |1>)/sqrt(2) |0> + ... wait.
|100> -> H(0)H(1) -> |->|+>|0> ? No, H(0)|1> = |->, H(1)|0> = |+>.
So |->|+> = 1/2 (|0>-|1>)(|0>+|1>) = 1/2 (|00>+|01>-|10>-|11>).
CNOT(0,1) on this:
|00> -> |00>
|01> -> |01>
|10> -> |11>
|11> -> |10>
State: 1/2 (|00> + |01> - |11> - |10>) = 1/2 (|00> - |10> + |01> - |11>).
Apply Rz(0.7854) on q[1]:
For |00> and |10> (where q[1]=0): no phase.
For |01> and |11> (where q[1]=1): multiply by e^{-i 0.7854/2} = e^{-i

## isqTrain/1280

- task_id: `isqTrain/1280`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `655`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the qaoa pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants me to generate a QAOA variant using q[3] -> q[4] with an expanded qubit register. Let me analyze The implementation and understand what's happening.

The implementation is a QAOA p=1 for MaxCut on a triangle (K3) graph with 4 qubits but only 3 are actively used.

The expected measurement probabilities show:
- |0000>: 0.031
- |0010>: 0.156
- |0100>: 0.156
- |0110>: 0.156
- |1000>: 0.156
- |1010>: 0.156
- |1100>: 0.156
- |1110>: 0.031

Wait, these probabilities suggest that q[3] (the 4th qubit, represented by the highest bit position) is always 0, and q[2] (the 3rd qubit) varies. Actually, let me re-read the bit ordering.

In --probs mode, "earlier measured qubit = higher bit", so:
- M(q[0]) is the highest bit
- M(q[1]) is next
- M(q[2]) is next
- M(q[3]) is the lowest bit

So |0010> means q[0]=0, q[1]=0, q[2]=1, q[3]=0.

Looking at the probabilities:
- q[3] is always 0 (since all states have 0 in the lowest bit)
- q[2] is 0 when q[0]=q[1] (for |0000> and |1100>)

Wait, let me reconsider. The states present are:
- |0000>: q[0]=0, q[1]=0, q[2]=0, q[3]=0
- |0010>: q[0]=0, q[1]=0, q[2]=1, q[3]=0
- |0100>: q[0]=0, q[1]=1, q[2]=0, q[3]=0
- |0110>: q[0]=0, q[1]=1, q[2]=1, q[3]=0
- |1000>: q[0]=1, q[1]=0, q[2]=0, q[3]=0
- |1010>: q[0]=1, q[1]=0, q[2]=1, q[3]=0
- |1100>: q[0]=1, q[1]=1, q[2]=0, q[3]=0
- |1110>: q[0]=1, q[1]=1, q[2]=1, q[3]=0

So q[3] is always 0 (never touched by any gates).

The circuit uses H gates on q[0], q[1], q[2] to create superposition, then applies ZZ interactions for edges of the triangle, then applies Rx mixer.

Now I need to write a variant that uses q[3] -> q[4], meaning it should use q[3] and q[4] somehow, and have an expanded register.

Actually, looking more carefully at the task, it says "implements a variant of the qaoa pattern using q[3] -> q[4]". This might mean the variant uses qubits q[3] and q[4] instead of or in addition to the original qubits.

Let me create a variant that:
1. Uses a 5-qubit register (expanded from 4)
2. Actively uses q[3] and q[4] in the QAOA circuit
3. Follows a similar QAOA pattern

For the reasoning section, I need to explain the circuit's goal, qubits used, step-by-step state evolution, and why expected probabilities follow.

Since the user wants ONLY the reasoning section and no code, I'll focus on explaining the logic.

Let me write the reasoning:

## Reasoning
Goal: Implement a QAOA p=1 variant for MaxCut with expanded qubit register using q[3] and q[4].

Qubits: 5 qubits (q[0]-q[4]), with q[3] and q[4] added to expand the base triangle graph, measuring all 5 qubits.

State evolution:
1. |00000> → H(q[0]), H(q[1]), H(q[2]), H(q[3]) → |+++0> = (1/4)∑|x1 x2 x3 x4 0>
2. Cost layer on edges including (3,4): CNOT(q[3],q[4]) → Rz(γ

## isqTrain/3047

- task_id: `isqTrain/3047`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `measurement_order`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `2372`

### Prompt

I need an isQ program to creates a Bell pair, measures the first qubit, and conditionally applies X to the second qubit based on the measurement result. This should reset the second qubit to |0>.

Requirements:
- Declare `qbit q[2];` and `bool flag;` at global scope.
- Use mid-circuit measurement with conditional correction.
- Measure the second qubit.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

**Goal**: Create a Bell pair, measure the first qubit, conditionally correct the second qubit to reset it to |0>, then measure the second qubit.

**Qubits**: 2 qubits (q[0], q[1]), both measured.

**Step-by-step state evolution**:

1. Initial state: |00>

2. Apply H(q[0]): (1/√2)(|0> + |1>)|0> = (1/√2)(|00> + |10>)

3. Apply CNOT(q[0], q[1]): (1/√2)(|00> + |11>) — this is the Bell state |Φ+>

4. Measure q[0]:
   - If result is 0 (probability 1/2): state collapses to |00>
   - If result is 1 (probability 1/2): state collapses to |11>, flag = true

5. Conditional X on q[1]:
   - If flag is true: |11> → |10>
   - If flag is false: |00> stays |00>

6. Measure q[1]:
   - From |00>: q[1] measures as 0
   - From |10>: q[1] measures as 0

Wait, but The resulting probabilities should be {|01>: 0.5, |10>: 0.5}. Let me reconsider.

The bitstring format says "earlier measured qubit = higher bit". So q[0] is measured first, making it the higher bit, and q[1] is measured second, making it the lower bit.

So the bitstring is (q[0] result)(q[1] result).

After the correction:
- If q[0] measures as 0: state is |00>, then q[1] measures as 0 → bitstring "00"
- If q[0] measures as 1: state is |10>, then q[1] measures as 0 → bitstring "10"

This would give {|00>: 0.5, |10>: 0.5}, not {|01>: 0.5, |10>: 0.5}.

Hmm, but The predicted output {|01>: 0.5, |10>: 0.5}. Let me re-read the problem.

Wait, maybe the correction is supposed to happen AFTER both measurements? No, that doesn't make sense with the code structure.

Let me re-read: "conditionally applies X to the second qubit based on the measurement result. This should reset the second qubit to |0>."

After Bell state creation: (1/√2)(|00> + |11>)

If we measure q[0] and get 0: state is |00>, q[1] is already |0>
If we measure q[0] and get 1: state is |11>, q[1] is |1>, need X to flip to |0>

So after correction:
- q[0]=0: |00>, q[1]=|0>
- q[0]=1: |10>, q[1]=|0>

Then measuring q[1] gives 0 in both cases.

So the final measurement results would be:
- |00>: 0.5 (q[0]=0, q[1]=0)
- |10>: 0.5 (q[0]=1, q[1]=0)

But the expected says {|01>: 0.5, |10>: 0.5}. This doesn't match.

Unless... the measurement of q[1] happens before the correction? Or there's something else going on.

Wait, maybe I'm misunderstanding the bit ordering. Let me re-read: "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."

So if q[0] is measured first and q[1] is measured second:
- q[0] result = higher bit
- q[1] result = lower bit
- bitstring = (q[0])(q[1])

So |00> means q[0]=0, q[1]=0. |10> means q[0]=1, q[1]=0.

With the correction, we'd get:
- |00>: 0.5
- |10>: 0.5

But the expected is {|01>: 0.5, |10>: 0.5}. There's a discrepancy.

Actually, let me reconsider. Maybe the problem statement's expected probabilities are wrong, or maybe there's a different interpretation.

Looking at the code more carefully:

The second measurement M(q

## isqTrain/2011

- task_id: `isqTrain/2011`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4298`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[5];
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    CNOT(q[0], q[3]);
    Toffoli(q[1], q[3], q[4]);
    CNOT(q[1], q[3]);
    Toffoli(q[2], q[3], q[4]);
    CNOT(q[2], q[3]);
    M(q[3]);
    M(q[4]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 5 qubits to |00000>. The first three X gates flip q[0], q[1], and q[2], resulting in the state |11100>.
2. CNOT(q[0], q[3]) flips q[3] to |1>, evolving the state to |11110>.
3. Toffoli(q[1], q[3], q[4]) flips q[4] because both q[1] and q[3] are |1>, evolving the state to |11111>.
4. CNOT(q[1], q[3]) flips q[3] back to |0>, evolving the state to |11101>.
5. Toffoli(q[2], q[3], q[4]) leaves q[4] unchanged because q[3] is |0>, keeping the state |11101>.
6. CNOT(q[2], q[3]) flips q[3] again, returning the state to |11111>.
7. Measurements are applied to q[3] and q[4], both of which are deterministically in the |1> state.

Predicted probability distribution: {'11': 1.0}

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'Weighted adder 1+1+1=3 -> state |11>, index 3 has P=1.0.'}

## isqTrain/3517

- task_id: `isqTrain/3517`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4391`

### Prompt

预测以下isQ代码的输出概率：

```
import std;

qbit q[3];

procedure main() {
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state of the 3-qubit system is $|000\rangle$.
2. `CNOT(q[0], q[1])`: Control qubit $q_0$ is in state $|0\rangle$, so target qubit $q_1$ is not flipped. The state remains $|000\rangle$.
3. `CNOT(q[0], q[2])`: Control qubit $q_0$ is in state $|0\rangle$, so target qubit $q_2$ is not flipped. The state remains $|000\rangle$.
4. The final quantum state before measurement is $|000\rangle$.
5. Since no superposition or bit-flip operations are applied, the measurement is deterministic.

Predicted probability distribution: {"000": 1.0}

### Reference answer

{'predicted_probs': {'000': 1.0}, 'explanation': 'The output is |000> with probability 1.0'}

## isqTrain/4551

- task_id: `isqTrain/4551`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `isq_syntax_for_loop`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2393`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];

procedure main() {
    
    X(q[0]);

    
    
    
    

    
    CNOT(q[0], q[1]);
    
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);

    
    X(q[0]); H(q[1]);  // replaced H with X
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

Let me analyze this circuit step by step.

Initial state: |00>

Step 1: X(q[0]) → |10>

Step 2: CNOT(q[0], q[1]) → |11>

Step 3: Rz(π/2, q[1]) → |11> (phase on |11> becomes e^{-iπ/4}... wait, Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}). So Rz(π/2, q[1]) on |11> gives e^{iπ/4}|11>)

Wait, let me be more careful. Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]].

Applied to q[1] when state is |11>: the q[1] is in |1>, so the amplitude gets multiplied by e^{iθ/2} = e^{iπ/4}.

Step 4: CNOT(q[0], q[1]) → |11> (control is 1, target is 1, flips to 0): |10>

Wait no. CNOT(q[0], q[1]) with q[0] as control and q[1] as target. State is |11>: control q[0]=1, so flip q[1]: 1→0, giving |10>.

So after step 4: e^{iπ/4}|10>

Step 5: X(q[0]); H(q[1])
X(q[0]) on |10>: |00>
H(q[1]) on |00>: (|00> + |01>)/√2

So state: e^{iπ/4}(|00> + |01>)/√2

Step 6: CNOT(q[0], q[1])
On (|00> + |01>)/√2: |00> stays |00>, |01> stays |01> (control is 0).
State: e^{iπ/4}(|00> + |01>)/√2

Step 7: Rz(π/2, q[1])
On (|00> + |01>)/√2:
|00>: q[1]=0, multiply by e^{-iπ/4}
|01>: q[1]=1, multiply by e^{iπ/4}

State: e^{iπ/4}(e^{-iπ/4}|00> + e^{iπ/4}|01>)/√2 = (|00> + e^{iπ/2}|01>)/√2 = (|00> + i|01>)/√2

Step 8: CNOT(q[0], q[1])
Control is q[0]=0 for both terms, so nothing changes.
State: (|00> + i|01>)/√2

Step 9: H(q[0]); H(q[1])
H(q[0])⊗H(q[1]) applied:
|00> → (|0>+|1>)(|0>+|1>)/2 = (|00>+|01>+|10>+|11>)/2
|01> → (|0>+|1>)(|0>-|1>)/2 = (|00>-|01>+|10>-|11>)/2

So state: [(|00>+|01>+|10>+|11>) + i(|00>-|01>+|10>-|11>)]/(2√2)
= [(1+i)|00> + (1-i)|01> + (1+i)|10> + (1-i)|11>]/(2√2)

Hmm, let me redo. Actually wait, I need to be more careful.

(1+i) = √2 * e^{iπ/4}
(1-i) = √2 * e^{-iπ/4}

So state: [e^{iπ/4}|00> + e^{-iπ/4}|01> + e^{iπ/4}|10> + e^{-iπ/4}|11>]/2

Step 10: CNOT(q[0], q[1])
|00> → |00>
|01> → |01>
|10> → |11>
|11> → |10>

State: [e^{iπ/4}|00> + e^{-iπ/4}|01> + e^{iπ/4}|11> + e^{-iπ/4}|10>]/2
= [e^{iπ/4}|00> + e^{-iπ/4}|10> + e^{-iπ/4}|01> + e^{iπ/4}|11>]/2

Step 11:

### Reference answer

{'predicted_probs': {'01': 0.5, '11': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 0.5000, P(|11>) = 0.5000.'}

# ISQ training COT RAG corpus: quantum_algorithms shard 128

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/103

- task_id: `isqExpand/algo/103`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `ancilla_usage`
- source: `isq_expansion`
- dataset_index: `2603`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[4];

procedure main() {
    X(q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    Toffoli(q[0], q[1], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}
```

### Chain-of-thought reasoning

## Reasoning
Goal: Predict output of half adder with A=0, B=1.

1. X(q[1]): B=1. A=q[0]=0 (default).
2. CNOT(q[0], q[2]): q[0]=0, no flip -> q[2]=0
3. CNOT(q[1], q[2]): q[1]=1, flip q[2] -> q[2]=1 (Sum=1)
4. Toffoli(q[0], q[1], q[3]): q[0]=0, so no flip -> q[3]=0 (Carry=0)

Final: |0110> = index 6 in 4-qubit space.
16-element array: [0]*6 + [1.0] + [0]*9

### Reference answer

{'predicted_probs': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'explanation': 'This is a quantum half adder with inputs A=q[0]=0, B=q[1]=1 (set by X). Step by step: CNOT(q[0],q[2]) does nothing (q[0]=0). CNOT(q[1],q[2]) flips q[2] to 1 (Sum = 0 XOR 1 = 1). Toffoli(q[0],q[1],q[3]) does nothing (q[0]=0, so AND=0, Carry=0). Final state: q[0]=0, q[1]=1, q[2]=1, q[3]=0 = |0110>. Index = 0*8+1*4+1*2+0 = 6. Only index 6 has probability 1.0.'}

## isqTrain/3499

- task_id: `isqTrain/3499`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1708`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```
import std;

qbit q[3];

procedure main() {
    X(q[0]);
    ctrl ctrl X(q[0], q[1], q[2]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: X on q[0]; Toffoli (controlled-controlled-X) on q[0], q[1], q[2]; CNOT on q[0], q[1]; Measurement of all qubits.
2. **State Evolution**:
   - Initial state: |000⟩.
   - `X(q[0])` flips q[0] to |1⟩, resulting in |100⟩.
   - `ctrl ctrl X(q[0], q[1], q[2])` (Toffoli) evaluates controls q[0]=|1⟩ and q[1]=|0⟩. Since q[1] is |0⟩, q[2] is not flipped. State remains |100⟩.
   - `CNOT(q[0], q[1])` flips q[1] because q[0] is |1⟩. The state evolves to |110⟩.
3. **Final state**: |110⟩.
4. **Predicted probabilities**: The state is deterministically |110⟩. Thus, measuring q[0], q[1], q[2] yields 110 with a probability of 1.0.

### Reference answer

{'predicted_probs': {'110': 1.0}, 'explanation': 'The output is |110> with probability 1.0'}

## isqTrain/4474

- task_id: `isqTrain/4474`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `interference`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `68`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;

qbit q[3];

procedure main() {
    
    X(q[2]);
    
    H(q[0]);
    
    ctrl SWAP(q[0], q[1], q[2]);
    
    H(q[0]);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the probability distribution of measurement outcomes for an isQ program.
    *   Program Details: 3 qubits `q[3]`. X on `q[2]`, H on `q[0]`, ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2]), H on `q[0]`, X on `q[0]`. Measure `q[0]`.
    *   predicted output Format: "## Circuit Analysis", 3-8 lines (simple), concise step-by-step reasoning, use Dirac notation, end with predicted probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: $|000\rangle$
    *   X(q[2]): Flips qubit 2. State becomes $|001\rangle$
    *   H(q[0]): Applies Hadamard to qubit 0. State becomes $\frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$
    *   ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2]):
        *   If `q[0]` is $|1\rangle$, swap `q[1]` and `q[2]`.
        *   Wait, the syntax `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])` might mean `q[0]` controls a swap (three-CNOT decomposition) between `q[1]` and `q[2]`? Let's check isQ syntax for `ctrl`. Usually `ctrl @[control] Gate(targets)`. Here it's `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])`. In isQ, `ctrl swap (three-CNOT decomposition)(q0, q1, q2)` typically means q0 controls the swap (three-CNOT decomposition) on q1 and q2. Wait, no. A standard swap (three-CNOT decomposition) takes 2 qubits. `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])` likely means `q[0]` controls the swap (three-CNOT decomposition) of `q[1]` and `q[2]`. Wait, or is it a controlled-swap operation (three-CNOT decomposition)? Yes, a controlled-swap operation (three-CNOT decomposition) is Cswap (three-CNOT decomposition).
        *   Let's look at the state $\frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$.
        *   $|001\rangle$: control q[0] is 0. No swap. Remains $|001\rangle$.
        *   $|101\rangle$: control q[0] is 1. Swaps q[1] and q[2]. q[1]=0, q[2]=1 -> q[1]=1, q[2]=0. State becomes $|110\rangle$.
        *   State after Cswap (three-CNOT decomposition): $\frac{1}{\sqrt{2}}(|001\rangle + |110\rangle)$.
    *   H(q[0]):
        *   $|001\rangle \to \frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$
        *   $|110\rangle \to \frac{1}{\sqrt{2}}(|110\rangle - |010\rangle)$
        *   Total state: $\frac{1}{2}(|001\rangle + |101\rangle + |110\rangle - |010\rangle)$
    *   X(q[0]): Flips qubit 0.
        *   $|001\rangle \to |101\rangle$
        *   $|101\rangle \to |001\rangle$
        *   $|110\rangle \to |010\rangle$
        *   $-|010\rangle \to -|110\rangle$
        *   Total state: $\frac{1}{2}(|101\rangle + |001\rangle + |010\rangle - |110\rangle) = \frac{1}{2}(|001\rangle + |101\rangle + |010\rangle - |110\rangle)$.
    *   Wait, only `q[0]` is measured.
    *   Let's re-evaluate the measurement on `q[0]`.
    *   Before X(q[0]):
        *   State was $\frac{1}{2}(|001\rangle + |101\rangle + |110\rangle - |010\rangle)$.
        *   Let's group by q[0]:
        *   q[0]=0: $\frac{1}{2}(|001\rangle - |010\rangle)$ -> Probability of q[0]=0 is $(1/2)^2 + (-1/2)^2 = 0.5$.
        *   q[0]=1: $\frac{1}{2}(|101

### Reference answer

{'predicted_probs': {'000': 0.5, '001': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.5000, P(|001>) = 0.5000.'}

## isqTrain/1408

- task_id: `isqTrain/1408`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `433`

### Prompt

I need an isQ program to the Bernstein-Vazirani algorithm to find the secret string s = 10011 (MSB first). Use 5 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Bernstein-Vazirani to find secret string s = 10011 via phase oracle encoding.

Six qubits used: q[0..4] (input register, measured) and anc[0] (ancilla, unmeasured).

State evolution:
1. Initialize |00000⟩|0⟩, then X(anc[0]) → |00000⟩|1⟩, then H(anc[0]) → |00000⟩|−⟩
2. Apply H to all inputs: (1/4√2) Σₓ |x⟩|−⟩ over all x ∈ {0,1}⁵
3. Oracle CNOTs from q[0], q[3], q[4] → anc[0] encode s·x, flipping ancilla when corresponding input bit is |1⟩
   State: (1/4√2) Σₓ (−1)^(s·x) |x⟩|−⟩, since |−⟩ acquires (−1) phase per flip
4. Apply H⊗⁵ to input register: transforms Σₓ(−1)^(s·x)|x⟩ → |s⟩ = |10011⟩

Measuring all 5 input qubits yields |10011⟩ with probability 1.0, as H⊗⁵ on the phase-encoded superposition perfectly recovers s.

## isqTrain/4187

- task_id: `isqTrain/4187`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4442`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 1.000, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    Rz(2.0 * 1.000, q[2]);
    CNOT(q[1], q[2]);
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations applied:**
   - Hadamard on all 3 qubits: H(q[0]), H(q[1]), H(q[2])
   - Controlled-Rz(2.0) on q[1] with control q[0]: CNOT-Rz(2.0)-CNOT
   - Controlled-Rz(2.0) on q[2] with control q[1]: CNOT-Rz(2.0)-CNOT
   - Rx(π) on all 3 qubits: Rx(2.0 × 0.500, q[i]) for i=0,1,2

2. **State evolution:**
   - Start: |000⟩
   - After H⊗³: |+++⟩ = (1/2√2)∑_{x,y,z∈{0,1}} |xyz⟩
   - CNOT(a,b)-Rz(2.0,b)-CNOT(a,b) = CRz(2.0,a→b): applies phase e^(i·1.0) when both a,b = |1⟩
   - After two CRz gates: state picks up phase e^(i·1.0) for |11⟩ on (q[0],q[1]) pair, and e^(i·1.0) for |11⟩ on (q[1],q[2]) pair
   - Rx(π) ≈ -iX (up to global phase): flips |0⟩↔|1⟩ with -i phase

3. **Final state:** Complex superposition with phase factors from CRz(2.0) followed by bit-flip from Rx(π).

4. **Predicted probability distribution:**
   - With θ = 1.0 rad (non-special angle), interference produces a non-uniform distribution
   - All 8 basis states have non-zero probability
   - Probabilities approximately: P(000) ≈ 0.35, P(001) ≈ 0.15, P(010) ≈ 0.03, P(011) ≈ 0.05, P(100) ≈ 0.15, P(101) ≈ 0.07, P(110) ≈ 0.15, P(111) ≈ 0.05
   - Most likely outcome: **|000

### Reference answer

Uniform distribution across 8 states

## isqTrain/128

- task_id: `isqTrain/128`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `interference`, `isq_syntax_arrays`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2589`

### Prompt

Create an isQ quantum circuit that implements the oracle_boolean pattern but with a different initial state preparation (flip q[[3]] -> q[1]).

### Chain-of-thought reasoning

The user wants me to implement an oracle_boolean pattern with a different initial state preparation. Let me analyze The implementation and understand what needs to be changed.

circuit implementation analysis:
1. It prepares ancilla q[1] in |-> initially (X(q[1]) then H(q[1]))
2. Actually wait, let me re-read. The reference shows:
   - X(q[1]) - flips q[1]
   - H(q[3]) - Hadamard on q[3]
   - H(q[0]), H(q[1]), H(q[2]) - prepares inputs in |+>

Wait, I need to re-read the prompt. It says "flip q[[3]] -> q[1]". This seems to indicate changing from flipping q[3] to flipping q[1].

Analyzing the:
- X(q[1]) flips q[1]
- H(q[3]) puts q[3] in |+>

The task says to implement oracle_boolean but with "flip q[[3]] -> q[1]". This means instead of flipping q[3] (the ancilla), we should flip q[1].

Actually, let me re-interpret. The reference code has:
1. X(q[1]) - this flips q[1]
2. H(q[3]) - this applies H to q[3]

The prompt says "flip q[[3]] -> q[1]", which could mean:
- Change from flipping q[3] to flipping q[1]

But the reference already flips q[1]. Let me look more carefully...

Actually, I think I need to look at the typical Bernstein-Vazirani or oracle pattern. In Bernstein-Vazirani:
- We have input qubits prepared in |+>
- We have an ancilla qubit prepared in |->
- The oracle applies CNOTs based on the secret string

In the reference:
- q[0], q[1], q[2] are input qubits (prepared in |+>)
- q[3] is the ancilla

The comment says "Prepare ancilla in |->" but then does X(q[1]) and H(q[3]). This seems inconsistent with the comment...

Let me trace through the reference:
1. X(q[1]) - |0000> -> |0100>
2. H(q[3]) - |0100> -> (|0100> + |0101>)/√2
3. H(q[0]), H(q[1]), H(q[2]) - creates superposition

Wait, the order matters. After step 1: |0100>
After H(q[3]): q[3] is in |+>, so state is |0100> (since q[3]=0, and H|0>=|+>)

Hmm, this is getting confusing. Let me think about what the predicted output should be.

Expected measurement probabilities: {|010>: 1.0}

This means q[0]=0, q[1]=1, q[2]=0 after measurement (assuming big-endian where q[0] is MSB).

Actually wait, the reference measures q[0], q[1], q[2]. The predicted output |010>, so:
- q[0] = 0
- q[1] = 1  
- q[2] = 0

This looks like it could be Bernstein-Vazirani where the secret string is "010" and we get that back.

Now the task says "flip q[[3]] -> q[1]". I interpret this as: instead of the typical setup where we flip the ancilla (q[3]) to prepare it in |->, we flip q[1] instead.

But in Bernstein-Vazirani, flipping the ancilla is crucial for phase kickback. If we don't flip the ancilla, we won't get the phase kickback.

Let me think about this differently. The reference code:
1. X(q[1]) - flips q[1]
2. H(q[3]) - puts ancilla in |+>
3. H(q[0]), H(q[1]), H(q[2]) - puts inputs in |+>
4. Oracle: CNOT(q[0], q[3]), CNOT(q[2], q[3])
5. H(q[0]), H(q[1]), H(q[2]) - inverse Hadamard
6. Measure q[0], q[1], q[2]

The oracle with CNOTs from q[0] and q[2] to q[3] would encode secret string "101".

For Bernstein-Vazirani with ancilla in |->:
- Initial: |0...0>|1> -> after X on ancilla
- After H on all: |+...+>|-> = (1/√

## isqTrain/3623

- task_id: `isqTrain/3623`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4638`

### Prompt

Implement the following in isQ: a 4-qubit Grover search for target state |1101> using the optimal 3 iterations. The circuit should:
1. Initialize 4 qubits in uniform superposition
2. Apply 3 Grover iterations (oracle + diffusion) using a for loop
3. Measure all 4 qubits
Use `deriving gate` and `ctrl<2> CZ` for the multi-controlled phase.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement 4-qubit Grover search to amplify the amplitude of target state |1101> (where q[0]=1,q[1]=1,q[2]=0,q[3]=1) using 3 optimal iterations.

All 4 qubits are measured, producing a 4-bit outcome with highest probability at |1101>.

**State evolution:**
1. **Init**: |0000>
2. **Superposition**: H⊗4 → |s⟩ = (1/4)Σ|x⟩ over all 16 basis states
3. **Oracle** (marks |1101>): X(q[2]) converts |1101>→|1111>, ctrl<2>CZ applies -1 phase to |1111>, X(q[2]) restores → |1101⟩ acquires -1 phase
4. **Diffusion**: H⊗4 → X⊗4 → ctrl<2>CZ → X⊗4 → H⊗4 reflects state about mean |s⟩, amplifying marked state amplitude
5. **3 iterations**: Each Grover iteration rotates state ~22.5° toward |1101⟩ in the 2D {|s⟩,|1101⟩} subspace. After 3 iterations: sin²(3×arcsin(1/4)) ≈ 96.3% probability at |1101⟩
6. **Final state**: ~0.963|1101⟩ + ~0.002Σ|other⟩

## isqTrain/819

- task_id: `isqTrain/819`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4971`

### Prompt

Write an isQ program that implements the quadratic_form pattern. Include explicit identity operations in the circuit (H-H pair before M(q[2])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement the quadratic form f(x₀,x₁) = x₀ AND x₁ using phase kickback, measuring the resulting probability distribution.

2. **Qubits**: 3 qubits (q[0], q[1] as inputs, q[2] as target); only q[2] is measured.

3. **State evolution**:
   - Initial: |000⟩
   - After H(q[0]), H(q[1]): (1/2)(|000⟩ + |010⟩ + |100⟩ + |110⟩)
   - After Toffoli(q[0],q[1],q[2]): (1/2)(|000⟩ + |010⟩ + |100⟩ + |111⟩)
   - After first H(q[2]): (1/2√2)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ - |111⟩)
   - After second H(q[2]): (1/2)(|000⟩ + |010⟩ + |100⟩ + |111⟩) — H·H = I, gate cancellation demonstrated

4. **Probabilities**: Measuring q[2], states |000⟩,|010⟩,|100⟩ yield outcome 0 (total weight 3/4), while |111⟩ yields outcome 1 (weight 1/4), giving P(|0⟩) = 0.75, P(|1⟩) = 0.25.

## isqTrain/3643

- task_id: `isqTrain/3643`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `1184`

### Prompt

帮我写一个isQ程序：the 3-qubit inverse Quantum Fourier Transform (QFT†) on input |010>. Use bit-reversal swaps first, then apply inverse rotation stages with negative angles. Measure all qubits.

### Chain-of-thought reasoning

Looking at this problem, I need to trace through the inverse QFT† applied to |010> on 3 qubits.

The goal is to implement inverse QFT on 3 qubits with input |010>.

Let me trace through the circuit step by step.

Initial state: |010> (after X(q[1]))

The inverse QFT circuit (with bit-reversal first) does:
1. Bit-reversal swaps: swap q[0] and q[2]
2. Inverse rotation stages with negative angles

For QFT on 3 qubits, the forward QFT would be:
- H on q[0], controlled Rk gates on q[0]
- H on q[1], controlled Rk gates on q[1]
- H on q[2], controlled Rk gates on q[2]
- Then bit-reversal swaps

For inverse QFT†, we reverse the order:
- Bit-reversal swaps first (swap q[0] and q[2])
- Then inverse of each gate

Let me trace the state evolution:

Starting: |q2 q1 q0> = |010>

After bit-reversal swap (swap q[0] and q[2]):
State becomes |010> → |010> (q[0]=0 swaps with q[2]=0, so no change)

Wait, let me reconsider. The qubits are q[0], q[1], q[2] representing |q2 q1 q0> in standard notation.

Actually, let me be careful. The input |010> means q[0]=0, q[1]=1, q[2]=0.

After X(q[1]): state is |010>

Now the inverse QFT:
1. Bit-reversal: swap q[0] and q[2]
   |010> → swap q0 and q2 → |010> (both are 0, so same)

2. H(q[2]): q[2] goes from |0> to |+> = (|0>+|1>)/√2
   State: (|010> + |110>)/√2

3. CRz(-π/4) with q[2] control, q[1] target:
   When q[2]=1, apply Rz(-π/4) to q[1]
   |010> stays |010>
   |110> → |1>(Rz(-π/4)|1>)|0> = e^(iπ/8)|110>
   Wait, Rz(θ)|1> = e^(-iθ/2)|1>
   Rz(-π/4)|1> = e^(iπ/8)|1>
   State: (|010> + e^(iπ/8)|110>)/√2

4. H(q[1]):
   |0> → |+>, |1> → |->
   |010> → (|000> + |010>)/√2
   |110> → (|100> - |110>)/√2 * e^(iπ/8)
   State: (|000> + |010> + e^(iπ/8)|100> - e^(iπ/8)|110>)/2

5. CRz(-π/8) with q[2] control, q[0] target:
   When q[2]=1, apply Rz(-π/8) to q[0]
   States where q[2]=1: |100> and |110>
   |100> → Rz(-π/8) on q[0] when |1>: e^(iπ/16)|100>
   |110> → Rz(-π/8) on q[0] when |1>: e^(iπ/16)|110>
   State: (|000> + |010> + e^(iπ/8)e^(iπ/16)|100> - e^(iπ/8)e^(iπ/16)|110>)/2
   = (|000> + |010> + e^(3iπ/16)|100> - e^(3iπ/16)|110>)/2

6. CRz(-π/4) with q[1] control, q[0] target:
   When q[1]=1, apply Rz(-π/4) to q[0]
   States where q[1]=1: |010> and |110>
   |010> → q[0]=0, Rz doesn't affect |0>: |010>
   |110> → q[0]=0, Rz doesn't affect |0>: |110>
   Wait, q[0] is 0 in these states, so Rz(-π/4)|0> = |0>

## isqExpand/algo/128

- task_id: `isqExpand/algo/128`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `superposition`, `phase_manipulation`, `interference`
- source: `isq_expansion`
- dataset_index: `1585`

### Prompt

Fix the bug in this quantum program:

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    X(q[1]);
    H(q[2]); Toffoli(q[0], q[1], q[2]); H(q[2]);
    X(q[1]);
    H(q[0]); H(q[1]); H(q[2]);
    H(q[2]); Toffoli(q[0], q[1], q[2]); H(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
Diffusion is H-Toffoli(as CCZ via H)-H, but should be H-X-CCZ-X-H.
Without X, CCZ marks |111> instead of |000> in the H-transformed basis.

Fix: Add X on all 3 qubits before and after the CCZ block in diffusion.

After fix: P(|101>) = 25/32 = 0.78125.

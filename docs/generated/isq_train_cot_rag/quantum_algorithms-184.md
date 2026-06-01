# ISQ training COT RAG corpus: quantum_algorithms shard 184

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3653

- task_id: `isqTrain/3653`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `2570`

### Prompt

用isQ实现2-bit quantum phase estimation (QPE) to estimate the phase 0 of a Rz rotation gate. Use:
1. Two precision qubits and one eigenstate qubit
2. Prepare eigenstate |1> on the target qubit
3. Apply controlled-Rz operations
4. Apply inverse QFT on precision register
5. Measure all qubits

### Chain-of-thought reasoning

Let me analyze this QPE circuit step by step.

Goal: Implement 2-bit QPE to estimate phase θ=0 of Rz rotation on eigenstate |1>.

The Rz gate is Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]. For |1>, the eigenvalue is e^{iθ/2}.

Wait, let me re-read the problem. The phase is 0, so θ=0. Then Rz(0) = I (identity), and the eigenvalue for |1> is e^{i*0/2} = 1 = e^{i*0}.

So the phase φ = 0/(2π) = 0, which in binary is 00.

Qubits: q[0] and q[1] are precision qubits, q[2] is the target/eigenstate qubit.

Step-by-step:

1. Initial state: |000⟩

2. X(q[2]): |001⟩ → q[2] is now |1⟩

Wait, actually let me think about the bit ordering. In the code:
- q[0], q[1] are precision qubits
- q[2] is the target qubit

After X(q[2]): state is |001⟩ (q[2]=|1⟩, q[1]=|0⟩, q[0]=|0⟩)

Hmm, but in the bitstring ordering for measurement, earlier measured qubit = higher bit. So M(q[0]) is the highest bit, M(q[1]) is middle, M(q[2]) is lowest bit.

3. H(q[0]); H(q[1]): Apply Hadamard to precision qubits
|001⟩ → (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ |1⟩ = 1/2(|001⟩ + |011⟩ + |101⟩ + |111⟩)

4. Controlled-Rz operations with phase 0:
ctrl Rz(2π * 0/4 * 1, q[0], q[2]) - this applies Rz(0) = I, controlled by q[0]
ctrl Rz(2π * 0/4 * 2, q[1], q[2]) - this applies Rz(0) = I, controlled by q[1]

Since the rotation angle is 0, both controlled operations do nothing. The state remains:
1/2(|001⟩ + |011⟩ + |101⟩ + |111⟩)

Wait, but actually the controlled-Rz(θ) on a target in |1⟩ applies a phase of e^{iθ/2} to the target. Let me reconsider.

Rz(θ)|1⟩ = e^{iθ/2}|1⟩

So controlled-Rz(θ) with control in |1⟩ and target in |1⟩ applies a phase of e^{iθ/2} to the combined state.

For the first controlled-Rz: θ₁ = 2π * 0/4 * 1 = 0, so phase = e^{i*0/2} = 1
For the second controlled-Rz: θ₂ = 2π * 0/4 * 2 = 0, so phase = e^{i*0/2} = 1

So indeed no phases are applied. State remains:
1/2(|001⟩ + |011⟩ + |101⟩ + |111⟩)

5. Inverse QFT on precision qubits (q[0], q[1]):

The inverse QFT for 2 qubits is:
- First, we need to understand the QFT. For 2 qubits, QFT maps |ab⟩ to:
  1/2 Σ_c,d e^{2πi(ab)/2 * ... }

Actually, let me just trace through the gates:

The code does:
swap (three-CNOT decomposition)(q[0], q[1]) via 3 CNOTs
H(q[0])
ctrl Rz(-π/2, q[1], q[0])
H(q[1])

Wait, this doesn't look like standard inverse QFT. Let me think about this more carefully.

Standard QFT for 2 qubits (q[0] is MSB, q[1] is LSB):
1. H(q[0])
2. ctrl Rz(π/2, q[1], q[0]) - controlled phase from q[1] to q[0]
3. H(q[1])
4. swap (three-CNOT decomposition)(q[0], q[1])

Inverse QFT would be:
1. swap (three-CNOT decomposition)(q[0], q[1])
2. H(q[1])
3. ctrl Rz(-π/2

## isqTrain/2925

- task_id: `isqTrain/2925`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2881`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```isq
import std;
qbit q[2];
// Controlled Rz(1*pi/8)
procedure main() {
    // H(q[0]); // BUG: missing Hadamard
    X(q[1]);
    ctrl Rz(0.392699, q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug:** The initial `H(q[0])` gate is commented out, leaving `q[0]` in the |0> state instead of creating a superposition. Without this, the controlled-Rz gate cannot perform phase kickback correctly.
2. **The fix:** Uncomment `H(q[0])` at the beginning of the procedure to initialize `q[0]` into the |+> state.
3. **State evolution:** 
   - Start: |00>
   - H(q[0]), X(q[1]): 1/√2 (|01> + |11>)
   - ctrl Rz(pi/8): 1/√2 (|01> + e^(i*pi/8)|11>)
   - H(q[0]): ((1+e^(i*pi/8))/2)|01> + ((1-e^(i*pi/8))/2)|11>
   - Measurements yield |01> with ~99.04% probability and |11> with ~0.96% probability, matching the predicted output.

## isqTrain/835

- task_id: `isqTrain/835`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `4806`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[3];

procedure main() {
    // Prepare input |101> = 5
    X(q[0]);
    X(q[2]);
    // 3-qubit QFT: process from MSB to LSB
    // Qubit 2 (MSB)
    H(q[2]);
    ctrl S(q[1], q[2]);
    ctrl T(q[0], q[2]);
    // Qubit 1 (middle)
    H(q[1]);
    ctrl S(q[0], q[1]);
    // Qubit 0 (LSB)
    H(q[0]);
    // Bit-reversal swap of q[0] and q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **State Preparation:** The circuit initializes 3 qubits to $|000\rangle$. The `X` gates on `q[0]` and `q[2]` prepare the input state $|101\rangle$, which represents the integer $x = 5$.
2. **QFT Operations:** The circuit applies the Quantum Fourier Transform (QFT) over $N=8$ dimensions. This involves applying Hadamard (`H`) gates and controlled phase rotations (`ctrl S`, `ctrl T`).
3. **Bit-Reversal Swap:** The sequence of 3 `CNOT` gates swaps the states of `q[0]` and `q[2]`, completing the standard QFT algorithm.
4. **State Evolution:** The QFT transforms the basis state $|x\rangle$ into the state $\frac{1}{\sqrt{N}} \sum_{y=0}^{N-1} e^{2\pi i x y / N} |y\rangle$. For $x=5$ and $N=8$, the final state is a superposition of all 8 possible basis states ($|000\rangle$ to $|111\rangle$), where each state has an amplitude of magnitude $1 /

### Reference answer

{'predicted_probs': {'0': 0.12499999999999997, '1': 0.12500000000000003, '2': 0.125, '3': 0.12500000000000006, '4': 0.125, '5': 0.12500000000000003, '6': 0.12499999999999996, '7': 0.125}, 'explanation': 'Parametric variant of isqEval/291. Dimension: predict probabilities for reference circuit.'}

## isqTrain/795

- task_id: `isqTrain/795`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `910`

### Prompt

Write isQ code for the following quantum task: implements a variant of the quantum_multiplier pattern using q[4] -> q[6]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a quantum multiplier variant computing a=1 × b=3, storing the product LSB in an expanded 6-qubit register.
2. **Qubits**: 6 qubits (q[0]–q[5]); q[0] stores multiplier a, q[1]–q[2] store multiplicand b, q[3] holds the product LSB, q[4]–q[5] remain ancillary/unused; measuring q[3], q[4], q[5].
3. **State evolution**:
   - Initial: |000000⟩
   - X(q[0]) → |100000⟩ (set a=1)
   - X(q[1]), X(q[2]) → |111000⟩ (set b=3=11₂)
   - Toffoli(q[0], q[1], q[3]): since q[0]=1 AND q[1]=1, flips q[3] → |111100⟩
4. **Final measurement**: q[3]=1, q[4]=0, q[5]=0 yields bitstring |100⟩ with probability 1.0, as q[4] and q[5] were never acted upon and remain in |0⟩.

## isqTrain/2691

- task_id: `isqTrain/2691`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `742`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[3];

procedure main(){
    H(q[0]);
    X2P(q[1]);
    CZ(q[0], q[2]);
    Y2M(q[0]);
    CZ(q[2], q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

The user wants to know the exact probability of each computational basis state after measurement for the given isQ program.

Let's analyze the circuit step by step:
Qubits: q[0], q[1], q[2], initially all in |0>.
Initial state: |000>

1. H(q[0])
State becomes: 1/sqrt(2)(|000> + |100>)
Wait, q[0] is the first qubit, q[1] is the second, q[2] is the third.
Wait, standard tensor product order:
If q[0] is the highest bit or lowest? Usually standard isQ is q[0] is highest bit.
Let's assume q[0] is the first qubit in tensor product.
State: |000> -> H on q[0] -> (|0> + |1>)/sqrt(2) \otimes |0> \otimes |0> = 1/sqrt(2) (|000> + |100>)

2. X2P(q[1])
X2P = Rx(pi/2)
Rx(pi/2) |0> = 1/sqrt(2) (|0> - i|1>)
So q[1] becomes (|0> - i|1>)/sqrt(2)
State: 1/sqrt(2) (|000> + |100>) \otimes (|0> - i|1>)/sqrt(2) \otimes |0>
Wait, q[0] \otimes q[1] \otimes q[2].
State is: 1/2 ( |000> - i|010> + |100> - i|110> )

3. CZ(q[0], q[2])
CZ applies Z on target if control is |1>.
Wait, CZ is symmetric, but applies Z to q[2] when q[0] is |1>.
Z |0> = |0>
Z |1> = -|1>
State: 1/2 ( |000> - i|010> + |100> - i|110> ) -> wait, CZ(q[0], q[2]) checks q[0] and flips sign of q[2].
Only terms where q[0]=1 and q[2]=1 are affected. But currently q[2] is always |0>.
So this gate does nothing to the state!
Wait, is this correct?
Let me double check.
State is a sum of |000>, |010>, |100>, |110>.
In all these terms, the third qubit (q[2]) is 0.
Therefore, CZ(q[0], q[2]) applies Z to |0> which is |0>, or it just applies Z to the third qubit.
Wait, Z acts on the third qubit. Since the third qubit is |0>, Z|0> = |0>. So the state is unchanged.
Wait, what if CZ applies a phase based on the target? No, CZ gives a phase of -1 to |11> on (control, target).
Here, the qubits are q[0] and q[2].
The basis states are |00>, |01>, |10>, |11>.
Our states for (q[0], q[2]) are |00> (from |000>), |00> (from |010>), |10> (from |100>), |10> (from |110>).
None of them is |11>. So the state remains unchanged.
1/2 ( |000> - i|010> + |100> - i|110> )

4. Y2M(q[0])
Y2M = Ry(-pi/2)
Ry(-pi/2) |0> = 1/sqrt(2) (|0> - |1>)
Ry(-pi/2) |1> = 1/sqrt(2) (|0> + |1>)
Apply to q[0]:
|000> -> Ry(-pi/2) on q[0] -> 1/sqrt(2) (|000> - |100>)
|010> -> 1/sqrt(2) (|010> - |110>)
|100> -> 1/sqrt(2) (|000> + |100>)
|110> -> 1/sqrt(2) (|010> + |110>)

Substitute into the state:
1/2 [ 1/sqrt(2)(|000> - |100>) - i * 1/sqrt(2)(|010> - |110>) + 1/sqrt(2)(|000> + |100>) - i * 1/sqrt(2)(|010> + |110>) ]
= 1 / (2*sqrt(2)) [ |

### Reference answer

{'predicted_probs': {'000': 0.5000000000000002, '010': 0.4999999999999999}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2922

- task_id: `isqTrain/2922`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2569`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[2];
// Controlled Rz(1*pi/4)
procedure main() {
    H(q[0]);
    // X(q[1]); // BUG: missing initialization
    ctrl Rz(0.785398, q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The `X(q[1])` gate is commented out on line 8, leaving q[1] in |0⟩ instead of |1⟩. This breaks the phase kickback circuit, which requires the target qubit to be in |1⟩ so that the controlled-Rz can imprint a measurable phase on the control.

2. **Fix**: Uncomment `X(q[1])` so it executes before the controlled-Rz gate, initializing q[1] to |1⟩.

3. **State evolution (corrected)**:
   - |00⟩ → H(q₀) → (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2
   - X(q₁) → (|01⟩+|11⟩)/√2
   - ctrl Rz

## isqTrain/1281

- task_id: `isqTrain/1281`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5642`

### Prompt

Implement the following in isQ: implements a variant of the qaoa pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this QAOA circuit carefully.

The circuit implements QAOA p=1 for MaxCut on a triangle (K3) graph, but with an expanded register of 5 qubits. The active qubits are q[0], q[1], q[2], and q[3], q[4] remain in |0⟩.

Wait, looking more carefully at the prompt - it says "q[3] -> q[5]" which suggests using qubits q[3] through q[5]. But The circuit should q[0], q[1], q[2] as active qubits and q[3], q[4] as idle qubits in a 5-qubit register.

Let me trace through the state evolution:

1. Initial state: |00000⟩

2. After H on q[0], q[1], q[2]: |+++00⟩ = (1/2√2)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩) ⊗ |00⟩

3. Cost layer with γ = π/4:
   - For each edge (0,1), (1,2), (0,2), we apply ZZ interaction via CNOT-Rz-CNOT
   - The ZZ(γ) gate applies phase e^{-iγ} when both qubits are |1⟩

Actually let me think about this more carefully. The Rz rotation applied is -0.785398... = -π/4. 

The CNOT-Rz-CNOT sequence implements: when control is |1⟩, apply Rz to target. This is equivalent to a controlled-phase gate.

For edge (0,1): CNOT(q[0], q[1]); Rz(-π/4, q[1]); CNOT(q[0], q[1])
This applies a phase of e^{-i(-π/4)/2} = e^{iπ/8} when |0⟩ on q[0], and e^{-i(-π/4)/2} · e^{-i(-π/4)} = e^{iπ/8} · e^{iπ/4} when |1⟩ on q[0].

Wait, let me reconsider. Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]. 

The CNOT-Rz(θ)-CNOT sequence: when control is |1⟩, target gets Rz(θ). This is equivalent to:
- Phase e^{-iθ/2} on |00⟩
- Phase e^{iθ/2} on |01⟩  
- Phase e^{-iθ/2} on |10⟩
- Phase e^{iθ/2} on |11⟩

Wait no. Let me be more careful.

CNOT-Rz(θ)-CNOT on control c, target t:
- |00⟩ → |00⟩ (no flip, Rz doesn't change |0⟩ component... wait)

Actually Rz(θ)|0⟩ = e^{-iθ/2}|0⟩ and Rz(θ)|1⟩ = e^{iθ/2}|1⟩.

So:
- |00⟩ → |00⟩ → e^{-iθ/2}|00⟩ → e^{-iθ/2}|00⟩
- |01⟩ → |01⟩ → e^{iθ/2}|01⟩ → e^{iθ/2}|01⟩
- |10⟩ → |11⟩ → e^{iθ/2}|11⟩ → e^{iθ/2}|10⟩
- |11⟩ → |10⟩ → e^{-iθ/2}|10⟩ → e^{-iθ/2}|11⟩

So the overall effect is:
- |00⟩: e^{-iθ/2}
- |01⟩: e^{iθ/2}
- |10⟩: e^{iθ/2}
- |11⟩: e^{-iθ/2}

This is equivalent to a ZZ interaction: exp(-iθ/2 · Z⊗Z) up to global phase.

For θ = -π/4:
- |00⟩: e^{iπ/8}
- |01⟩: e^{-iπ/8}
- |10⟩: e^{-iπ/8}
- |11⟩: e^{iπ/8}

Or equivalently, the phase accumulated is: e^{iπ/4} when both qubits agree (00 or 11), e^{-iπ/4} when they disagree (01 or 10). Wait, let me recalculate.

θ = -π/4, so -θ/2 = π/8, θ/2 = -π/8.

- |00⟩: e^{-

## isqTrain/2707

- task_id: `isqTrain/2707`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1378`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
defgate U0 = [
    1, 0, 0, 0, 0, 0, 0, 0;
    0, -1, 0, 0, 0, 0, 0, 0;
    0, 0, -1, 0, 0, 0, 0, 0;
    0, 0, 0, -1, 0, 0, 0, 0;
    0, 0, 0, 0, -1, 0, 0, 0;
    0, 0, 0, 0, 0, -1, 0, 0;
    0, 0, 0, 0, 0, 0, -1, 0;
    0, 0, 0, 0, 0, 0, 0, -1
];
oracle U_omega(3,1) = [0,1,0,0,0,0,0,0];
qbit q[3];
qbit anc;
int grover_search() {
    H(q);
    X(anc);
    H(anc);
    for i in 0:2 {
        U_omega(q[2], q[1], q[0], anc);
        H(q);
        U0(q[2], q[1], q[0]);
        H(q);
    }
    H(anc);
    X(anc);
    return M(q);
}
procedure main(){
    print grover_search();
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants to know the output probability distribution of a given isQ quantum circuit implementing Grover's search algorithm. I need to generate a concise step-by-step analysis ending with the probability distribution.

2.  **Analyze the Circuit**:
    *   Number of qubits: `q[3]` (3 qubits), `anc` (1 qubit). Total 4 qubits. We measure only `q`.
    *   Initial state: `|0000>`
    *   Initialization:
        *   `H(q)` on q[0], q[1], q[2] -> Creates equal superposition over qubits 0, 1, 2.
        *   `X(anc)`, `H(anc)` -> Puts ancilla in `|->` state.
        *   Combined state: $H^{\otimes 3}|000> \otimes |-> = \frac{1}{2\sqrt{2}} \sum_{x=0}^7 |x> \otimes |->$
    *   Oracle `U_omega(3,1) = [0,1,0,0,0,0,0,0]`:
        *   `3` means 3 control qubits. `1` means 1 target qubit.
        *   The array represents the state(s) that trigger the oracle. Here it's `1` at index 1, which corresponds to `|001>`. Wait, standard bit ordering in isQ for oracles: `[0,1,0,0,0,0,0,0]` implies a Z-gate is applied on the target (or phase flip) when the control state is `|001>`.
        *   Let's check the `anc` state `|->`. A phase flip (Z) on `|->` gives `-|->`. So `U_omega` applies a phase of -1 to `|001>`. Wait, the target is `anc`. The operation is $I - 2|1><1|_x \otimes |1><1|_{anc}$ ? No, standard phase oracle puts a -1 phase on the target, which becomes a -1 phase on the state because `<-|Z|-> = - <-|`. So the state $|x>|->$ gets multiplied by -1 if $x$ is the target.
        *   Target state $|w> = |001>$.
    *   Diffusion operator:
        *   `H(q); U0(q[2], q[1], q[0]); H(q);`
        *   `U0` is a diagonal matrix with 1 at index 0, and -1 at indices 1 to 7. This is $2|0><0| - I$, the standard Grover diffusion operator.
    *   Iterations:
        *   `for i in 0:2` loops from 0 to 2, meaning 3 iterations! (i=0, 1, 2).
        *   Wait, standard Grover for 3 qubits (8 states) requires $\approx \frac{\pi}{4}\sqrt{8} = \frac{\pi\sqrt{8}}{4} \approx 2.22$ iterations.
        *   2 iterations is usually optimal. What happens with 3 iterations?
        *   Let's trace the amplitude of $|w>$ and $|w^\perp>$.
        *   Initial amplitudes: $a = \sin(\theta/2)$ where $\theta = 0$. Wait, initial is $|w^\perp> = \frac{1}{2\sqrt{2}} \sum |x> = \frac{1}{2\sqrt{2}} \sum |x>$. No, uniform superposition is $|s> = \frac{1}{\sqrt{N}}\sum|x>$.
        *   Angle $\theta/2$ such that $\sin(\theta/2) = \frac{1}{\sqrt{8}}$.
        *   Each iteration rotates the state by $\theta$ towards $|w>$.
        *   After $k$ iterations, the amplitude of $|w>$ is $\sin((2k+1)\theta/2)$.
        *   Here $N=8$, $\sin(\theta/2) = 1/\sqrt{8}$, $\theta/2 = \arcsin(1/\sqrt{8})$.
        *   After 3 iterations ($k=3$), amplitude of $|w>$ is $\sin(7\theta/2)$.
        *   Let's calculate exactly.
        *   $N=8$, $\sin(\theta/2) = 1/(2\sqrt{2})

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1253

- task_id: `isqTrain/1253`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1569`

### Prompt

Implement the following in isQ: implements a variant of the error_correction_syndrome pattern using data[3] -> data[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to generate reasoning for a variant of the error_correction_syndrome pattern using data[3] -> data[5]. Let me analyze this:

1. The original code uses data[0], data[1], data[2] for encoding
2. The variant should use data[3] -> data[5] instead (so data[3], data[4], data[5])
3. The register should be expanded - so data[5] means we need at least 6 qubits (indices 0-5)
4. Additional qubits (data[0], data[1], data[2]) are left in ground state |0>

Let me trace through the circuit:

1. Start with |000000>|00> (6 data qubits, 2 syndrome qubits)
2. X(data[3]): |000100>|00>
3. CNOT(data[3], data[4]): |000110>|00>
4. CNOT(data[3], data[5]): |000111>|00>
5. X(data[4]): |000101>|00> (introducing error)
6. Syndrome extraction:
   - CNOT(data[3], syndrome[0]): |000101>|10> (data[3]=1, so syndrome[0] flips)
   - CNOT(data[4], syndrome[0]): |000101>|00> (data[4]=0, so syndrome[0] flips back)
   
Wait, let me reconsider. After X(data[4]):
- data[3] = 1
- data[4] = 0 (was 1, flipped by X)
- data[5] = 1

So syndrome[0] = data[3] XOR data[4] = 1 XOR 0 = 1
   syndrome[1] = data[4] XOR data[5] = 0 XOR 1 = 1

Let me trace more carefully:

1. Initial: |000000>|00>
2. X(data[3]): |000100>|00>
3. CNOT(data[3], data[4]): data[3]=1 controls data[4], so data[4] flips: |000110>|00>
4. CNOT(data[3], data[5]): data[3]=1 controls data[5], so data[5] flips: |000111>|00>
5. X(data[4]): flips data[4]: |000101>|00>

Now syndrome extraction:
6. CNOT(data[3], syndrome[0]): data[3]=1, so syndrome[0] flips: |000101>|10>
7. CNOT(data[4], syndrome[0]): data[4]=0, so syndrome[0] doesn't flip: |000101>|10>
8. CNOT(data[4], syndrome[1]): data[4]=0, so syndrome[1] doesn't flip: |000101>|10>
9. CNOT(data[5], syndrome[1]): data[5]=1, so syndrome[1] flips: |000101>|11>

So the syndrome measurement will give |11> with probability 1.0, which matches the predicted output.

Now let me write concise reasoning:

## Reasoning
1. Goal: Implement 3-qubit bit-flip code syndrome detection using qubits data[3-5] (expanded register) to identify a bit-flip error on data[4].

2. Qubits: 6 data qubits (data[0-5]) + 2 syndrome qubits; syndrome[0] and syndrome[1] are measured.

3. State evolution:
   - Initial: |000000>|00>
   - X(data[3]): |000100>|00>
   - CNOT(data[3], data[4]): |000110>|00>
   - CNOT(data[3], data[5]): |000111>|00> (encoded logical |1>)
   - X(data[4]): |000101>|00> (error introduced)
   - CNOT(data[3], syndrome[0]): |000101>|10>
   - CNOT(data[4], syndrome[0]): |000101>|10> (data[4]=0, no change)
   - CNOT(data[4], syndrome[1]): |000101>|10> (data[4]=0, no change)
   - CNOT(data[5], syndrome[1]): |000101>|11>

4. Expected probabilities: Syndrome |11> indicates parity mismatches on both checks, uniquely identifying the error on data[4]. Measurement yields {|11>: 1.0}.

Wait, I made an error. Let me recheck step 7 and 8:

After X(data[4]):
- data[3] = 1
- data[4] = 0 (was 1, now

## isqTrain/3503

- task_id: `isqTrain/3503`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `interference`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `4345`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```
import std;

qbit q[3];
qbit anc[1];

procedure main() {
    X(anc[0]);
    H(anc[0]);

    H(q[0]); H(q[1]); H(q[2]);

    CNOT(q[1], anc[0]);

    H(q[0]); H(q[1]); H(q[2]);

    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The objective is to analyze the given isQ quantum program, track the quantum state evolution step-by-step, and predict the output probability distribution for the measured qubits.

2.  **Analyze the Circuit**:
    *   Initial state: $|000\rangle_q \otimes |0\rangle_{anc} = |0000\rangle$ (q[0], q[1], q[2], anc[0])
    *   `X(anc[0])`: anc becomes $|1\rangle$.
    *   `H(anc[0])`: anc becomes $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   State so far: $(|000\rangle_q) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_{anc}$
    *   `H(q[0]); H(q[1]); H(q[2])`: Apply H to all q qubits.
        $|000\rangle_q \xrightarrow{H^{\otimes 3}} \frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x\rangle_q$
    *   State before CNOT: $\frac{1}{\sqrt{8}} \sum_x |x\rangle_q \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_{anc}$
    *   `CNOT(q[1], anc[0])`:
        Control: q[1], Target: anc[0].
        Since anc[0] is in $|-\rangle$, this acts as a phase kickback onto q[1].
        $CNOT_{q[1], anc} (|x_1\rangle \otimes |-\rangle) = (-1)^{x_1} |x_1\rangle \otimes |-\rangle$.
        Therefore, if q[1] is 1, the state gets a negative sign.
    *   State after CNOT: $\frac{1}{\sqrt{8}} \sum_x (-1)^{x_1} |x\rangle_q \otimes |-\rangle_{anc}$
        Let's write it out explicitly for the q qubits:
        $\frac{1}{2\sqrt{2}} \sum_{x_0, x_1, x_2 \in \{0,1\}} (-1)^{x_1} |x_0, x_1, x_2\rangle_q$
        Notice that this state is $H \otimes Z \otimes H |000\rangle_q$ (ignoring global phase or tensor product order, specifically: H on q[0], H on q[2], and Z on q[1]).
        Wait, let's check:
        $H|0\rangle = |+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}$
        $Z H|0\rangle = |-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$
        So the state is $|+\rangle \otimes |-\rangle \otimes |+\rangle$.
    *   `H(q[0]); H(q[1]); H(q[2])`:
        Apply H again to all q qubits.
        $H |+\rangle = |0\rangle$
        $H |-\rangle = |1\rangle$
        So the final state of q qubits is $|0\rangle \otimes |1\rangle \otimes |0\rangle = |010\rangle_q$.
    *   `M(q[0]); M(q[1]); M(q[2])`:
        Measure q qubits.
        The outcome will deterministically be $|010\rangle$ (or '010' in binary, which is q[0]=0, q[1]=1, q[2]=0).
        Wait, the order of measurement bitstring in isQ `--probs` output: earlier measured qubit = higher bit. So q[0] is the highest bit, q[1] is the middle, q[2] is the lowest.
        So $q_0 q_1 q_2$ = 010.
        Value of bitstring: 2.

3.  **Format the Output**:
    *   No isQ code blocks.
    *   Start with "## Circuit Analysis".
    *   Step-by-step evolution using Dirac notation.
    *   Conclude with the predicted probability distribution.

4.  **Drafting the reasoning**:
    *   Initial: $|000\rangle_q|0

### Reference answer

{'predicted_probs': {'010': 1.0}, 'explanation': 'The output is |010> with probability 1.0'}

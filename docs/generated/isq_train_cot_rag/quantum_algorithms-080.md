# ISQ training COT RAG corpus: quantum_algorithms shard 80

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4522

- task_id: `isqTrain/4522`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `interference`, `multi_controlled_logic`, `ancilla_usage`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `4779`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

oracle Uf(3,1) = [0,0,0,0,0,0,1,0];

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

qbit q[3];
qbit anc;

procedure main() {
    
    X(q[0]); H(q[1]); H(q[2]);  // replaced H with X
    
    X(anc);
    H(anc);
    
    Uf(q[2], q[1], q[0], anc);
    H(q[0]); H(q[1]); H(q[2]);
    U0(q[2], q[1], q[0]);
    H(q[0]); H(q[1]); H(q[2]);
    
    Uf(q[2], q[1], q[0], anc);
    H(q[0]); H(q[1]); H(q[2]);
    U0(q[2], q[1], q[0]);
    H(q[0]); H(q[1]); H(q[2]);
    
    H(anc); X(anc);
    
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

The user wants an analysis of an isQ quantum program.
The program applies a Grover's algorithm circuit to a 3-qubit register `q` and one ancillary qubit `anc`.
Wait, it applies Grover iterations twice. Let's trace it.
Oracle `Uf(3,1) = [0,0,0,0,0,0,1,0];` applies a phase of -1 to the state |110> of the input qubits, and flips the ancilla.
Wait, let's map the oracle.
`Uf` is applied to `q[2], q[1], q[0], anc`.
The index in `Uf` array is for the states of `q[2]q[1]q[0]`.
Array `[0,0,0,0,0,0,1,0]` means that the 6th element is 1. Since standard isQ `oracle` sets the element to 1 (or -1 depending on definition, but usually it's standard truth table: if index is 1, apply X to ancilla).
Wait, if `Uf` flips the ancilla for |110>, since ancilla is in |-> state, it applies a phase of -1 to |110> of the main qubits.
Let's check the initial state of `q`:
`X(q[0])` makes q[0] = |1>.
`H(q[1])` makes q[1] = |+>.
`H(q[2])` makes q[2] = |+>.
So the initial state of `q` is |1> (+) (+) = 1/2 (|100> + |101> + |110> + |111>). Wait! No, the order of qubits in tensor product: q[2] is the highest bit.
Let's write the states in binary order: q[2]q[1]q[0].
q[2] is in |+>, q[1] is in |+>, q[0] is in |1>.
So the state is 1/2(|--1>) = 1/2(|001> + |011> + |101> + |111>) -- wait.
Let's be careful.
q[2] = |+> = 1/sqrt(2) (|0> + |1>)
q[1] = |+> = 1/sqrt(2) (|0> + |1>)
q[0] = |1>
The state of `q` is |q[2]> x |q[1]> x |q[0]> = 1/2 ( |000> + |010> + |100> + |110> ) ? No, if q[0]=|1>, the last bit is 1.
Let's list all combinations of q[2], q[1], q[0]:
q[2]=0, q[1]=0, q[0]=1 => |001>
q[2]=0, q[1]=1, q[0]=1 => |011>
q[2]=1, q[1]=0, q[0]=1 => |101>
q[2]=1, q[1]=1, q[0]=1 => |111>
Wait! The expected outcome says `|011>` has probability 0.5625, and the others (including |001>, |101>, |111>) have probability 0.0625.
Wait, let's look at the oracle: `Uf(3,1) = [0,0,0,0,0,0,1,0]`.
The target state of the oracle (where the value is 1) corresponds to index 6, which is binary 110.
So the marked state is |110>.
Initial state: 1/2 ( |001> + |011> + |101> + |111> ). Wait, does Grover's algorithm search in a subspace?
Yes, it searches in the span of {|001>, |011>, |101>, |111>}.
Wait, Grover's diffusion operator is `H^{otimes 3} U_0 H^{otimes 3}`, where U_0 is a diagonal matrix with 1 on |000> and -1 elsewhere. So it reflects around the mean of the uniform superposition of all 8 states?
Wait, if the initial state has zero amplitude for |000>, |010>, |100>, |110>, the diffusion operator `H U_0 H` acts on the whole space.
Let's trace `H^{otimes 3} U_0 H^{otimes 3}` on |psi>.
U_0 is defined as:
[1, 0, 0, 0,

### Reference answer

{'predicted_probs': {'000': 0.0625, '001': 0.0625, '010': 0.0625, '011': 0.5625, '100': 0.0625, '101': 0.0625, '110': 0.0625, '111': 0.0625}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.0625, P(|001>) = 0.0625, P(|010>) = 0.0625, P(|011>) = 0.5625, P(|100>) = 0.0625, P(|101>) = 0.0625, P(|110>) = 0.0625, P(|111>) = 0.0625.'}

## isqTrain/3801

- task_id: `isqTrain/3801`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `297`

### Prompt

Help me write isQ code that 4-bit Bernstein-Vazirani to find secret s=0011. Use oracle keyword, for loops for Hadamard. Measure all 5 qubits.

### Chain-of-thought reasoning

Step 1: Understand the Goal
The task is to generate a step-by-step reasoning section for the provided isQ code that implements the Bernstein-Vazirani algorithm to find the secret string `s = 0011`.

Step 2: Analyze the isQ code
- Imports `std`.
- Defines an oracle `f(4, 1)` with the truth table mapping for `s = 0011`. The truth table is `[0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]`. Wait, the prompt says `s=0011`, but the oracle array is `[0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]`.
Let's double check. For `s = 0011`, $f(x) = x \cdot s \pmod 2 = x_0 s_0 \oplus x_1 s_1 \oplus x_2 s_2 \oplus x_3 s_3$. Assuming q[0] is $x_3$, q[1] is $x_2$, q[2] is $x_1$, q[3] is $x_0$? Or maybe little endian. The standard isQ array is enumerated as $x = 0, 1, \dots, 15$. If $s=0011$, $x \cdot s = (x_1 \oplus x_0)$. So $f(x) = 0$ for $x \in \{0, 3, 4, 7, 8, 11, 12, 15\}$ and $f(x) = 1$ for $x \in \{1, 2, 5, 6, 9, 10, 13, 14\}$. The array indices where value is 1 are 1, 2, 5, 6, 9, 10, 13, 14. Let's check the provided array: `[0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]`. Yes, exactly!
- `qbit q[5]`
- `X(q[4])`, `H(q[4])` puts qubit 4 into $|-\rangle$.
- `for i in 0:4` applies H to q[0], q[1], q[2], q[3], q[4]. Wait, the prompt says "Hadamard on inputs" then "Oracle" then "Hadamard" again `for i in 0:4`. Let's look at the code:

Actually, `0:4` means `0, 1, 2, 3` (exclusive end, typical for isQ). Wait! Is it 0 to 4 exclusive? Let's check. If it's `0:4`, it loops `0, 1, 2, 3`. The code applies H to `q[4]` initially, then `for i in 0:4` applies H to `q[0]...q[3]`. Then after oracle, applies H to `q[0]...q[3]`. Wait, does it apply H to `q[4]` again? No, `0:4` in isQ typically means `[0, 1, 2, 3]`. Let's assume it applies to 0,1,2,3.
Wait, The predicted output `{|00110>: 0.5, |00111>: 0.5}`.
Wait, the output string is 5 bits, meaning 5 qubits are measured: q[0], q[1], q[2], q[3], q[4].
Wait, if `s=0011` is the secret, the top 4 qubits should measure exactly `0011`. That would be `|00110>` and `|00111>` because q[4] is in $|-\rangle$ and had H applied to it?
Let's trace q[4].
Initially `|0

## isqTrain/940

- task_id: `isqTrain/940`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1543`

### Prompt

Implement a quantum circuit in isQ: implements the reversible_logic pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a reversible_logic pattern using a controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) gate with an explicit identity X-X pair to demonstrate gate cancellation awareness.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Initial: |000⟩
   - X(q[0]), X(q[1]) → |110⟩ (q[0]=|1⟩, q[1]=|1⟩, q[2]=|0⟩)
   - ctrl swap_gate(q[0], q[1], q[2]): Since q[0]=|1⟩, swap (three-CNOT decomposition)(q[1],q[2]) fires → |101⟩
   - X(q[0]) → |001⟩
   - X(q[0]) → |101⟩ (X-X identity pair cancels, demonstrating gate cancellation)
4. **Result**: Final state |101⟩ yields measurement probability {|101⟩: 1.0}.

## isqTrain/2872

- task_id: `isqTrain/2872`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5734`

### Prompt

Code this in isQ: demonstrating phase kickback with controlled-S. Set the target qubit to |1>, apply Hadamard to the control, apply controlled-S, then Hadamard again. Measure both qubits.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `procedure main()` as entry point.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
- Goal: Demonstrate phase kickback by applying a controlled-S gate where the target is in an eigenstate of S.
- Qubits: 2 (`q[0]` control, `q[1]` target). Both measured.
- State evolution:
  1. Initial state: |00⟩
  2. `X(q[1])`: |0⟩⊗|1⟩
  3. `H(q[0])`: 1/√2 (|0⟩ + |1⟩) ⊗ |1⟩ = 1/√2 (|01⟩ + |11⟩)
  4. `ctrl S(q[0], q[1])`: Target `q[1]` is in eigenstate |1⟩ of S (eigenvalue i). Phase i kicks back to control: 1/√2 (|01⟩ + i|11⟩)
  5. `H(q[0])`: H acts on control: 1/2 ((1+i)|01⟩ + (1-i)|11⟩)
- Probabilities follow from state magnitudes: P(|01⟩) = |(1+i)/2|² = 0.5, P(|11⟩) = |(1-i)/2|² = 0.5.

## isqTrain/74

- task_id: `isqTrain/74`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `2125`

### Prompt

实现以下量子计算任务（使用isQ）：implements the bell_state_preparation pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has 2 qubits q[0] and q[1].

1. Initial state: |00⟩

2. H(q[0]): Creates superposition on q[0]
   (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2

3. CNOT(q[0], q[1]): Creates Bell state
   (|00⟩ + |11⟩)/√2

4. Z(q[0]): Apply Z to q[0]
   (|00⟩ - |11⟩)/√2

5. X(q[0]): Apply X to q[0]
   (|10⟩ - |01⟩)/√2

6. CNOT(q[0], q[1]): 
   Need to trace this carefully.
   CNOT with q[0] as control, q[1] as target.
   
   |10⟩ → |11⟩ (control=1, flip target)
   |01⟩ → |00⟩ (control=0, don't flip target)
   
   So we get: (|11⟩ - |00⟩)/√2

7. H(q[0]):
   |11⟩ → (|01⟩ + |11⟩)/√2
   |00⟩ → (|00⟩ + |10⟩)/√2
   
   So: (|01⟩ + |11⟩ - |00⟩ - |10⟩)/2

Wait, let me recalculate more carefully.

After step 5: (|10⟩ - |01⟩)/√2

Step 6: CNOT(q[0], q[1])
|10⟩: q[0]=1, so flip q[1]: |10⟩ → |11⟩
|01⟩: q[0]=0, so don't flip q[1]: |01⟩ → |01⟩

Result: (|11⟩ - |01⟩)/√2

Step 7: H(q[0]):
|11⟩: H on first qubit → (|01⟩ - |11⟩)/√2
|01⟩: H on first qubit → (|01⟩ + |11⟩)/√2

Wait, H|0⟩ = (|0⟩ + |1⟩)/√2, H|1⟩ = (|0⟩ - |1⟩)/√2

|11⟩ = |1⟩⊗|1⟩
H on first: (|0⟩ - |1⟩)/√2 ⊗ |1⟩ = (|01⟩ - |11⟩)/√2

|01⟩ = |0⟩⊗|1⟩
H on first: (|0⟩ + |1⟩)/√2 ⊗ |1⟩ = (|01⟩ + |11⟩)/√2

Final: (|01⟩ - |11⟩)/√2 - (|01⟩ + |11⟩)/√2)/√2
     = ((|01⟩ - |11⟩) - (|01⟩ + |11⟩))/2
     = (|01⟩ - |11⟩ - |01⟩ - |11⟩)/2
     = -2|11⟩/2
     = -|11⟩

So the final state is -|11⟩ (up to global phase, this is |11⟩).

Now measurements: M(q[1]) then M(q[0])

In isQ's --probs mode, "earlier measured qubit = higher bit". So q[1] is measured first, making it the higher bit, and q[0] is measured second, making it the lower bit.

So the bitstring index is: q[1] q[0]

If state is |11⟩, then q[0]=1 and q[1]=1.

The bitstring would be q[1]=1 (higher bit), q[0]=1 (lower bit) = binary 11 = 3.

But The predicted output {|11>: 1.0}, where |11> means index 3.

Actually, let me reconsider the notation. When they say {|11>: 1.0}, this means the probability of getting measurement outcome corresponding to bitstring "11" is 1.0.

With the reversed measurement order M(q[1]); M(q[0]), q[1] is measured first (higher bit), q[0] is measured second (lower bit).

The quantum state is |q[0]=1, q[1]=1⟩ = |11⟩ in the computational basis.

When we measure, both qubits give 1. The bitstring with q[1] as higher bit and q[0] as lower bit is "11", which is index 3.

So {|11>: 1.0} means probability at index 3 is 1.0

## isqTrain/3648

- task_id: `isqTrain/3648`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `473`

### Prompt

实现以下量子计算任务（使用isQ）：the 3-qubit inverse Quantum Fourier Transform (QFT†) on input |111>. Use bit-reversal swaps first, then apply inverse rotation stages with negative angles. Measure all qubits.

### Chain-of-thought reasoning

Let me analyze this problem step by step.

The task is to implement the inverse Quantum Fourier Transform (QFT†) on the state |111>.

First, let me recall what QFT does and what QFT† does.

The QFT on 3 qubits transforms a computational basis state |j⟩ to:
QFT|j⟩ = (1/√8) Σ_k e^(2πijk/8) |k⟩

For |j⟩ = |111⟩ = |7⟩:
QFT|7⟩ = (1/√8) Σ_k e^(2πi·7·k/8) |k⟩

The inverse QFT (QFT†) transforms:
QFT†|j⟩ = (1/√8) Σ_k e^(-2πijk/8) |k⟩

Wait, let me think about this more carefully. The QFT† undoes the QFT. So if we apply QFT† to |111⟩ = |7⟩:

QFT†|7⟩ = (1/√8) Σ_k e^(-2πi·7·k/8) |k⟩

Let me compute this:
= (1/√8) [|0⟩ + e^(-14πi/8)|1⟩ + e^(-28πi/8)|2⟩ + e^(-42πi/8)|3⟩ + e^(-56πi/8)|4⟩ + e^(-70πi/8)|5⟩ + e^(-84πi/8)|6⟩ + e^(-98πi/8)|7⟩]

Simplifying the exponents mod 2πi:
- e^(-14πi/8) = e^(-7πi/4) = e^(πi/4)
- e^(-28πi/8) = e^(-7πi/2) = e^(πi/2)
- e^(-42πi/8) = e^(-21πi/4) = e^(3πi/4)
- e^(-56πi/8) = e^(-7πi) = -1 = e^(πi)
- e^(-70πi/8) = e^(-35πi/4) = e^(5πi/4)
- e^(-84πi/8) = e^(-21πi/2) = e^(3πi/2)
- e^(-98πi/8) = e^(-49πi/4) = e^(7πi/4)

So QFT†|7⟩ = (1/√8) [|0⟩ + e^(πi/4)|1⟩ + e^(πi/2)|2⟩ + e^(3πi/4)|3⟩ + e^(πi)|4⟩ + e^(5πi/4)|5⟩ + e^(3πi/2)|6⟩ + e^(7πi/4)|7⟩]

This is a uniform superposition with all amplitudes having magnitude 1/√8. So when measured, all 8 outcomes have equal probability of 1/8 = 0.125.

Now let me trace through the circuit:

Initial state: |000⟩
After X on all qubits: |111⟩

Now we apply QFT†. The standard QFT circuit applies:
1. H on q[0], then controlled rotations R_k on q[0] controlled by q[1], q[2]
2. H on q[1], then controlled rotations on q[1] controlled by q[2]
3. H on q[2]
4. Swap q[0] and q[2]

For QFT†, we reverse the order and use negative angles:
1. Swap q[0] and q[2]
2. H on q[2], then negative controlled rotations on q[2] controlled by q[1], q[0]
3. H on q[1], then negative controlled rotation on q[1] controlled by q[0]
4. H on q[0]

Analyzing the code:
1. First, swaps: CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]); - this swaps q[0] and q[2]
2. H(q[2])
3. ctrl Rz(-2π/4, q[2], q[1]) - controlled Rz(-π/2) on q[2] with q[1] as control
4. H(q[1])
5. ctrl Rz(-2π/8, q[2], q[0]) - controlled Rz(-π/4) on q[2] with q[0] as

## isqTrain/4018

- task_id: `isqTrain/4018`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4206`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```
import std;
// QAOA MaxCut p=1 on 4-node square graph
// gamma=0.785, beta=0.393
qbit q[4];

procedure main() {
    // Superposition
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // Cost unitary
    // Edge (0,1)
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    // Edge (1,2)
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[1], q[2]);
    // Edge (2,3)
    CNOT(q[2], q[3]);
    Rz(2.0 * 0.785, q[3]);
    CNOT(q[2], q[3]);
    // Edge (0,3)
    CNOT(q[0], q[3]);
    Rz(2.0 * 0.785, q[3]);
    CNOT(q[0], q[3]);
    // Mixer
    Rx(2.0 * 0.393, q[0]);
    // BUG: missing gate here
    Rx(2.0 * 0.393, q[2]);
    Rx(2.0 * 0.393, q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

**Bug:** The mixer unitary in QAOA must apply Rx(2β) to every qubit. The buggy code applies Rx to q[0], q[2], and q[3], but is missing `Rx(2.0 * 0.393, q[1])`.

**Fix:** Insert `Rx(2.0 * 0.393, q[1]);` after the Rx on q[0], so all four qubits receive the mixer rotation.

**State evolution (corrected):**
1. **Init:** |0000⟩
2. **Hadamards:** |++++⟩ = equal superposition over all 16 basis states
3. **Cost unitary:** Each CNOT-Rz(2γ)-CNOT on edge (i,j) adds phase e^{-iγ} for states where qᵢ≠qⱼ and e^{+iγ} otherwise. For the square graph (4 edges), this encodes the MaxCut objective via accumulated phases: states with 2 or 4 cut edges get favorable phases.
4. **Mixer:** Rx(2β=0.786) on all four qubits interferes amplitudes, reinforcing balanced-cut states.
5. **Measurement:** Yields ~12.5% each on |0011⟩, |0101⟩, |0110⟩, |1001⟩, |1010⟩, |1100⟩ (optimal/balanced cuts), with slightly boosted probabilities on |0000⟩ and |1111⟩ (~12.52%) due to the chosen γ,β parameters.

## isqTrain/1168

- task_id: `isqTrain/1168`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2701`

### Prompt

Create an isQ quantum circuit that implements the iqp_circuit pattern using an alternative gate decomposition (CZ -> H CNOT H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the given isQ program that implements an IQP circuit pattern using the CZ -> H CNOT H decomposition.

Let me analyze the circuit:

1. Three qubits q[0], q[1], q[2]
2. First Hadamard layer: H on all 3 qubits
3. Diagonal gates: T on all 3 qubits
4. Two CZ gates decomposed as H-CNOT-H:
   - CZ(q[0], q[1]): H(q[1]), CNOT(q[0], q[1]), H(q[1])
   - CZ(q[1], q[2]): H(q[2]), CNOT(q[1], q[2]), H(q[2])
5. Second Hadamard layer: H on all 3 qubits
6. Measure all qubits

Let me trace the state evolution:

Initial: |000⟩

After H on all: 1/√8 (|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

After T on all: Each qubit gets T applied. T|0⟩ = |0⟩, T|1⟩ = e^(iπ/4)|1⟩
So for 3 qubits with T on each: 1/√8 (|000⟩ + e^(iπ/4)|001⟩ + e^(iπ/4)|010⟩ + e^(iπ/2)|011⟩ + e^(iπ/4)|100⟩ + e^(iπ/2)|101⟩ + e^(iπ/2)|110⟩ + e^(i3π/4)|111⟩)

Wait, let me be more careful. T applies a phase of e^(iπ/4) to |1⟩ state. So T⊗T⊗T:
- |000⟩ → |000⟩
- |001⟩ → e^(iπ/4)|001⟩
- |010⟩ → e^(iπ/4)|010⟩
- |011⟩ → e^(iπ/2)|011⟩
- |100⟩ → e^(iπ/4)|100⟩
- |101⟩ → e^(iπ/2)|101⟩
- |110⟩ → e^(iπ/2)|110⟩
- |111⟩ → e^(i3π/4)|111⟩

Now the CZ gates. CZ(q[0], q[1]) applies Z to q[1] when q[0]=1. This adds a phase of -1 when both q[0]=1 and q[1]=1.
CZ(q[1], q[2]) applies Z to q[2] when q[1]=1. This adds a phase of -1 when both q[1]=1 and q[2]=1.

So the combined effect of both CZ gates:
- |000⟩ → |000⟩ (phase 1)
- |001⟩ → |001⟩ (phase 1, q[1]=0 so no CZ effect)
- |010⟩ → -|010⟩ (CZ(q[1],q[2]) gives -1 since q[1]=1, q[2]=0... wait no, CZ applies Z to target when control is |1⟩, so it phases when both are in a specific configuration)

Let me reconsider. CZ(a, b) applies Z to qubit b when qubit a is |1⟩. In computational basis, this means it adds a phase of -1 only when both a AND b are |1⟩.

So CZ(q[0], q[1]): phase -1 when q[0]=1 AND q[1]=1
CZ(q[1], q[2]): phase -1 when q[1]=1 AND q[2]=1

Combined phase for each basis state:
- |000⟩: phase 1 (neither condition met)
- |001⟩: phase 1 (q[1]=0, neither met)
- |010⟩: phase -1 (q[1]=1, q[2]=0... CZ(q[1],q[2]) checks q[1]=1 AND q[2]=1, but q[2]=0, so no. CZ(q[0],q[1]) checks q[0]=0, so no. Phase is 1)

Wait, let me redo this:
- |q[0]q[1]q[2]⟩
- CZ(q[0], q[1]): phase -1 if q[0]=1 AND q[1]=1
- CZ(q[1], q[2]): phase -1 if q[1]=1 AND q[2]=1

|000⟩: 0&0=0, 0

## isqTrain/3523

- task_id: `isqTrain/3523`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `interference`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `186`

### Prompt

Predict the output probabilities of the following quantum circuit:

```
import std;

qbit q[3];
qbit anc[1];

procedure main() {
    X(anc[0]);
    H(anc[0]);

    H(q[0]); H(q[1]); H(q[2]);

    CNOT(q[0], anc[0]);
    CNOT(q[2], anc[0]);

    H(q[0]); H(q[1]); H(q[2]);

    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the output probability distribution of the given isQ program.
    *   Given: An isQ program creating 3 qubits `q[3]` and 1 ancilla `anc[1]`. The gates applied are `X(anc[0])`, `H(anc[0])`, `H` on all `q`, `CNOT(q[0], anc[0])`, `CNOT(q[2], anc[0])`, and `H` on all `q`. Finally, `q` is measured.
    *   Output format: "## Circuit Analysis" followed by step-by-step reasoning, using Dirac notation. Max 15 lines. End with predicted probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: $|0000\rangle_{q_0 q_1 q_2 anc}$ (Assuming standard convention where measured qubits form the bitstring).
    *   `X(anc[0])`: $|0001\rangle$
    *   `H(anc[0])`: $|000\rangle \otimes |-\rangle = \frac{1}{\sqrt{2}} (|0000\rangle - |0001\rangle)$
    *   `H(q[0]) H(q[1]) H(q[2])`: $\frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x\rangle \otimes |-\rangle$
    *   `CNOT(q[0], anc[0])` and `CNOT(q[2], anc[0])`: These CNOTs flip the ancilla based on $q_0 \oplus q_2$.
    *   Let's trace the state: $\frac{1}{\sqrt{8}} \sum_x |x\rangle \otimes (|0 \oplus x_0 \oplus x_2\rangle - |1 \oplus x_0 \oplus x_2\rangle)$
    *   Notice that $|0 \oplus a\rangle - |1 \oplus a\rangle$ is $-|-\rangle$ if $a=0$ and $|+\rangle$ if $a=1$? Wait.
        *   If $a=0$: $|0\rangle - |1\rangle = |-\rangle$
        *   If $a=1$: $|1\rangle - |0\rangle = -(|0\rangle - |1\rangle) = -|-\rangle$.
        *   Wait, let's re-evaluate: $(|0 \oplus a\rangle - |1 \oplus a\rangle) = (-1)^a (|0\rangle - |1\rangle) = (-1)^a |-\rangle$.
    *   So, the ancilla state is $(-1)^{x_0 \oplus x_2} |-\rangle$.
    *   The combined state becomes $\frac{1}{\sqrt{8}} \sum_x (-1)^{x_0 \oplus x_2} |x\rangle \otimes |-\rangle$.
    *   `H(q[0]) H(q[1]) H(q[2])`: We apply Hadamard to the first three qubits.
    *   The effect of $H^{\otimes 3}$ on a state $\sum_x (-1)^{f(x)} |x\rangle$ where $f(x) = x_0 \oplus x_2$ (which is a linear boolean function).
    *   We know $H^{\otimes n} |x\rangle = \frac{1}{\sqrt{2^n}} \sum_y (-1)^{x \cdot y} |y\rangle$.
    *   So $H^{\otimes 3} \sum_x (-1)^{x_0 \oplus x_2} |x\rangle = H^{\otimes 3} \sum_x (-1)^{x \cdot 101} |x\rangle$.
    *   Since $H^{\otimes n} \sum_x (-1)^{x \cdot z} |x\rangle = |z\rangle$ (up to global phase/normalization), wait. Let's verify.
    *   $H^{\otimes n} |z\rangle = \frac{1}{\sqrt{2^n}} \sum_x (-1)^{x \cdot z} |x\rangle$. So applying $H^{\otimes n}$ again gives exactly $|z\rangle$.
    *   Here $z = 101$ (which corresponds to $q_0=1,

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'The output is |101> with probability 1.0'}

## isqExpand/algo/51

- task_id: `isqExpand/algo/51`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `grover`, `3qubit`, `multi_solution`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `2245`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[1]);
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. H on all 3 qubits: uniform superposition
2. First oracle block: X(q[0]); CCZ; X(q[0]) — marks |011>
   When q[0]=0 (flipped to 1 by X), q[1]=1, q[2]=1: marks |011>
3. Second oracle block: X(q[1]); CCZ; X(q[1]) — marks |101>
   When q[0]=1, q[1]=0 (flipped to 1 by X), q[2]=1: marks |101>
4. Diffusion: H-X-CCZ-X-H on all 3 qubits

This is Grover with M=2 solutions out of N=8.
theta = arcsin(sqrt(M/N)) = arcsin(sqrt(2/8)) = arcsin(1/2) = pi/6
After 1 iteration: P_total = sin^2((2*1+1)*pi/6) = sin^2(pi/2) = 1.0

The probability concentrates entirely on the two marked states, each getting 0.5.

### Reference answer

{'predicted_probs': {'000': 0.0, '001': 0.0, '010': 0.0, '011': 0.5, '100': 0.0, '101': 0.5, '110': 0.0, '111': 0.0}, 'explanation': 'This is one Grover iteration on 3 qubits with two marked states. The first oracle block: X(q[0]); CCZ; X(q[0]) marks |011> (q[0]=0 flipped to 1, q[1]=1, q[2]=1). The second oracle block: X(q[1]); CCZ; X(q[1]) marks |101> (q[0]=1, q[1]=0 flipped to 1, q[2]=1). With M=2 solutions out of N=8, theta=arcsin(sqrt(2/8))=pi/6. After 1 iteration: P(marked)=sin^2(3*pi/6)=sin^2(pi/2)=1. Each marked state gets 0.5, all others get 0.'}

# ISQ training COT RAG corpus: quantum_algorithms shard 181

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3793

- task_id: `isqTrain/3793`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3169`

### Prompt

Write isQ code for the following quantum task: Deutsch-Jozsa for a 3-input balanced oracle with truth table [0, 0, 0, 0, 1, 1, 1, 1]. Use for loops for Hadamard application. Measure all 4 qubits.

### Chain-of-thought reasoning

Let me trace through the Deutsch-Jozsa algorithm for a 3-input balanced oracle with truth table [0, 0, 0, 0, 1, 1, 1, 1].

1. **Goal**: Implement Deutsch-Jozsa to determine if a 3-bit function is constant or balanced.

2. **Qubits**: 4 qubits needed - q[0], q[1], q[2] (input) and q[3] (output). All 4 are measured.

3. **State evolution**:

Initial state: |0000>

After X(q[3]): |0001>

After H(q[3]): |000-> = |000>(|0>-|1>)/√2

After Hadamard on all 4 qubits (q[0], q[1], q[2], q[3]):
- The input qubits become superposition over all 8 basis states
- q[3] goes from |-> to |-> (H|-> = -|-> actually, let me recalculate)

Wait, let me be more careful.

H|0> = |+> = (|0>+|1>)/√2
H|1> = |-> = (|0>-|1>)/√2

So after X(q[3]): |0001>
After H(q[3]): |000>|-> = |0000>/√2 - |0001>/√2

After H on q[0], q[1], q[2], q[3]:
- H⊗3 on |000> = sum over all |x>/√(8) for x in {000,001,...,111}
- H on |-> = -|->

So the state is: -(1/√8) Σ_x |x>|-> where the sum is over all 8 possible x values.

The oracle f maps |x>|y> -> |x>|y⊕f(x)>

Since the ancilla is in |-> = (|0>-|1>)/√2, we have:
|x>|-> -> (-1)^f(x)|x>|->

So after the oracle:
State = -(1/√8) Σ_x (-1)^f(x)|x>|->

For f(x) = [0,0,0,0,1,1,1,1]:
- f(000)=0, f(001)=0, f(010)=0, f(011)=0
- f(100)=1, f(101)=1, f(110)=1, f(111)=1

So (-1)^f(x): [+1,+1,+1,+1,-1,-1,-1,-1]

State after oracle = -(1/√8)(|000>+|001>+|010>+|011>-|100>-|101>-|110>-|111>)|->

Now apply H on q[0], q[1], q[2] (the first 3 qubits):

The Hadamard transform on the input register:
H⊗3 applied to (1/√8) Σ_x (-1)^f(x)|x>

The key insight: H⊗3|x> = (1/√8) Σ_z (-1)^{x·z}|z>

So (1/√8) Σ_x (-1)^f(x) H⊗3|x> = (1/8) Σ_z [Σ_x (-1)^f(x)(-1)^{x·z}] |z>

For z = 000: Σ_x (-1)^f(x)(-1)^0 = 1+1+1+1-1-1-1-1 = 0
For z = 100: Σ_x (-1)^f(x)(-1)^{x·100} = Σ_x (-1)^{f(x)+x_0}

x=000: (-1)^{0+0}=1
x=001: (-1)^{0+0}=1
x=010: (-1)^{0+0}=1
x=011: (-1)^{0+0}=1
x=100: (-1)^{1+1}=1
x=101: (-1)^{1+1}=1
x=110: (-1)^{1+1}=1
x=111: (-1)^{1+1}=1

Sum = 8, so amplitude for |100> = 8/8 = 1

For z = 010: Σ_x (-1)^{f(x)+x_1}
x=000: (-1)^{0+0}=1
x=001: (-1)^{0+0}=1
x=010: (-1)^{0+1}=-1
x=011: (-1)^{0+1

## isqTrain/3785

- task_id: `isqTrain/3785`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2634`

### Prompt

实现以下量子计算任务（使用isQ）：the Deutsch-Jozsa algorithm for a 2-input balanced oracle with truth table [1, 0, 0, 1]. Use the oracle keyword, prepare output in |-> state, apply Hadamard-oracle-Hadamard, measure input qubits. Result should be non-zero (balanced).

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a Deutsch-Jozsa algorithm implementation in isQ.

The problem is:
- 2-input balanced oracle with truth table [1, 0, 0, 1]
- This is the Deutsch-Jozsa algorithm
- Output qubit prepared in |->
- Apply H-oracle-H on input qubits
- Measure input qubits to determine if oracle is balanced or constant
- For a balanced oracle, the result should be non-zero

Let me trace the state evolution:

1. Initial state: |000>

2. Apply X to q[2] (output): |001>

3. Apply H to q[2]: |0>(|0>-|1>)/√2 = (|00>-|01>)/√2

4. Apply H to q[0] and q[1]: 
   Now we have (1/2)(|00>+|01>+|10>+|11>)(|0>-|1>)/√2
   = (1/2√2) Σ_{x∈{00,01,10,11}} |x>(|0>-|1>)

5. Apply oracle f: This maps |x>|y> → |x>|y ⊕ f(x)>
   For the truth table [1, 0, 0, 1], this means:
   - f(00) = 1, f(01) = 0, f(10) = 0, f(11) = 1
   
   After oracle, we get:
   (1/2√2) Σ_x |x>(|0⊕f(x)> - |1⊕f(x)>)/...
   
   Actually, let me be more careful. The oracle U_f maps |x>|y> → |x>|y ⊕ f(x)>.
   
   For the state (|0>-|1>)/√2, applying U_f gives:
   If f(x)=0: |0⊕0>-|1⊕0> = |0>-|1> (unchanged)
   If f(x)=1: |0⊕1>-|1⊕1> = |1>-|0> = -(|0>-|1>) (phase flip)
   
   So the output qubit picks up a phase of (-1)^f(x).
   
   State after oracle:
   (1/2√2)[|00>(-1)^1(|0>-|1>) + |01>(-1)^0(|0>-|1>) + |10>(-1)^0(|0>-|1>) + |11>(-1)^1(|0>-|1>)]
   = (1/2√2)(-|00>+|01>+|10>-|11>)(|0>-|1>)

6. Apply H to q[0] and q[1]:
   H|0> = (|0>+|1>)/√2
   H|1> = (|0>-|1>)/√2
   
   H⊗2|-00> = -H⊗2|00> = -(1/√2)(|0>+|1>)⊗(1/√2)(|0>+|1>) = -(1/2)(|00>+|01>+|10>+|11>)
   H⊗2|01> = (1/2)(|00>-|01>+|10>-|11>)
   H⊗2|10> = (1/2)(|00>+|01>-|10>-|11>)
   H⊗2|-11> = -(1/2)(|00>-|01>-|10>+|11>)
   
   Sum with coefficients:
   -(1/2)(|00>+|01>+|10>+|11>) + (1/2)(|00>-|01>+|10>-|11>) + (1/2)(|00>+|01>-|10>-|11>) - (1/2)(|00>-|01>-|10>+|11>)
   
   Let me compute coefficient for each basis state:
   |00>: -(1/2) + (1/2) + (1/2) - (1/2) = 0
   |01>: -(1/2) - (1/2) + (1/2) + (1/2) = 0
   |10>: -(1/2) + (1/2) - (1/2) + (1/2) = 0
   |11>: -(1/2) - (1/2) - (1/2) - (1/2) = -2
   Hmm, wait, that doesn't seem right. Let me redo this.
   
   Actually, the standard result for Deutsch-Jozsa is that for a balanced function, all input qubits

## isqTrain/2999

- task_id: `isqTrain/2999`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2870`

### Prompt

Fix the bug in this quantum program:

```isq
import std;
qbit q[2];
// Bell state with S phase
procedure main() {
    H(q[0]);
    CNOT(q[1], q[0]);
    S(q[1]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug**: The `CNOT` gate in the buggy code uses `q[1]` as the control and `q[0]` as the target. Since the Hadamard gate creates superposition on `q[0]`, `q[0]` must be the control qubit to properly entangle the pair.
2. **The fix**: Change `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])` so that the state of `q[0]` controls the bit flip on `q[1]`.
3. **State evolution**: 
   - Start: |00>
   - `H(q[0])`: 1/√2 (|00> + |10>)
   - `CNOT(q[0], q[1])`: 1/√2 (|00> + |11>) (Bell state)
   - `S(q[1])`: 1/√2 (|00> + i|11>)
   - Measurement probabilities remain {|00>: 0.5, |11>: 0.5}, confirming the fix.

## isqTrain/95

- task_id: `isqTrain/95`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5081`

### Prompt

Implement the following in isQ: implements the gate_decomposition pattern with modified rotation parameters (pi2_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit implements a gate decomposition pattern with modified rotation parameters (pi/2 to pi/4 adjustments). This looks like a QAOA-style circuit with cost and mixing unitaries.

Let me trace through the state evolution:

1. Initial state: |00⟩

2. After H(q[0]) and H(q[1]):
   |00⟩ → |+⟩|+⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

3. Cost Unitary with CNOT-Rz(pi/4)-CNOT (Rz(pi/2) = 2*gamma where gamma = pi/4):
   The CNOT-Rz(θ)-CNOT on q[0],q[1] applies Rz(θ) when both qubits are in |1⟩ state (controlled-Rz).
   
   Actually, let me think more carefully. CNOT(q[0], q[1]) followed by Rz(θ, q[1]) followed by CNOT(q[0], q[1]):
   
   This is equivalent to controlled-Rz(θ) where q[0] is control and q[1] is target. Wait, no.
   
   CNOT(q[0], q[1]) flips q[1] when q[0] is |1⟩.
   Then Rz(θ) on q[1].
   Then CNOT(q[0], q[1]) again.
   
   Let me work this out with matrix notation. Actually, let me think about what this does in the computational basis.
   
   If q[0] = |0⟩: CNOT does nothing to q[1], Rz(θ) applies to q[1], then CNOT does nothing. So Rz(θ) is applied to q[1].
   
   If q[0] = |1⟩: CNOT flips q[1], then Rz(θ) applies to the flipped q[1], then CNOT flips back.
   
   So when q[0] = |1⟩, the Rz(θ) is applied to the flipped q[1]. But since Rz(θ) = diag(1, e^{iθ}), applying it to the flipped qubit... hmm, this is getting complex.
   
   Actually, the standard decomposition for ZZ interaction is CNOT-Rz(2γ)-CNOT which applies Rz(2γ) on the target controlled by the control. But here the Rz is just pi/4, so it's like a controlled-Rz(pi/4).
   
   Actually, let me reconsider. The circuit CNOT(q[0], q[1]), Rz(θ, q[1]), CNOT(q[0], q[1]):
   
   This applies e^{-iθZ/2} to q[1] when q[0] = |0⟩, and when q[0] = |1⟩, it also applies e^{-iθZ/2} to q[1] but in the flipped basis... 
   
   Hmm, let me just compute this properly. Let me use the fact that CNOT conjugation of Rz on target gives Rz on target still (since Z commutes with the X that CNOT applies).
   
   Wait, that's not right. CNOT(q[0], q[1]) applies X to q[1] when q[0] = |1⟩. Conjugating Rz(θ) by X on the same qubit: X Rz(θ) X = diag(e^{-iθ/2}, e^{iθ/2}) when viewed properly... 
   
   Actually, Rz(θ) = e^{-iθZ/2} and X Z X = -Z, so X Rz(θ) X = e^{iθZ/2} = Rz(-θ).
   
   So when q[0] = |1⟩, the effective operation on q[1] is Rz(-θ).
   When q[0] = |0⟩, the effective operation on q[1] is Rz(θ).
   
   This means the overall effect is:
   |00⟩ → e^{-iθ/2}|00⟩
   |01⟩ → e^{iθ/2}|01⟩
   |10⟩ → e^{iθ/2}|10⟩
   |11⟩ → e^{-iθ/2}|11⟩
   
   Wait, that's equivalent to applying Rz(θ) on q[1] and something else... Actually this is like a controlled-phase gate but not exactly.
   
   Let me redo this. For each computational basis state:
   
   |00⟩: CNOT does nothing, Rz(θ) on q[1] gives phase e^{-iθ/2} to |0

## isqTrain/808

- task_id: `isqTrain/808`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2817`

### Prompt

Implement the following in isQ: implements a variant of the quadratic_form pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Looking at this task, I need to write a reasoning section for an isQ program that implements a variant of the quadratic_form pattern using q[2] -> q[3].

The circuit should:
- qbit q[3] (3 qubits: q[0], q[1], q[2])
- H(q[0]) - puts q[0] in superposition
- CNOT(q[0], q[1]) - copies q[0] to q[1]
- M(q[1]) and M(q[2]) - measures q[1] and q[2]

The resulting probabilities should be {|00>: 0.5, |10>: 0.5}, meaning:
- q[1] and q[2] are measured
- q[1] follows q[0] (via CNOT), q[2] stays |0>

Wait, the task says "using q[2] -> q[3]" but the reference uses q[0], q[1], q[2]. Let me re-read...

The task says "variant of the quadratic_form pattern using q[2] -> q[3]" - this might mean the variant should use qubits q[2] and q[3], requiring a larger register.

Let me trace through The implementation:
1. Initial state: |000>
2. H(q[0]): (|000> + |100>) / sqrt(2)
3. CNOT(q[0], q[1]): (|000> + |110>) / sqrt(2)
4. Measure q[1] and q[2]:
   - q[1] is the first measured qubit (higher bit in bitstring)
   - q[2] is the second measured qubit (lower bit)
   
In state |000>: q[1]=0, q[2]=0 -> |00>
In state |110>: q[1]=1, q[2]=0 -> |10>

So probabilities: P(|00>) = 0.5, P(|10>) = 0.5 ✓

Now I need to create a reasoning for a variant that uses q[2] -> q[3]. This would need at least 4 qubits (q[0], q[1], q[2], q[3]).

For the variant, I could:
- Have a larger register (qbit q[4])
- Apply operations involving q[2] and q[3]
- Maybe: H(q[2]), CNOT(q[2], q[3]), then measure q[2] and q[3]

Let me write the reasoning for this:

## Reasoning
1. The circuit implements a quadratic form variant using q[2] and q[3], with an expanded 4-qubit register.
2. Four qubits are needed (qbit q[4]); q[2] and q[3] are measured.
3. State evolution:
   - Initial: |0000>
   - H(q[2]): (|0000> + |0010>) / sqrt(2)  [q[2] is the 3rd qubit, index 2]
   - CNOT(q[2], q[3]): (|0000> + |0011>) / sqrt(2)
4. Measurement probabilities: measuring q[2] (higher bit) and q[3] (lower bit):
   - |0000> contributes |00>, |0011> contributes |11>
   - P(|00>) = 0.5, P(|11>) = 0.5

Wait, but The resulting probabilities should be {|00>: 0.5, |10>: 0.5}, not {|00>: 0.5, |11>: 0.5}. So the variant must be different...

Let me re-read the task. It says "variant of the quadratic_form pattern using q[2] -> q[3]". The circuit should expected probabilities {|00>: 0.5, |10>: 0.5}. 

Hmm, maybe I'm overcomplicating this. The task is asking me to generate the reasoning, not modify the circuit. The implementation already achieves the predicted output.

Let me trace through The implementation again:
- qbit q[3]: q[0], q[1], q[2]
- H(q[0]): |000> → (|000> + |100>)/√2
- CNOT(q[0], q[1]): → (|000> + |110>)/√2
- M(q[1]), M(q[2]):
  - q[1] is measured first (higher bit in bitstring)
  - q[2] is measured second (lower bit)
  - |000>: q[1]=0, q[2]=0 → |00>
  -

## isqExpand/algo/75

- task_id: `isqExpand/algo/75`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `vqe`, `bug_fix`, `wrong_gate`, `rz_vs_ry`, `population_transfer`
- source: `isq_expansion`
- dataset_index: `3968`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```isq
import std;
qbit q[2];

procedure main() {
    // Rotation layer (BUG: Rz instead of Ry)
    Rz(pi/3.0, q[0]);
    Rz(pi/3.0, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The bug uses Rz instead of Ry in the VQE rotation layer.

Rz(theta)|0> = e^{-i*theta/2}|0> — Rz only adds a phase to basis states, it never creates a superposition from |0>. So Rz(pi/3)|0> = e^{-i*pi/6}|0>, which has P(0)=1, P(1)=0.

With Rz on both qubits from |00>, the state remains |00> (up to global phase). CNOT on |00> does nothing. Result: P(00)=1.0, all others 0.

With the correct Ry gates:
Ry(pi/3)|0> = cos(pi/6)|0> + sin(pi/6)|1> = (sqrt3/2)|0> + (1/2)|1>
This creates actual superposition, enabling the CNOT to create entanglement.

Fix: Replace both Rz with Ry.

## isqTrain/23

- task_id: `isqTrain/23`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2209`

### Prompt

Help me write isQ code that implements the qft_subcircuit pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this QFT circuit step by step.

The circuit implements a 3-qubit QFT with an alternative swap (three-CNOT decomposition) decomposition using H-CZ-H instead of CNOT gates.

Initial state: |000⟩

After X(q[2]): |100⟩ (q[2] is the highest bit, but wait, let me reconsider the bit ordering)

Actually, let me be careful about the qubit ordering. In isQ, q[0] is typically the least significant bit.

Wait, looking at the main:
- X(q[2]) sets q[2] to |1⟩
- Then qft3(q[0], q[1], q[2]) is called where a=q[0], b=q[1], c=q[2]

So after X(q[2]), the state is |100⟩ where q[2]=1 (rightmost bit in ket notation depends on convention).

Let me use the convention where |q[2]q[1]q[0]⟩.

After X(q[2]): |100⟩ (q[2]=1, q[1]=0, q[0]=0)

Now applying QFT3:

1. H(a) = H(q[0]): State becomes |100⟩ → (|100⟩ + |101⟩)/√2 = (|4⟩ + |5⟩)/√2

Wait, let me reconsider. The state is |q[2]q[1]q[0]⟩ = |100⟩ means q[2]=1, q[1]=0, q[0]=0.

After H(q[0]): (|100⟩ + |101⟩)/√2

2. ctrl Rz(π/2, b, a) = ctrl Rz(π/2, q[1], q[0]): This applies Rz(π/2) to q[1] controlled by q[0].

When q[0]=|1⟩, q[1] gets phase e^(iπ/4)... wait, Rz(π/2) applies e^(-iπ/4) to |0⟩ and e^(iπ/4) to |1⟩. But q[1] is |0⟩ in both terms.

Hmm, let me reconsider. The controlled-Rz applies Rz(θ) to the target when control is |1⟩.

Actually, Rz(θ)|0⟩ = e^(-iθ/2)|0⟩, Rz(θ)|1⟩ = e^(iθ/2)|1⟩.

So ctrl Rz(π/2, q[1], q[0]): when q[0]=|1⟩, apply Rz(π/2) to q[1].

State: (|100⟩ + e^(-iπ/4)|101⟩)/√2

Wait, that's not right either. Rz(π/2) on |0⟩ gives e^(-iπ/4)|0⟩.

State: (|100⟩ + e^(-iπ/4)|101⟩)/√2

3. ctrl Rz(π/4, c, a) = ctrl Rz(π/4, q[2], q[0]): when q[0]=|1⟩, apply Rz(π/4) to q[2].

q[2] is |1⟩ when q[0]=|1⟩ (in the |101⟩ term).

Rz(π/4)|1⟩ = e^(iπ/8)|1⟩

State: (|100⟩ + e^(-iπ/4)·e^(iπ/8)|101⟩)/√2 = (|100⟩ + e^(-iπ/8)|101⟩)/√2

Hmm, this is getting complex. Let me just verify the output.

The QFT of |100⟩ (which is computational basis state |4⟩ in a 3-qubit system) should give an equal superposition over all 8 basis states.

Actually, QFT|j⟩ = (1/√N) Σ_k e^(2πijk/N)|k⟩

For N=8 and j=4:
QFT|4⟩ = (1/√8) Σ_{k=0}^{7} e^(2πi·4·k/8)|k⟩
= (1/√8) Σ_{k=0}^{7} e^(πik)|k⟩
= (1/√8) Σ_{k=0}^{7} (-1)^k|k⟩

This gives equal amplitudes with alternating signs: 1/√8 for each, so probabilities are all 1/8 = 0.125.

This matches the predicted output!

Now let me trace through more carefully but I'll be more concise.

Starting state: X(q[2]) gives |

## isqQA/quantum_algorithms/129_application_scenario

- task_id: `isqQA/quantum_algorithms/129_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `application_scenario`, `algorithm`, `纠缠交换`
- source: `qa_pipeline`
- dataset_index: `5328`

### Prompt

纠缠交换不仅是量子力学非定域性的直观体现，更是长距离量子通信的基石。请深入剖析纠缠交换在量子中继器中的核心作用机制，并结合“墨子号”量子卫星等实际案例探讨其未来在量子互联网中的发展前景。此外，请提供一段使用isQ语言编写的代码，演示如何通过贝尔态测量使得两个从未发生过直接相互作用的量子比特建立纠缠。

### Reference answer

纠缠交换是量子信息科学中极具颠覆性的核心技术之一。在实际应用中，它最核心的场景是构建量子中继器，以解决长距离光纤通信中光子信号呈指数级衰减的物理瓶颈。

在经典通信中，信号放大器可以简单地增强削弱的光信号，但在量子通信（如量子密钥分发 QKD）中，由于量子不可克隆定理，我们无法复制或放大未知的量子态。纠缠交换巧妙地突破了这个限制：假设通信双方 Alice 和 Bob 相距甚远，他们在中间建立一个中继站 Charlie。Alice 和 Charlie 共享一对纠缠粒子（A, C1），Charlie 和 Bob 共享另一对纠缠粒子（C2, B）。此时，A 和 B 并无纠缠。Charlie 对手中的 C1 和 C2 进行贝尔态测量（Bell State Measurement, BSM），迫使它们坍缩到某一个贝尔态上。根据量子力学的奇妙特性，这一测量行为会瞬间将 A 和 B 投影到一个高度纠缠的状态中。通过经典信道将 Charlie 的测量结果告知 Alice 和 Bob，他们即可通过局域的酉变换建立标准的最大纠缠态。通过逐段建立短距离纠缠并进行交换，量子中继器将长距离通信的指数级损耗转化为多项式级损耗，这是构建全球化量子互联网的唯一可行途径。

在应用案例方面，中国发射的“墨子号”量子科学实验卫星是纠缠交换技术的巅峰之作。在实验中，卫星作为移动中继站，分别向相距1200公里的两个地面站分发纠缠光子。通过在卫星上进行联合贝尔态测量，成功实现了千公里级的远程纠缠分发，证明了基于纠缠交换的星地一体化量子网络的工程可行性。未来，纠缠交换将与量子存储器深度融合，推动分布式量子计算和量子传感器网络的发展，使得未来不仅能在全球范围内实现绝对安全的通信，还能将分散的量子计算节点连接成具有超强算力的“量子计算云”。

下面是使用 isQ 语言编写的纠缠交换核心过程的代码演示。假设我们分配了4个量子比特，其中 q[0] 和 q[1] 初始纠缠，q[2] 和 q[3] 初始纠缠。我们通过对 q[1] 和 q[2] 执行 CNOT 和 Hadamard 门模拟贝尔态测量，并根据测量结果对两端的 q[0] 和 q[3] 进行局域保罗门纠正，最终在 q[0] 和 q[3] 之间建立完美的纠缠连接：

import std;

qbit q[4];

procedure main() {
    // 1. 初始化：在 q[0], q[1] 以及 q[2], q[3] 之间分别建立纠缠对
    H(q[0]);
    CNOT(q[0], q[1]);

    H(q[2]);
    CNOT(q[2], q[3]);

    // 2. 纠缠交换：中继节点对 q[1] 和 q[2] 执行贝尔基测量
    // 通过 CNOT 和 H 门将贝尔基转换到计算基上进行测量
    CNOT(q[1], q[2]);
    H(q[1]);

    // 3. 执行测量并通过经典信道获取结果
    int r1 = M(q[1]);
    int r2 = M(q[2]);

    // 4. 遥现纠错：根据测量结果，对远程的 q[0] 和 q[3] 进行相应的局域操作
    // 若 r2 为 1，则需要对 q[3] 施加 X 门纠正
    if (r2 == 1) {
        X(q[3]);
    }
    // 若 r1 为 1，则需要对 q[0] 施加 Z 门纠正
    if (r1 == 1) {
        Z(q[0]);
    }
    // 至此，原本没有直接相互作用的 q[0] 和 q[3] 成功建立了贝尔态纠缠
}

## isqQA/quantum_algorithms/122_principle_advantage

- task_id: `isqQA/quantum_algorithms/122_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `离散时间量子行走`
- source: `qa_pipeline`
- dataset_index: `4376`

### Prompt

作为量子计算领域的学生，我对基于离散时间量子行走的算法非常感兴趣。请问教授，离散时间量子行走的宏观原理是什么？它与经典的随机漫步在时间复杂度和空间扩散规律上有何显著差异？其带来量子加速的根本物理与数学来源是什么？最后，能否提供一段使用isQ语言实现的简单的一维量子行走代码，以帮助我直观理解底层量子线路的设计逻辑？

### Reference answer

离散时间量子行走（Discrete-Time Quantum Walk, DTQW）是经典随机漫步在量子计算领域的直接推广与升级，它不仅是理解量子动力学扩散的重要模型，更是设计诸多高速量子算法（如元素区分、图搜索和布尔公式求值）的核心底层工具。

首先，从**宏观原理**来看，离散时间量子行走建立在由“位置空间”和“硬币空间”构成的复合希尔伯特空间中。其核心演化机制可以被拆分为两个交替执行的酉操作：
1. **硬币抛掷**：在每一步移动之前，对一个辅助的量子态（即“硬币”）施加一个酉操作（如Hadamard门）。这与经典抛硬币不同，量子硬币会处于正面和反面的相干叠加态。
2. **条件移位**：根据量子硬币的叠加状态，将行走者在位置空间中进行条件性的平移。例如，硬币为 |0⟩ 时向左走，为 |1⟩ 时向右走。
由于量子力学的线性性质，行走者实际上同时探索了所有可能的路径，并在位置空间和硬币空间之间产生了深度的量子纠缠。

其次，在**时间复杂度对比与扩散规律**上，经典与量子展现出了本质的区别：
- 经典随机漫步：受限于经典概率的扩散方程，经过 $t$ 步后，粒子的空间分布方差（即扩散距离的平方）呈线性增长，因此其标准差（空间扩散范围）为 $\Delta x \sim O(\sqrt{t})$。
- 离散时间量子行走：得益于量子态的相干叠加，经过 $t$ 步后，其概率分布的方差呈二次方增长，标准差 $\Delta x \sim O(t)$。这种类似光速极限的线性扩散被称为“弹道式传播”。在算法应用中，这意味着量子行走寻找目标节点的搜索时间复杂度从经典图搜索的 $O(N)$ 降低到了 $O(\sqrt{N})$，实现了平方级的二次加速；在某些特定的黑盒问题或特殊图结构中，甚至能展现出指数级的加速。

最后，**量子加速的根本来源**是**量子相干性与干涉效应**。在量子行走中，向左和向右移动的概率幅并不是简单的相加，而是作为复振幅进行相长干涉或相消干涉。特别是相消干涉极大地抑制了行走者停留在原点或原路返回的概率，而相长干涉则将概率幅放大到更远的位置。这种干涉机制打破了经典概率论中的中心极限定理束缚，使得量子行走能够以极快的速度遍历状态空间。

为了让你直观理解，下面我为你编写了一段基于 **isQ语言** 的一维环面（周期为4）量子行走代码示例。代码中使用了2个量子比特表示位置，1个量子比特表示硬币，通过控制门清晰地实现了根据硬币状态进行加1（右移）或减1（左移）的条件移位逻辑：

```isq
import std;

// 声明用于硬币的1个量子比特和用于位置的2个量子比特
qbit c[1];
qbit p[2];

procedure main() {
    // 初始状态全为 |0>，即位置在 00 (0号节点)，硬币为 |0>
    
    // 执行2步完整的离散时间量子行走
    for i in 0:2 {
        // 1. 硬币抛掷操作：使用 Hadamard 门创造叠加态
        H(c[0]);
        
        // 2. 条件移位操作
        // 当硬币为 |1> 时，位置在模4意义下加1（右移）
        // 模4加法器逻辑：(高位受低位控制翻转，然后最低位翻转)
        ctrl @[c[0]] CNOT(p[0], p[1]);
        ctrl @[c[0]] X(p[0]);
        
        // 当硬币为 |0> 时，位置在模4意义下减1（左移）
        // 模4减法器逻辑：(最低位翻转，然后高位受低位控制翻转)
        nctrl @[c[0]] X(p[0]);
        nctrl @[c[0]] CNOT(p[0], p[1]);
    }
    
    // 测量硬币和位置量子比特，观察行走后的概率分布
    int coin_res = M(c[0]);
    int pos_res0 = M(p[0]);
    int pos_res1 = M(p[1]);
}
```
通过研究这段代码中的受控门（`ctrl` 和 `nctrl`）逻辑，你可以深刻体会到量子计算是如何将不同路径的计算步骤融合进同一个酉演化过程中的。

## isqTrain/1179

- task_id: `isqTrain/1179`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2211`

### Prompt

Code this in isQ: implements the fourier_checking pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants a reasoning section explaining a Fourier checking / forrelation circuit implemented in isQ.

Let me trace through the circuit:

1. Initial state: |00⟩
2. First H layer: H⊗H |00⟩ = |++⟩ = (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2
3. Phase oracle f: T on q[0], S on q[1]
   - T|+⟩ = (|0⟩ + e^(iπ/4)|1⟩)/√2
   - S|+⟩ = (|0⟩ + i|1⟩)/√2
4. Middle H layer: H⊗H
5. Phase oracle g: S on q[0], T on q[1]
6. Final H layer: H⊗H
7. Then H-H pair on q[0] (which cancels to identity)
8. Measurement

Let me compute this more carefully.

Initial: |00⟩

After first H layer:
|ψ₁⟩ = |++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

After T(q[0]) and S(q[1]):
T acts on q[0]: T|+⟩ = (|0⟩ + e^(iπ/4)|1⟩)/√2
S acts on q[1]: S|+⟩ = (|0⟩ + i|1⟩)/√2

|ψ₂⟩ = (1/2)(|00⟩ + i|01⟩ + e^(iπ/4)|10⟩ + ie^(iπ/4)|11⟩)

After middle H layer (H⊗H):
For each basis state, H⊗H maps:
|00⟩ → |++⟩
|01⟩ → |+-⟩
|10⟩ → |-+⟩
|11⟩ → |−−⟩

So H⊗H|ψ₂⟩ = (1/2)(|++⟩ + i|+-⟩ + e^(iπ/4)|-+⟩ + ie^(iπ/4)|--⟩)

Let me expand this:
= (1/4)[(|00⟩+|01⟩+|10⟩+|11⟩) + i(|00⟩-|01⟩+|10⟩-|11⟩) + e^(iπ/4)(|00⟩+|01⟩-|10⟩-|11⟩) + ie^(iπ/4)(|00⟩-|01⟩-|10⟩+|11⟩)]

Coefficients:
|00⟩: 1 + i + e^(iπ/4) + ie^(iπ/4) = (1+i)(1+e^(iπ/4))
|01⟩: 1 - i + e^(iπ/4) - ie^(iπ/4) = (1-i)(1+e^(iπ/4))  -- wait, let me redo

Actually, let me be more careful:
|00⟩: 1 + i + e^(iπ/4) + ie^(iπ/4) = (1+e^(iπ/4)) + i(1+e^(iπ/4)) = (1+i)(1+e^(iπ/4))
|01⟩: 1 - i + e^(iπ/4) - ie^(iπ/4) = (1+e^(iπ/4)) - i(1-e^(iπ/4)) -- hmm, let me just compute directly

Wait, let me be more careful with the signs:

|00⟩: 1 + i + e^(iπ/4) + ie^(iπ/4)
|01⟩: 1 - i + e^(iπ/4) - ie^(iπ/4)
|10⟩: 1 + i - e^(iπ/4) - ie^(iπ/4)
|11⟩: 1 - i - e^(iπ/4) + ie^(iπ/4)

Let me factor:
|00⟩: (1+i)(1+e^(iπ/4))
|01⟩: (1-i)(1+e^(iπ/4))
|10⟩: (1+i)(1-e^(iπ/4))
|11⟩: (1-i)(1-e^(iπ/4))

Hmm wait, let me double-check:
(1-i)(1+e^(iπ/4)) = 1 + e^(iπ/4) - i - ie^(iπ/4) ✓ for |01⟩
(1+i)(1-e^(iπ/4)) = 1 - e^(iπ/4) + i - ie^(iπ/4) = 1 + i - e^(iπ/4

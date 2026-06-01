# ISQ training COT RAG corpus: qft_subcircuit shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3312

- task_id: `isqTrain/3312`
- task_type: `code_generation`
- category: `qft_subcircuit`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_inv`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3910`

### Prompt

Implement the following in isQ: an isQ program: apply 2-qubit QFT then inverse QFT on |00>. The net effect should be identity.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task type: code_generation (reasoning only).
    *   Goal: Explain an isQ program that applies a 2-qubit QFT followed by an inverse 2-qubit QFT to the state |00>.
    *   Output format: "## Reasoning" followed by a concise explanation (3-15 lines).
    *   Constraint: NO isQ code in the output, strict adherence to specified formatting.

2.  **Analyze the Circuit (from circuit implementation):**
    *   Initial state: |00>.
    *   **QFT Step:**
        *   `H(q[0])`: |00> -> (|0> + |1>)/√2 ⊗ |0> = (|00> + |10>)/√2.
        *   `ctrl Rz(pi/2, q[1], q[0])` (q[1] controls q[0] - wait, reference says `ctrl Rz(..., q[1], q[0])` which means q[1] is control, q[0] is target. So if q[1] is |1>, apply Rz to q[0]. But state has q[1]=|0>, so nothing happens? Wait, standard QFT is `ctrl Rz(target, control)` or `crz(control, target)`. Let's look at the reference code: `ctrl Rz(3.14/2.0, q[1], q[0])`. In isQ `ctrl Rz(theta, q[1], q[0])` means q[1] controls q[0]. But wait, The circuit should `H(q[1])` next. Standard 2-qubit QFT applies H to q[1], then controlled Rz from q[1] to q[0], then swap (three-CNOT decomposition). Wait, standard QFT is: H(q[1]), CRz(q[0] -> q[1]), H(q[0]), swap (three-CNOT decomposition). Let me re-analyze the:
            *   `H(q[0]);`
            *   `ctrl Rz(pi/2, q[1], q[0]);`
            *   `H(q[1]);`
            *   `CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1]);` (This is swap (three-CNOT decomposition)).
            Let's trace this standard QFT from the reference code (actually it looks like a slightly permuted QFT but let's just trace the math):
            Initial: |00>
            `H(q[0])` -> (|00> + |10>)/√2
            `ctrl Rz(pi/2, q[1], q[0])` -> q[1] is 0, so no phase added. State is (|00> + |10>)/√2.
            `H(q[1])` -> q[1] becomes (|0>+|1>)/√2.
            State is 1/2 (|00> + |01> + |10> + |11>).
            swap (three-CNOT decomposition)(q[0], q[1]) -> 1/2 (|00> + |10> + |01> + |11>).
            Actually, since it's a uniform superposition, any phase addition or permutations of uniform superpositions won't change it! Wait, if it's (1/2)(|0>+|1>)(|0>+|1>), it's invariant under swap (three-CNOT decomposition) and local phases!
            Wait, let's look at the actual reference code carefully.
            Is it exactly identity?
            QFT(|00>) = |00> + |01> + |10> + |11> = (|0>+|1>)(|0>+|1>).
            If we apply inv QFT to this, we get |00> back.
            So I don't even need to trace the exact reference QFT implementation if I just state the principle. But I should trace the specific reference implementation to be precise.
            Actually, let's trace:
            1. |00>
            2. H(q[0]) -> (|00> + |10>)/√2
            3. `ctrl Rz(pi/2, q[1], q[0])` -> q[1] is control, q[0] is target. Since q[1] is always 0 here, state is still (|00> + |10>)/√2.
            4. H(q[1]) -> (|00> + |01> + |10> + |11>)/2
            5. swap (three-CNOT decomposition) -> (|00> + |10> + |01> + |11>)/

## isqTrain/3310

- task_id: `isqTrain/3310`
- task_type: `code_generation`
- category: `qft_subcircuit`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3488`

### Prompt

Write isQ code for the following quantum task: an isQ program: 2-qubit QFT on initial state |01>. QFT circuit: H(q[0]), ctrl Rz(pi/2) from q[1] to q[0], H(q[1]), SWAP.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Apply 2-qubit QFT to initial state |01> and verify equal measurement probabilities.

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. Start |00>, apply X(q[1]) → |01>
2. H(q[0]): |01> → (1/√2)(|01> + |11>)
3. ctrl Rz(π/2) [q[1]→q[0]]: phases q[0] when q[1]=|1⟩ → (1/√2)(|01> + i|11>)
4. H(q[1]): |1>→|-> on q[1] → (1/2)(|00> - |01> + i|10> - i|11>)
5. swap (three-CNOT decomposition)(q[0],q[1]) via 3 CNOTs → (1/2)(|00> + i|01> - |10> - i|11>)

**Probabilities:** Each basis state has amplitude 1/2, so |amplitude|² = 0.25 for all four outcomes: {|00⟩: 0.25, |01⟩: 0.25, |10⟩: 0.25, |11⟩: 0.25}.

## isqTrain/3142

- task_id: `isqTrain/3142`
- task_type: `code_generation`
- category: `qft_subcircuit`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5578`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply 2-qubit QFT to initial state |00>. QFT circuit: H(q[0]), ctrl Rz(pi/2) from q[1] to q[0], H(q[1]), then SWAP. Measure both.

### Chain-of-thought reasoning

The user wants me to explain the 2-qubit QFT applied to |00>.

Let me trace through the circuit:

1. Initial state: |00>

2. H(q[0]): Apply Hadamard to qubit 0
   |00> → 1/√2 (|00> + |10>)

3. ctrl Rz(π/2, q[1], q[0]): This is a controlled-Rz with q[1] as control and q[0] as target. When q[1] is |1>, apply Rz(π/2) to q[0].
   Rz(π/2) = diag(1, e^(iπ/2)) = diag(1, i)
   
   Current state: 1/√2 (|00> + |10>)
   - |00>: q[1]=0, so no phase applied → |00>
   - |10>: q[1]=1, so Rz(π/2) applied to q[0]. Since q[0]=1, we get e^(iπ/2) = i factor → i|10>
   
   State becomes: 1/√2 (|00> + i|10>)

4. H(q[1]): Apply Hadamard to qubit 1
   |0>₁ → (|0> + |1>)/√2
   |1>₁ → (|0> - |1>)/√2
   
   State: 1/√2 (|00> + i|10>)
   = 1/√2 [(|0>₁|0>₀)/√2 + (|0>₁|1>₀)/√2 + i((|0>₁|0>₀)/√2 - (|0>₁|1>₀)/√2)]
   
   Wait, let me be more careful. Let me use |q[1]q[0]> notation.
   
   State: 1/√2 (|00> + i|10>)
   
   H on q[1]:
   |0>₁ → (|0> + |1>)/√2
   |1>₁ → (|0> - |1>)/√2
   
   So |00> → 1/√2 (|00> + |10>)
   And |10> → 1/√2 (|00> - |10>)
   
   State: 1/√2 [1/√2 (|00> + |10>) + i · 1/√2 (|00> - |10>)]
   = 1/2 [(|00> + |10>) + i(|00> - |10>)]
   = 1/2 [(1+i)|00> + (1-i)|10>]

5. swap (three-CNOT decomposition)(q[0], q[1]) using CNOTs:
   Swaps q[0] and q[1].
   
   State before swap (three-CNOT decomposition): 1/2 [(1+i)|00> + (1-i)|10>]
   
   Wait, this doesn't look right for equal probabilities. Let me re-examine.

Actually, wait. Let me re-examine the circuit order. The standard QFT for 2 qubits on |00> should give |00> since QFT|00> = |++> ... no wait.

QFT on |00>:
QFT|x> = 1/N Σ_k e^(2πixk/N)|k>

For x = 0 (|00> = |0> in big-endian 2-bit representation):
QFT|0> = 1/2 Σ_{k=0}^{3} e^0|k> = 1/2 (|0> + |1> + |2> + |3>) = 1/2 (|00> + |01> + |10> + |11>)

So after QFT on |00>, we should get an equal superposition of all 4 states.

Let me retrace:

1. |00>

2. H(q[0]): qubit 0 → superposition
   |00> → 1/√2(|00> + |01>)
   
   Wait, I need to be careful about which qubit is which. Let me use |q[1]q[0]> notation consistently.
   
   |00> means q[1]=0, q[0]=0.
   
   H(q[0]): acts on qubit 0 (the rightmost in my notation)
   |0> → (|0> + |1>)/√2
   
   |00> → 1/√2(|00> + |01>)

3. ctrl Rz(π/2, q[1], q[0]): q[1

## isqTrain/3311

- task_id: `isqTrain/3311`
- task_type: `code_generation`
- category: `qft_subcircuit`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `182`

### Prompt

Implement the following in isQ: an isQ program: 2-qubit QFT on initial state |11>. QFT circuit: H(q[0]), ctrl Rz(pi/2) from q[1] to q[0], H(q[1]), SWAP.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Write a reasoning section for a specific isQ quantum program (2-qubit QFT on |11>).
    *   Format constraints: Concise (3-8 lines for simple, up to 15 for complex), use Dirac notation, output ONLY the reasoning section starting with "## Reasoning", NO isQ code blocks.
    *   Goal: Explain 1) circuit goal, 2) qubits/measured, 3) state evolution, 4) expected probabilities.

2.  **Analyze the Circuit:**
    *   Initial state: |00>
    *   Prepare state |11> -> `X(q[0]); X(q[1]);` -> state is |11>.
    *   QFT step 1: H(q[0]) -> |1> becomes (|0> - |1>)/sqrt(2) = |->
        *   Overall state: |-1> = (|01> - |11>) / sqrt(2)
    *   QFT step 2: ctrl Rz(pi/2, q[1], q[0]) -> if q[1] is |1>, apply Rz(pi/2) to q[0].
        *   Wait, standard QFT applies controlled-R_k where control is j and target is i (for k = j-i). Wait, standard 2-qubit QFT on q0, q1.
        *   Let's trace the given code: `ctrl Rz(pi/2, q[1], q[0]);`
        *   This is a controlled-Rz(pi/2) with q[1] as control, q[0] as target.
        *   State |-1> = (|01> - |11>) / sqrt(2)
        *   Apply CRz(pi/2, q1->q0):
            *   |01> gets phase e^{-i pi/4} on q0? No, Rz(pi/2) is diag(1, e^{i pi/2}) = diag(1, i).
            *   Actually, `ctrl Rz` in isQ applies Rz on target if control is |1>.
            *   So |01> -> |01>.
            *   |11> -> i|11>.
        *   Wait, let me double check the isQ `Rz` gate. `Rz(theta)` usually means diag(1, e^{i*theta}). If theta=pi/2, diag(1, i).
        *   State becomes: (|01> - i|11>) / sqrt(2).
    *   QFT step 3: H(q[1]) -> Apply H to q[1].
        *   |01> -> |0>(|0>-|1>)/sqrt(2) = (|00> - |01>)/sqrt(2)
        *   |11> -> |1>(|0>-|1>)/sqrt(2) = (|10> - |11>)/sqrt(2)
        *   Overall state before phase normalization: ( (|00> - |01>) - i(|10> - |11>) ) / 2
    *   swap (three-CNOT decomposition) step: CNOT(q0, q1); CNOT(q1, q0); CNOT(q0, q1); -> swaps q0 and q1.
        *   Wait, standard QFT usually swaps at the end. If q0 is most significant (|q0 q1>), then QFT swaps indices.
        *   Let's trace: ( |00> - |01> - i|10> + i|11> ) / 2.
        *   Swap q0 and q1:
            *   |00> -> |00>
            *   |01> -> |10>
            *   |10> -> |01>
            *   |11> -> |11>
        *   State becomes: ( |00> - |10> - i|01> + i|11> ) / 2 = (1/2)|0>(|0>-i|1>) + (1/2)|1>(-|0>+i|1>)
        *   Wait! The resulting probabilities should be uniform: 0.25 for all.
        *   Let's check probabilities of the state ( |00> - |01> - i|10> + i|11> ) / 2. Magnitude squared of each coefficient is 1/4.
        *   Does the swap change the probabilities of individual qubits? No. Magnitude squared of |00>, |01>, |10>, |11> remains 0.25.
        *   Wait, in isQ measurement, `M(q[0])` is the higher bit or lower bit? "ear

## isqTrain/3143

- task_id: `isqTrain/3143`
- task_type: `code_generation`
- category: `qft_subcircuit`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2239`

### Prompt

用isQ实现an isQ program: apply 2-qubit QFT to initial state |10>. QFT circuit: H(q[0]), ctrl Rz(pi/2) from q[1] to q[0], H(q[1]), then SWAP. Measure both.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply 2-qubit QFT to initial state |10⟩ (q[0]=1, q[1]=0) and measure both qubits.

**State evolution:**
1. **X(q[0]):** |00⟩ → |10⟩
2. **H(q[0]):** |10⟩ → (|00⟩ − |10⟩)/√2
3. **ctrl Rz(π/2, q[1], q[0]):** Since q[1]=|0⟩ in both terms, the gate is never

## isqTrain/3314

- task_id: `isqTrain/3314`
- task_type: `code_generation`
- category: `qft_subcircuit`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_inv`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4399`

### Prompt

Code this in isQ: an isQ program: apply 2-qubit QFT then inverse QFT on |10>. The net effect should be identity.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program that applies QFT followed by inverse QFT on the initial state |10>.

Let me trace through the circuit:

1. Initial state: |00>
2. X(q[0]) -> |10>
3. QFT on |10>:
   - H(q[0]): |10> -> (1/√2)(|00> - |10>)  [actually let me be careful: q[0] is the first qubit, so |10> means q[0]=0, q[1]=1]
   
   Wait, I need to be careful about the bit ordering. In isQ, typically q[0] is the least significant bit or most significant?

Let me think about this more carefully. The state |10> typically means qubit 0 is in state |0> and qubit 1 is in state |1>, or it could mean q[0]=1, q[1]=0.

Actually, in quantum computing, |10> usually means the first qubit (q0) is |1> and the second qubit (q1) is |0>. So X(q[0]) applied to |00> gives |10>.

QFT on 2 qubits:
The 2-qubit QFT is:
1. H on q[0]
2. Controlled-Rz(π/2) from q[1] to q[0]
3. H on q[1]
4. swap (three-CNOT decomposition) q[0] and q[1]

Let me trace:

Initial: |10> (meaning q[0]=1, q[1]=0)

Step 1: H(q[0])
|10> = |1>⊗|0>
H on q[0]: (1/√2)(|0> - |1>)⊗|0> = (1/√2)(|00> - |10>)

Step 2: ctrl Rz(π/2) from q[1] to q[0]
Since q[1]=0 in both |00> and |10>, this controlled gate doesn't do anything.
State remains: (1/√2)(|00> - |10>)

Step 3: H(q[1])
(1/√2)(|0>⊗(1/√2)(|0>+|1>) - |1>⊗(1/√2)(|0>+|1>))
= (1/2)(|00> + |01> - |10> - |11>)

Step 4: swap (three-CNOT decomposition)(q[0], q[1]) via 3 CNOTs
(1/2)(|00> + |10> - |01> - |11>)

Now inverse QFT:
The inverse QFT reverses the order and conjugates phases.

Step 5: swap (three-CNOT decomposition) (inverse of step 4)
(1/2)(|00> + |01> - |10> - |11>)

Step 6: inv H(q[1]) = H(q[1]) (since H is self-inverse)
Apply H to q[1]:
|00> -> (1/√2)(|00>+|01>)
|01> -> (1/√2)(|00>-|01>)
|10> -> (1/√2)(|10>+|11>)
|11> -> (1/√2)(|10>-|11>)

(1/2)[(1/√2)(|00>+|01>) + (1/√2)(|00>-|01>) - (1/√2)(|10>+|11>) - (1/√2)(|10>-|11>)]
= (1/2√2)[|00>+|01>+|00>-|01>-|10>-|11>-|10>+|11>]
= (1/2√2)[2|00> - 2|10>]
= (1/√2)(|00> - |10>)

Step 7: ctrl Rz(-π/2) from q[1] to q[0]
For |00>: q[1]=0, no effect
For |10>: q[1]=0, no effect
State remains: (1/√2)(|00> - |10>)

Step 8: inv H(q[0]) = H(q[0])
(1/√2)[(1/√2)(|00>+|10>) - (1/√2)(|00>-|10>)]
= (1/2)[|00>+|10>-|00>+|10>]
= (1/2)[2|10>]
= |10>

The final state is |10>, confirming that QFT followed by inverse QFT is the identity.

The expected measurement probabilities

## isqTrain/3313

- task_id: `isqTrain/3313`
- task_type: `code_generation`
- category: `qft_subcircuit`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_inv`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2102`

### Prompt

Write an isQ program that an isQ program: apply 2-qubit QFT then inverse QFT on |01>. The net effect should be identity.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a quantum circuit that applies QFT and then inverse QFT on the state |01>.

Let me trace through the circuit:

1. Initialize |00>
2. X(q[1]) → |01>
3. QFT on |01>:
   - H(q[0]) → (1/√2)(|01> + |11>) = (1/√2)(|0> + |1>)⊗|1>
   - ctrl Rz(π/2, q[1], q[0]) → applies Rz(π/2) to q[0] when q[1]=|1>
     - |01> stays |01>, |11> gets phase e^(iπ/4)... wait, let me reconsider
     - Actually ctrl Rz(π/2, q[1], q[0]) means q[1] is control, q[0] is target
     - When q[1] = |1>, apply Rz(π/2) to q[0]
     - Rz(π/2) = [[1,0],[0,e^(iπ/2)]] = [[1,0],[0,i]]
     - |01> → |01> (unchanged, q[0]=|0>)
     - |11> → e^(iπ/2)|11> = i|11>
     - State: (1/√2)(|01> + i|11>)
   - H(q[1]) → applies H to q[1]
     - |01> → (1/√2)(|00> + |10>)... wait no
     - Actually |01> means q[0]=|0>, q[1]=|1>
     - H(q[1]) on |01>: |0>⊗H|1> = |0>⊗(1/√2)(|0>-|1>) = (1/√2)(|00> - |01>)
     - H(q[1]) on |11>: |1>⊗H|1> = |1>⊗(1/√2)(|0>-|1>) = (1/√2)(|10> - |11>)
     - State: (1/√2)[(1/√2)(|00> - |01>) + i(1/√2)(|10> - |11>)]
     - = (1/2)(|00> - |01> + i|10> - i|11>)
   - swap (three-CNOT decomposition) via CNOTs: CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1])
     - This swaps q[0] and q[1]
     - |00> → |00>, |01> → |10>, |10> → |01>, |11> → |11>
     - State: (1/2)(|00> - |10> + i|01> - i|11>)

4. Inverse QFT:
   - Inverse swap (three-CNOT decomposition): CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1])
     - Swaps back: |10> → |01>, |01> → |10>
     - State: (1/2)(|00> - |01> + i|10> - i|11>)
   - inv H(q[1]) = H(q[1]) (H is self-inverse)
     - |00> → (1/√2)(|00> + |01>)... wait let me be careful
     - inv H = H since H† = H
     - State after H(q[1]): Apply H to q[1]
     - |00>: (1/√2)(|00> + |01>)
     - |01>: (1/√2)(|00> - |01>)
     - |10>: (1/√2)(|10> + |11>)
     - |11>: (1/√2)(|10> - |11>)
     
     So: (1/2)[(1/√2)(|00> + |01>) - (1/√2)(|00> - |01>) + i(1/√2)(|10> + |11>) - i(1/√2)(|10> - |11>)]
     = (1/2)(1/√2)[|00> + |01> - |00> + |01> + i|10> + i|11> - i|10> + i|11>]
     = (1/2√2)[2|01> + 2i|11>]
     = (1

## isqTrain/3315

- task_id: `isqTrain/3315`
- task_type: `code_generation`
- category: `qft_subcircuit`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_inv`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5370`

### Prompt

Implement the following in isQ: an isQ program: apply 2-qubit QFT then inverse QFT on |11>. The net effect should be identity.

### Chain-of-thought reasoning

The user wants a reasoning section for a circuit that:
1. Initializes 2 qubits to |11> using X gates
2. Applies QFT on the 2 qubits
3. Applies inverse QFT on the 2 qubits
4. Measures both qubits

The net effect is identity, so we should get |11> with probability 1.0.

Let me trace through the QFT and inverse QFT:

For a 2-qubit QFT on |11>:
- Start: |11>
- H on q[0]: 1/√2 (|01> - |11>) = 1/√2 (|0> - |1>)⊗|1>
- CRz(π/2, q[1], q[0]): applies phase to q[0] if q[1]=1
  - |01> stays |01>
  - |11> becomes e^(iπ/4)|11>
  - Wait, CRz(θ) on control c, target t applies Rz(θ) to t when c=|1>
  - Rz(θ)|0> = |0>, Rz(θ)|1> = e^(iθ/2)|1>
  - Actually Rz(θ) = [[1,0],[0,e^(iθ)]]
  
  Hmm, let me reconsider. Rz(θ, q) is [[1,0],[0,e^(iθ)]].
  
  CRz(π/2, q[1], q[0]): applies Rz(π/2) to q[0] when q[1]=|1>
  
  State after H(q[0]): 1/√2(|01> - |11>)
  
  After CRz(π/2, q[1], q[0]):
  - |01> stays (q[1]=0, no rotation)
  - |11> → e^(iπ/2)|11> = i|11>
  
  State: 1/√2(|01> - i|11>)
  
- H(q[1]): 
  - |01> → |0>⊗|+> = |0>⊗1/√2(|0>+|1>)
  - |11> → |1>⊗1/√2(|0>+|1>)
  - Wait, I need to be more careful about which qubit is which.
  
  Let me use q[1]q[0] ordering where q[1] is the higher bit.
  
  After X(q[0]), X(q[1]): |q[1]=1, q[0]=1> = |11>
  
  H(q[0]): q[0] becomes 1/√2(|0>-|1>)
  State: 1/√2(|10> - |11>)
  
  CRz(π/2, q[1], q[0]): applies Rz(π/2) to q[0] when q[1]=|1>
  Since q[1]=1 for both terms, Rz(π/2) is applied to q[0]:
  |10> → |1>⊗|0> → |1>⊗|0> (no phase on |0>)
  |11> → |1>⊗e^(iπ/2)|1> = i|11>
  
  State: 1/√2(|10> - i|11>)
  
  Hmm wait, Rz(π/2)|0> = |0>, Rz(π/2)|1> = e^(iπ/2)|1>
  
  So state: 1/√2(|10> - i|11>)
  
  H(q[1]): 
  |10> → |0>⊗|0> wait no...
  
  Let me be more careful. H(q[1]) applies H to q[1].
  
  |10> = |q[1]=1, q[0]=0>
  H(q[1])|1> = |->
  So |10> → 1/√2(|00> - |10>)
  
  |11> = |q[1]=1, q[0]=1>
  H(q[1])|1> = |->
  So |11> → 1/√2(|01> - |11>)
  
  State: 1/√2(1/√2(|00> - |10>) - i·1/√2(|01> - |11>))
       = 1/2(|00> - |10> - i|01> + i|11>)
  
  Then swap q[0] and q[1] using 3 CNOTs:
  CNOT(q[0], q[1]); CNOT(q

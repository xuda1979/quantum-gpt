# ISQ training COT RAG corpus: bernstein_vazirani shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3140

- task_id: `isqTrain/3140`
- task_type: `code_generation`
- category: `bernstein_vazirani`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1150`

### Prompt

Create an isQ quantum circuit that an isQ program: Bernstein-Vazirani algorithm with secret string s=110. Use 3 query qubits + 1 ancilla.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Bernstein-Vazirani algorithm recovers secret string s=110 using a single oracle query.

**Qubits:** 4 total — q[0],q[1],q[2] (query register), q[3] (ancilla, prepared in |−⟩). All 4 are measured.

**State evolution:**
1. **Init:** |0000⟩ → X(q[3]) → |0001⟩ → H(q[3]) → |000⟩(|0⟩−|1⟩)/√2
2. **H on query:** H⊗3 on q[0..2] → (1/2√2)∑ₓ|x⟩(|0⟩−|1⟩), where x ranges over 3-bit strings
3. **Oracle (s=110, bits 0,1 active):** CNOT(q[0],q[3]) and CNOT(q[1],q[3]) apply phase kickback: → (1/2√2)∑ₓ(−1)^(x₀⊕x₁)|x⟩(|0⟩−|1⟩)
4. **H on query:** H⊗3 converts

## isqTrain/3322

- task_id: `isqTrain/3322`
- task_type: `code_generation`
- category: `bernstein_vazirani`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`
- source: `isq_train_cot`
- dataset_index: `5264`

### Prompt

Help me write isQ code that an isQ program: Bernstein-Vazirani with secret s=011.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Bernstein-Vazirani algorithm with secret string s = 011.
    *   **Reference Code:** Provided. Uses 4 qubits (3 for input, 1 for ancilla).
    *   **predicted output:** Reasoning section ONLY (starting with "## Reasoning").
    *   **Constraints:** Dirac notation, concise (3-15 lines), step-by-step state evolution, NO code blocks.

2.  **Understand the Circuit:**
    *   Qubits: `q[0]`, `q[1]`, `q[2]` (input), `q[3]` (target/ancilla).
    *   Initial state: `|0000>`
    *   Target preparation: `X(q[3])` makes it `|1>`, then `H(q[3])` makes it `|- >`.
    *   Input preparation: `H(q[0]); H(q[1]); H(q[2])` creates superposition `|+++>`.
    *   Oracle Uf: `CNOT(q[1], q[3])` and `CNOT(q[2], q[3])`. This applies the phase oracle for s=011. Wait, `CNOT` with target in `|->` acts as a phase kickback. The control qubits get a `-1` phase if they are `|1>`. For s=011, q[1] and q[2] are the '1's. (Note: 011 usually means bit 2=1, bit 1=1, bit 0=0 if we read left to right as q[2]q[1]q[0]. Let's trace carefully).
        *   $U_f |x\rangle |- \rangle = (-1)^{x \cdot s} |x\rangle |- \rangle$.
        *   Since the controls are $q_1$ and $q_2$, the phase is $(-1)^{x_1 \oplus x_2}$.
    *   Interference: `H(q[0]); H(q[1]); H(q[2])`.
    *   Measurement: `M(q[0..3])`. The input qubits will deterministically collapse to the secret string `|011>` (or $q_2 q_1 q_0 = 110$ depending on bit ordering, let's look at the predicted output). predicted output is `|0110>` or `|0111>`.
    *   The predicted measurement probabilities are `|0110>: 0.5, |0111>: 0.5`.
    *   Let's check the bitstring indexing. "earlier measured qubit = higher bit".
    *   Measurements are `M(q[0])`, `M(q[1])`, `M(q[2])`, `M(q[3])`.
    *   Bitstring index = $q_0 \times 2^3 + q_1 \times 2^2 + q_2 \times 2^1 + q_3 \times 2^0$.
    *   For $q_0=0, q_1=1, q_2=1, q_3 \in \{0,1\}$: Bitstring = $0 \times 8 + 1 \times 4 + 1 \times 2 + q_3 \times 1 = 6 + q_3$.
    *   So binary string is `0110` (6) or `0111` (7).
    *   This means the secret string recovered is $q_0 q_1 q_2 = 011$. Since $q_1$ and $q_2$ are the controls, they flip the phase, so the result is indeed `011`.

3.  **Draft the Reasoning Steps:**
    *   *Goal:* Implement Bernstein-Vazirani to find secret string $s=011$.
    *   *Qubits:* 4 qubits ($q_0, q_1, q_2$ for input, $q_3$ for ancilla). All 4 are measured.
    *   *Init:* Start with $|0000\rangle$.
    *   *Preparation:* Apply $X$ then $H$ to $q_3$ to get $|-\rangle$. Apply $H$ to $q_0, q_1, q_2$ to get $\frac{1}{\sqrt{8}} \sum |x\rangle_{012} |-\rangle_3$.
    *   *Oracle:* Apply CNOTs from $q_1$ and $q_2

## isqTrain/3321

- task_id: `isqTrain/3321`
- task_type: `code_generation`
- category: `bernstein_vazirani`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`
- source: `isq_train_cot`
- dataset_index: `3165`

### Prompt

帮我写一个isQ程序：an isQ program: Bernstein-Vazirani with secret s=001.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement the Bernstein-Vazirani algorithm to find a hidden binary string $s=001$.
2. **Qubits**: 4 qubits are used ($q[0..2]$ for input, $q[3]$ for output); all are measured.
3. **Initialization**: Start in $|0000\rangle$, apply X to $q[3]$ to get $|0001\rangle$.
4. **Superposition**: Apply H to all qubits to reach $\frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^

## isqTrain/3138

- task_id: `isqTrain/3138`
- task_type: `code_generation`
- category: `bernstein_vazirani`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1323`

### Prompt

请用isQ语言编写一个量子电路：an isQ program: Bernstein-Vazirani algorithm with secret string s=11. Use 2 query qubits + 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement the Bernstein-Vazirani algorithm to find the secret binary string $s=11$.
2. **Qubits**: 3 total ($q[0], q[1]$ for the query register, $q[2]$ for the ancilla). All 3 are measured.
3. **State Evolution**:
   - Initialize to $|000\rangle$. Apply $X(q[2])$ and Hadamard to all qubits: state becomes $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes |-\rangle$.
   - Apply the oracle for $s=11$ via $CNOT(q[0], q[2])$ and $CNOT(q[1], q[2])$. This flips the ancilla phase for $|10\rangle$ and $|01\rangle$, yielding $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle) \otimes |-\rangle$.
   - Apply $H$ to $q[0]$ and $q[1]$. The query register interferes exactly to $|11\rangle$, resulting in the final state $|11\rangle \otimes |-\rangle$.
4. **Measurement**: Measuring yields $|11\rangle$ for the query qubits, revealing the secret string. The ancilla remains in $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$, yielding $|110\rangle$ and $|111\rangle$ with 50% probability each.

## isqTrain/3136

- task_id: `isqTrain/3136`
- task_type: `code_generation`
- category: `bernstein_vazirani`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `110`

### Prompt

Code this in isQ: an isQ program: Bernstein-Vazirani algorithm with secret string s=01. Use 2 query qubits + 1 ancilla.

### Chain-of-thought reasoning

Let me trace through the Bernstein-Vazirani algorithm with secret string s=01.

1. Goal: Find the secret string s=01 using the Bernstein-Vazirani algorithm.

2. Qubits: 3 qubits total (q[0], q[1] are query qubits, q[2] is ancilla). All 3 are measured.

3. State evolution:
- Initial: |000>
- After X(q[2]): |001>
- After H(q[2]): (|000> - |001>)/√2 = |00>|-> = |00>(|0> - |1>)/√2
- After H(q[0]), H(q[1]): (|00> + |01> + |10> + |11>)|-> /2

Wait, let me be more careful.

Initial state: |000>

After X(q[2]): |001>

After H(q[2]): (|000> - |001>)/√2

After H(q[0]), H(q[1]): The query register becomes (|00> + |01> + |10> + |11>)/2, so the full state is:
(|000> + |010> + |100> + |110> - |001> - |011> - |101> - |111>) / (2√2)

= (|00> + |01> + |10> + |11>) ⊗ (|0> - |1>) / (2√2)

Actually, let me rewrite:
= (|0> + |1>)_0 ⊗ (|0> + |1>)_1 ⊗ (|0> - |1>)_2 / (2√2)

Wait, that's not right either. Let me be careful with the ordering.

Full state after Hadamards:
= Σ_x |x>|-> / 2 where x ranges over 00, 01, 10, 11

Now oracle: f(x) = s·x = 01 · x = x_1 (the second bit of x)

The oracle applies phase kickback: |x>|-> → (-1)^{f(x)}|x>|->

So for each x:
- x=00: s·x = 0, phase = +1
- x=01: s·x = 0·0 + 1·1 = 1, phase = -1
- x=10: s·x = 0·1 + 1·0 = 0, phase = +1
- x=11: s·x = 0·1 + 1·1 = 1, phase = -1

Wait, s = 01 means s_0 = 0, s_1 = 1. So s·x = s_0·x_0 + s_1·x_1 = 0·x_0 + 1·x_1 = x_1.

So the oracle flips the ancilla based on x_1 (which is q[1]).

The CNOT(q[1], q[2]) gate flips the ancilla when q[1] = |1>. This applies the phase (-1)^{x_1} to the query register.

After oracle:
Σ_x (-1)^{x_1} |x>|-> / 2

= (|00> - |01> + |10> - |11>) |-> / 2

After final H(q[0]), H(q[1]):
H⊗2 (|00> - |01> + |10> - |11>) / 2 ⊗ |->

H⊗2 on the query register:
|00> → |++>
|01> → |+->
|10> → |-+>
|11> → |-->

Wait, let me compute properly.

H⊗2 |00> = (|00> + |01> + |10> + |11>)/2
H⊗2 |01> = (|00> - |01> + |10> - |11>)/2
H⊗2 |10> = (|00> + |01> - |10> - |11>)/2
H⊗2 |11> = (|00> - |01> - |10> + |11>)/2

So H⊗2 (|00> - |01> + |10> - |11>) / 2
= [1/2 · (|00> + |01> + |10> + |11>)/2 
   - 1/2 · (|00> - |01> + |10> - |11>)/2
   + 1/2 · (|00> + |01> - |10> - |11>)/2
   -

## isqTrain/3137

- task_id: `isqTrain/3137`
- task_type: `code_generation`
- category: `bernstein_vazirani`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `710`

### Prompt

Implement a quantum circuit in isQ: an isQ program: Bernstein-Vazirani algorithm with secret string s=10. Use 2 query qubits + 1 ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Code generation for Bernstein-Vazirani algorithm with secret string s=10.
    *   Tool: isQ quantum programming language.
    *   Output: Only the reasoning section (starting with "## Reasoning"). Do NOT include code.
    *   Constraints: 3-8 lines (simple) to 15 lines (complex). Use Dirac notation.

2.  **Understand the Algorithm & Circuit:**
    *   Goal: Find a secret string $s=10$ (2 bits) using the Bernstein-Vazirani algorithm.
    *   Qubits: 3 total (q[0], q[1] for query, q[2] for ancilla).
    *   Initial state: $|000\rangle$
    *   Step 1: Prepare ancilla in $|-\rangle$. Apply $X$ to q[2], then $H$ to q[2]. State: $|00\rangle_q \otimes |-\rangle_a$.
    *   Step 2: Apply $H$ to query qubits q[0], q[1]. State: $|+\rangle|+\rangle|-\rangle = \frac{1}{2}\sum_{x \in \{0,1\}^2} |x\rangle|-\rangle$.
    *   Step 3: Oracle $U_f$. Since $s=10$, $f(x) = s \cdot x = x_1$. So, apply CNOT(q[1], q[2]). State: $\frac{1}{2}\sum_{x} (-1)^{x_1}|x\rangle|-\rangle$.
    *   Step 4: Apply $H$ to q[0], q[1]. State: $(-1)^{s_0}|s_0 s_1\rangle|-\rangle = |10\rangle_q \otimes |-\rangle_a$. (Wait, the standard BV maps to $|s\rangle$ or $-|s\rangle$. With $H^{\otimes 2} (-1)^{x_1} |x\rangle$ it evaluates to exactly $|10\rangle$ since $s_0=1, s_1=0$. Wait, $x_1$ corresponds to $s_1=1$? If $s=10$, $s_0=1, s_1=0$ (assuming standard little/big endian). Let's trace carefully.)
    *   Let's check standard BV: $|00\rangle |1\rangle \to H^{\otimes 2} \otimes H \to \sum |x\rangle |-\rangle$. Oracle adds phase $(-1)^{s \cdot x}$. Since $s=10$, $s \cdot x = 1 \cdot x_0 + 0 \cdot x_1 = x_0$. So the oracle is CNOT(q[0], q[2]). Then $H^{\otimes 2}$ transforms $(-1)^{x_0} |x\rangle$ back to $|10\rangle$. (If q[0] is bit 0, then $x_0$).
    *   Let's re-verify the provided circuit implementation: `CNOT(q[0], q[2]);`. This implies $s=01$ if q[0] is LSB, or $s=10$ if q[0] is MSB.
    *   Let's follow the reference's oracle. $s=10$ means q[0] is the '1' (MSB, or just bit 0 depending on notation). If $s=10$, and only CNOT(q[0], q[2]) is applied, the phase is $(-1)^{x_0}$. After $H^{\otimes 2}$, the state is $|10\rangle$ (if bit 0 is MSB) or $|01\rangle$ (if bit 0 is LSB).
    *   The prompt states: Expected measurement probabilities: `{|100>: 0.5, |101>: 0.5}`.
    *   Wait, The resulting probabilities should be $|100\rangle$ and $|101\rangle$.
    *   Let's trace state with circuit implementation: `CNOT(q[0], q[2])` followed by `H(q[0]) H(q[1])`.
        *   Before H: $\frac{1}{2}(|00\rangle - |10\rangle + |01\rangle - |11\rangle) |-\rangle$.
        *   After $H^{\otimes 2}$ on query: $H$ on q[0] takes $|0\rangle-|1\rangle \

## isqTrain/3139

- task_id: `isqTrain/3139`
- task_type: `code_generation`
- category: `bernstein_vazirani`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5046`

### Prompt

Create an isQ quantum circuit that an isQ program: Bernstein-Vazirani algorithm with secret string s=101. Use 3 query qubits + 1 ancilla.

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a concise step-by-step reasoning for an isQ Bernstein-Vazirani program with secret string $s=101$. The output must be a specific format starting with "## Reasoning" and include no code.
2.  **Algorithm Details**:
    *   Secret string $s = 101$.
    *   3 query qubits ($q_0, q_1, q_2$), 1 ancilla ($q_3$).
    *   Initial state: $|0000\rangle$.
    *   Step 1: $X(q_3) \implies |0001\rangle$.
    *   Step 2: $H(q_3) \implies |000\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |000\rangle \otimes |-\rangle$.
    *   Step 3: $H$ on $q_0, q_1, q_2 \implies \frac{1}{2\sqrt{2}} \sum_{x=0}^{7} |x\rangle \otimes |-\rangle$.
    *   Step 4: Oracle $U_f$. CNOT($q_0, q_3$) and CNOT($q_2, q_3$). This applies phase oracle: $(-1)^{x \cdot s} |x\rangle \otimes |-\rangle$.
    *   Step 5: $H$ on $q_0, q_1, q_2$. Converts phase to state: $|101\rangle \otimes |-\rangle$.
    *   Step 6: Measurement of $q_0, q_1, q_2, q_3$.
3.  **Drafting the reasoning**:
    *   Line 1: Goal (Find secret string $s=101$ using Bernstein-Vazirani).
    *   Line 2: Qubits & Measurement (4 qubits total: 3 query, 1 ancilla; all 4 measured).
    *   Line 3-5: State evolution ($|0000\rangle \xrightarrow{X_3, H} |+\rangle^{\otimes 3}|-\rangle \xrightarrow{U_f} \sum (-1)^{s\cdot x}|x\rangle|-\rangle \xrightarrow{H^{\otimes 3}} |101\rangle|-\rangle$).
    *   Line 6: Probabilities (Measurement yields $|1010\rangle$ or $|1011\rangle$ depending on ancilla state, each with 0.5 probability). Note: measurement array bitstring is earlier qubit = higher bit, so measuring $q_0, q_1, q_2, q_3$ gives $q_0$ as MSB? Let's check typical isQ output: usually $q_0$ is MSB. If $q_0, q_1, q_2$ is 101, ancilla is +/-, then bitstring is 1010 or 1011. Yes.
4.  **Refining concisely**:
    *   Goal: Implement Bernstein-Vazirani to find secret string $s=101$.
    *   Qubits: 4 qubits ($q[0..2]$ query, $q[3]$ ancilla); all measured.
    *   Evolution: Start $|0000\rangle \xrightarrow{X_3, H^{\otimes 4}} |{+}\rangle^{\otimes 3}|{-}\rangle$.
    *   Oracle: $CNOT_{0,3}, CNOT_{2,3}$ encodes $s=101$, applying phase kickback $\sum_x (-1)^{x \cdot s}|x\rangle|{-}\rangle$.
    *   Final ops: $H^{\otimes 3}$ on query register leaves $|101\rangle|-\rangle$.
    *   Probabilities: Ancilla $|-\rangle$ has 50% chance of $|0\rangle$/$|1\rangle$, yielding states $|1010\rangle$ or $|1011\rangle$ with $p=0.5$ each.
5.  **Formatting check**:
    *   Starts with "## Reasoning"
    *   No code blocks
    *   3-8 lines (we have ~5-6 logical lines).

Let's write it out:
## Reasoning
1. Goal: Implement the Bernstein-Vazirani algorithm to determine the secret string $s=101$.
2. Qubits: 4 total (3 query qubits $q[0..2]$, 1 ancilla

## isqTrain/3141

- task_id: `isqTrain/3141`
- task_type: `code_generation`
- category: `bernstein_vazirani`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5294`

### Prompt

I need an isQ program to an isQ program: Bernstein-Vazirani algorithm with secret string s=111. Use 3 query qubits + 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Bernstein-Vazirani algorithm to find secret string s=111 using phase kickback.

We use 4 qubits: q[0], q[1], q[2] (query register) and q[3] (ancilla). All are measured.

State evolution:
1. |0000> → X(q[3]) → |0001>
2. H(q[3]) → |000>|-> = |000>(|0>-|1>)/√2
3. H(q[0..2]) → (1/√8)Σ|x>|-> where x ∈ {0,1}³
4. CNOT(q[0],q[3]), CNOT(q[1],q[3]), CNOT(q[2],q[3]): Oracle applies phase (-1)^(s·x) for s=111 → (1/√8)Σ(-1)^(x₀⊕x₁⊕x₂)|x>|-> = |111>|->

5. H(q[0..2]) on query register: The Hadamard transform converts |s⟩ = |111⟩ back from the phase-encoded state

6. Final state: |111>|-> where the query register is |111> and ancilla remains in |->

Expected probabilities: Query qubits deterministically yield 111; ancilla in |-> = (|0>-|1>)/√2 gives 50/50 outcome, producing {|1110>: 0.5, |1111>: 0.5}

## isqTrain/3323

- task_id: `isqTrain/3323`
- task_type: `code_generation`
- category: `bernstein_vazirani`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`
- source: `isq_train_cot`
- dataset_index: `1442`

### Prompt

Write an isQ program that an isQ program: Bernstein-Vazirani with secret s=100.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement the Bernstein-Vazirani algorithm to find the 3-bit secret string $s=100$.
2. **Qubits**: Uses 4 qubits: 3 query qubits ($q[0..2]$) and 1 ancilla ($q[3]$).
3. **State Evolution**:
   - Initialize ancilla to $|1\rangle$: $X(q[3]) \rightarrow |0001\rangle$.
   - Apply Hadamards to all: $H^{\otimes 4} \rightarrow \frac{1}{2\sqrt{2}} \sum_{x \in \{0,1\}^3} |x\rangle \otimes |-\rangle$.
   - Apply oracle $U_f$ via `CNOT(q[0], q[3])` (encodes $s_0=1$): the phase kick

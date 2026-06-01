# ISQ training COT RAG corpus: amplitude_amplification shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3105

- task_id: `isqTrain/3105`
- task_type: `code_generation`
- category: `amplitude_amplification`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4883`

### Prompt

帮我写一个isQ程序：an isQ program: Grover's algorithm on 3 qubits to find |111>, 1 iteration.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement 1-iteration Grover's algorithm on 3 qubits to amplify the probability of measuring |111>.

All 3 qubits are initialized to |000> and measured at the end.

**Step-by-step evolution:**
1. **H⊗3** creates equal superposition: |ψ⟩ = 1/√8 Σ|x⟩ for x∈{0,...,7}
2. **Oracle (double-controlled-Z (ctrl @[c1, c2] Z(target)))** flips phase of |111⟩: |ψ⟩ = 1/√8(|000⟩+...+|110⟩ - |111⟩)
3. **Diffusion (H⊗3 X⊗3 double-controlled-Z (ctrl @[c1, c2] Z(target)) X⊗3 H⊗3)** reflects amplitudes about the mean:
   - Mean amplitude = (7·1/√8 - 1/√8)/8 = 3/(4√8

## isqTrain/3316

- task_id: `isqTrain/3316`
- task_type: `code_generation`
- category: `amplitude_amplification`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `5733`

### Prompt

I need an isQ program to an isQ program: Grover 2-qubit search for |11> but express the iteration count using a for loop (1 iteration).

### Chain-of-thought reasoning

Let me trace through the Grover 2-qubit search for |11> with 1 iteration.

**Goal**: Use Grover's algorithm to search for |11> on 2 qubits.

**Initial state**: |00>

**After H on both qubits**: (|00> + |01> + |10> + |11>)/2 = |+>

**Oracle for |11>**: The CZ gate applies a phase of -1 to |11>
State becomes: (|00> + |01> + |10> - |11>)/2

**Diffusion operator**: H⊗2 → X⊗2 → CZ → X⊗2 → H⊗2

After H⊗2: This transforms to the {|+>, |->, ...} basis
(1/2)(|+>|+> + |+>|-> + |->|+> - |->|->>) = let me compute more carefully.

Actually, let me compute step by step:

After oracle: (|00> + |01> + |10> - |11>)/2

After H⊗2 on both:
H|0> = |+>, H|1> = |->
So H⊗2|00> = |++>, H⊗2|01> = |+->, H⊗2|10> = |-+>, H⊗2|11> = |-->

State: (|++> + |+-> + |-+> - |-->)/2

In computational basis:
|++> = (|00>+|01>+|10>+|11>)/2
|+-> = (|00>-|01>+|10>-|11>)/2
|-+> = (|00>+|01>-|10>-|11>)/2
|--> = (|00>-|01>-|10>+|11>)/2

So state = (1/2)[(|00>+|01>+|10>+|11>)/2 + (|00>-|01>+|10>-|11>)/2 + (|00>+|01>-|10>-|11>)/2 - (|00>-|01>-|10>+|11>)/2]
= (1/4)[(|00>+|01>+|10>+|11>) + (|00>-|01>+|10>-|11>) + (|00>+|01>-|10>-|11>) - (|00>-|01>-|10>+|11>)]
= (1/4)[|00>(1+1+1-1) + |01>(1-1+1+1) + |10>(1+1-1+1) + |11>(1-1-1-1)]
= (1/4)[2|00> + 2|01> + 2|10> - 2|11>]

After X⊗2: |00> → |11>, |01> → |10>, |10> → |01>, |11> → |00>
State: (1/4)[2|11> + 2|10> + 2|01> - 2|00>]

After CZ: flips phase of |11>
State: (1/4)[-2|11> + 2|10> + 2|01> - 2|00>]

After X⊗2:
State: (1/4)[-2|00> + 2|01> + 2|10> - 2|11>]

Hmm wait, let me redo. After CZ flips sign of |11>:
State: (1/4)[2|11> - 2|10> ... no wait.

Let me redo more carefully.

After H⊗2 (diffusion step starts):
State = (1/4)[2|00> + 2|01> + 2|10> - 2|11>]

After X⊗2: swaps |0>↔|1>
State = (1/4)[2|11> + 2|10> + 2|01> - 2|00>]

After CZ: applies -1 phase to |11>
State = (1/4)[-2|11> + 2|10> + 2|01> - 2|00>]

After X⊗2:
State = (1/4)[-2|00> + 2|01> + 2|10> - 2|11>]

After H⊗2:
Need to apply H⊗2 to this state.

H⊗2|-2|00>) = -2|++>
H⊗2(2|01>) = 2|+->
H⊗2(2|10>) = 2|-+>
H⊗2(-2|11>) = -2|-->

= -2|++> +

## isqTrain/3251

- task_id: `isqTrain/3251`
- task_type: `code_generation`
- category: `amplitude_amplification`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2343`

### Prompt

Write isQ code for the following quantum task: an isQ program: prepare |11> on 2 qubits, then apply Grover-like circuit but with S gate (pi/2 phase) as oracle instead of Z.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |00>

Step 1: Prepare |11>
Apply X to both qubits: |00> → |11>

Step 2: Apply H to both qubits
|11> → H⊗H → (|0> - |1>)/√2 ⊗ (|0> - |1>)/√2 = (|00> - |01> - |10> + |11>)/2

Step 3: Apply S-phase oracle (controlled-S on |11>)
The controlled-S gate applies S to q[1] when q[0] is |1>.
S = diag(1, i), so S|0> = |0>, S|1> = i|1>

State before: (|00> - |01> - |10> + |11>)/2
- |00>: q[0]=0, no control → |00>
- |01>: q[0]=0, no control → |01>
- |10>: q[0]=1, S on q[1]=|0> → |10>
- |11>: q[0]=1, S on q[1]=|1> → i|11>

State after: (|00> - |01> - |10> + i|11>)/2

Step 4: Diffusion operator (H⊗H, X⊗X, CZ, X⊗X, H⊗H)

After H⊗H:
|00> → (|0>+|1>)/√2 ⊗ (|0>+|1>)/√2 = (|00>+|01>+|10>+|11>)/2
|01> → (|0>+|1>)/√2 ⊗ (|0>-|1>)/√2 = (|00>-|01>+|10>-|11>)/2
|10> → (|0>-|1>)/√2 ⊗ (|0>+|1>)/√2 = (|00>+|01>-|10>-|11>)/2
|11> → (|0>-|1>)/√2 ⊗ (|0>-|1>)/√2 = (|00>-|01>-|10>+|11>)/2

So after H⊗H:
(1/2)[(|00>+|01>+|10>+|11>)/2 - (|00>-|01>+|10>-|11>)/2 - (|00>+|01>-|10>-|11>)/2 + i(|00>-|01>-|10>+|11>)/2]

Let me collect terms for each basis state:

|00>: (1/2)[1/2 - 1/2 - 1/2 + i/2] = (1/4)(1 - 1 - 1 + i) = (1/4)(-1 + i)
|01>: (1/2)[1/2 + 1/2 - 1/2 - i/2] = (1/4)(1 + 1 - 1 - i) = (1/4)(1 - i)
|10>: (1/2)[1/2 - 1/2 - 1/2 - i/2] = (1/4)(1 - 1 - 1 - i) = (1/4)(-1 - i)
|11>: (1/2)[1/2 + 1/2 - 1/2 + i/2] = (1/4)(1 + 1 - 1 + i) = (1/4)(1 + i)

Wait, let me redo this more carefully.

State before diffusion H⊗H: (|00> - |01> - |10> + i|11>)/2

Applying H⊗H to each component:
H⊗H|00> = (|0>+|1>)⊗(|0>+|1>)/2 = (|00>+|01>+|10>+|11>)/2
H⊗H|01> = (|0>+|1>)⊗(|0>-|1>)/2 = (|00>-|01>+|10>-|11>)/2
H⊗H|10> = (|0>-|1>)⊗(|0>+|1>)/2 = (|00>+|01>-|10>-|11>)/2
H⊗H|11> = (|0>-|1>)⊗(|0>-|1>)/2 = (|00>-|01>-|10>+|11>)/2

After H⊗H:
(1/2)[(1)(|00>+|01>+|10>+|11>)/2 + (-1)(|00>-|01>+

## isqTrain/3106

- task_id: `isqTrain/3106`
- task_type: `code_generation`
- category: `amplitude_amplification`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`
- source: `isq_train_cot`
- dataset_index: `5599`

### Prompt

Write isQ code for the following quantum task: an isQ program: apply the 2-qubit Grover diffusion operator WITHOUT an oracle (identity oracle). The state remains uniform since diffusion reflects the uniform state onto itself.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

Goal: Apply the 2-qubit Grover diffusion operator without an oracle, showing that the uniform superposition state is unchanged.

The circuit uses 2 qubits, both measured.

State evolution:
1. Initial state: |00>
2. After H⊗H: |+>|+> = (|00> + |01> + |10> + |11>)/2 (uniform superposition)
3. Identity oracle: no change, state remains uniform
4. Diffusion operator = H⊗H → X⊗X → CZ → X⊗X → H⊗H

Let me trace through the diffusion operator on |+>|+>:

After H⊗H on |+>|+>: |00> (since H|+> = |0>)
After X⊗X on |00>: |11>
After CZ on |11>: -|11>
After X⊗X on -|11>: -|00>
After H⊗H on -|00>: -|+>|+> = -(uniform superposition)

Wait, but the uniform superposition is an eigenstate of the diffusion operator with eigenvalue 1, not -1. Let me reconsider.

Actually, let me be more careful. The diffusion operator is 2|s><s| - I where |s> is the uniform superposition.

For 2 qubits: |s> = (|00> + |01> + |10> + |11>)/2

D|s> = (2|s><s| - I)|s> = 2|s><s|s> - |s> = 2|s>(1) - |s> = |s>

So |s> is an eigenstate with eigenvalue +1. The diffusion operator reflects about |s>, so |s> maps to itself.

Now let me trace the implementation:
- Start: |s> = (|00>+|01>+|10>+|11>)/2
- H⊗H: |s> → |00> (because H|+> = |0>)

Wait, H|+> = |0>? Let me check:
H|+> = H(1/√2)(|0>+|1>) = (1/√2)(|0>+|1>+|0>-|1>)/√2... no

H|+> = H · (1/√2)(|0>+|1>) = (1/√2)[H|0>+H|1>] = (1/√2)[|+>+|->] = (1/√2)(1/√2)(|0>+|1>+|0>-|1>) = (1/√2)(2|0>/√2) = |0>

Yes, H|+> = |0>. Good.

So H⊗H|s> = |00>

Then X⊗X|00> = |11>
Then CZ|11> = -|11> (Z is applied to target when control is |1>, and Z|1> = -|1>)
Then X⊗X(-|11>) = -|00>
Then H⊗H(-|00>) = -|++> = -|s>... 

Hmm, that gives -|s>, not |s>. But The predicted output uniform distribution.

Actually, global phase doesn't affect measurement probabilities. So -|s> has the same measurement probabilities as |s>.

Actually wait, let me reconsider the diffusion operator implementation. The standard implementation of the diffusion operator for n qubits is:
H⊗n · (2|0><0| - I) · H⊗n

And (2|0><0| - I) can be implemented as X⊗n · CZ · X⊗n (for 2 qubits, using CZ to implement the controlled-Z which gives -1 to |11>, and the X gates convert |00> ↔ |11>).

So: H⊗H · X⊗X · CZ · X⊗X · H⊗H

Let me compute this:
X⊗X · CZ · X⊗X = 
- CZ applies -1 phase when both are |1>
- First X⊗X maps |00>→|11>, |01>→|10>, |10>→|01>, |11>→|00>
- Then CZ: |11>→-|11>, others unchanged
- Then X⊗X maps back

So the combined operation:
|00> → |11> → -|11> → -|00>
|01> → |10> → |10> → |01>
|10> → |01> → |01> → |10>
|11> → |00> → |00> → |11>

So X⊗X · CZ · X⊗X = diag(-1, 1, 1,

## isqTrain/3249

- task_id: `isqTrain/3249`
- task_type: `code_generation`
- category: `amplitude_amplification`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4372`

### Prompt

Code this in isQ: an isQ program: prepare |01> on 2 qubits, then apply Grover-like circuit but with S gate (pi/2 phase) as oracle instead of Z.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

**Goal**: Prepare a modified Grover's circuit with S gate (π/2 phase) as oracle instead of Z on 2 qubits.

**Initial state**: |00⟩

**Step 1: Hadamard on both qubits**
H⊗H |00⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 = |+⟩⊗|+⟩

**Step 2: S-phase oracle for |11⟩ (marked state)**
The oracle marks |11⟩ with an S gate (phase i). But wait, the problem says oracle for |01⟩.

Let me re-read the circuit:
- X(q[1]) - flips q[1]
- ctrl S(q[0], q[1]) - applies S to q[1] when q[0] is |1⟩
- X(q[1]) - flips q[1] back

So the sequence is:
1. X(q[1]): |q0,q1⟩ → |q0, q1⊕1⟩. This means |00⟩→|01⟩, |01⟩→|00⟩, |10⟩→|11⟩, |11⟩→|10⟩
2. ctrl S(q[0], q[1]): applies S to q[1] when q[0]=1. This adds phase i to |11⟩ state (which was originally |10⟩)
3. X(q[1]): flips back

So the marked state is |10⟩ (not |01⟩).

Wait, let me re-read the problem. "prepare |01> on 2 qubits, then apply Grover-like circuit but with S gate (pi/2 phase) as oracle instead of Z."

Hmm, but The implementation starts with H(q[0]); H(q[1]); which prepares |++⟩, not |01⟩.

Let me look at The implementation more carefully. The oracle:
- X(q[1])
- ctrl S(q[0], q[1])
- X(q[1])

This marks the state where q[0]=1 and q[1]=0 (before X on q[1])... no wait.

Let me trace more carefully:

After H⊗H: (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

After X(q[1]): (|01⟩ + |00⟩ + |11⟩ + |10⟩)/2

After ctrl S(q[0], q[1]): S gate on q[1] when q[0]=1. S|0⟩=|0⟩, S|1⟩=i|1⟩.
- |01⟩: q[0]=0, no change → |01⟩
- |00⟩: q[0]=0, no change → |00⟩
- |11⟩: q[0]=1, S on q[1]=|1⟩ → i|11⟩
- |10⟩: q[0]=1, S on q[1]=|0⟩ → |10⟩

So state becomes: (|01⟩ + |00⟩ + i|11⟩ + |10⟩)/2

After X(q[1]): (|00⟩ + |01⟩ + i|10⟩ + |11⟩)/2

So the |10⟩ component got phase i. That's the marked state.

**Diffusion operator**: H⊗H, then X⊗X, then CZ, then X⊗X, then H⊗H

State after oracle: (|00⟩ + |01⟩ + i|10⟩ + |11⟩)/2

Let me compute diffusion step by step.

After H⊗H:
The diffusion operator D = 2|++⟩⟨++| - I

Actually, let me just compute the diffusion step by step.

After oracle: ψ = (|00⟩ + |01⟩ + i|10⟩ + |11⟩)/2

Apply H⊗H:
|00⟩ → (|00⟩+|01⟩+|10⟩+|11⟩)/2
|01⟩ → (|00⟩-|01⟩+|10⟩-|11⟩)/2
|10⟩ → (|00⟩+|01⟩-|10⟩-|11⟩)/2
|11⟩ → (|00⟩-|01⟩-|10⟩+|11⟩)/2

ψ' = [(|00⟩+|01⟩+|10⟩+|11⟩) + (|00⟩-|01⟩+|10⟩-|11⟩) + i(|00⟩+|01⟩-|10⟩-|11⟩) + (|00⟩-|01⟩-|10⟩+|11⟩)]/4

= [(1+1+i+1)|00⟩ + (1-

## isqTrain/3104

- task_id: `isqTrain/3104`
- task_type: `code_generation`
- category: `amplitude_amplification`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2082`

### Prompt

用isQ实现an isQ program: Grover's algorithm on 3 qubits to find |000>, 1 iteration.

### Chain-of-thought reasoning

The user wants a reasoning section for a Grover's algorithm on 3 qubits searching for |000>.

1.  **Goal**: Implement Grover's algorithm on 3 qubits to find the state |000>, using exactly one iteration.
2.  **Qubits**: 3 qubits, all measured.
3.  **State Evolution**:
    *   **Initialization**: |000>
    *   **Superposition**: Apply H to all. State becomes $|+\rangle^{\otimes 3} = \frac{1}{2\sqrt{2}} \sum_{x=0}^{7} |x\rangle$.
    *   **Oracle (Mark |000>)**:
        *   The standard oracle flips the phase of the target state.
        *   To use a double-controlled-Z (ctrl @[c1, c2] Z(target)) gate (which marks |111>), we flip all qubits first using X gates.
        *   $X^{\otimes 3}$ transforms $|000\rangle \to |111\rangle$ and all others to non-$|111\rangle$ states.
        *   double-controlled-Z (ctrl @[c1, c2] Z(target)) applies a phase of -1 to $|111\rangle$. This effectively marks the original $|000\rangle$ state with a -1 phase.
        *   Uncompute $X^{\otimes 3}$.
        *   State is now $\frac{1}{2\sqrt{2}} (|000\rangle \times (-1) + \text{others})$.
        *   Wait, let's trace it carefully.
        *   $H^{\otimes 3} |000\rangle = \frac{1}{\sqrt{8}} \sum |x\rangle$. Let $|w\rangle = |000\rangle$ be the winner. Let $|s\rangle = \frac{1}{\sqrt{8}} \sum |x\rangle$.
        *   The amplitude of $|w\rangle$ is $1/\sqrt{8}$. The sum of amplitudes of others is $7/\sqrt{8}$.
        *   Wait, the reflection $U_s$ (diffusion) is $2|s\rangle\langle s| - I$.
        *   The state after Oracle $U_w$ is $|w\rangle$ has amplitude $-1/\sqrt{8}$, others have $+1/\sqrt{8}$.
        *   Apply Diffusion: $H^{\otimes 3}$, $X^{\otimes 3}$, double-controlled-Z (ctrl @[c1, c2] Z(target)), $X^{\otimes 3}$, $H^{\otimes 3}$.
        *   The diffusion operator reflects around $|s\rangle$.
        *   Amplitude of $|w\rangle$ becomes $\frac{1}{\sqrt{8}} (\frac{6}{8} - (-\frac{1}{8})) = \frac{7}{8\sqrt{8}}$. Wait, standard formula: $a' = (1 - 2/8)(-1/8) + (2/8)(7/8) = (6/8)(-1/8) + 14/64 = -6/64 + 14/64 = 8/64 = 1/8$? No.
        *   Let's do the math: Initial amplitude of winner $a = 1/\sqrt{8}$.
        *   $a_{new} = \frac{N-2}{N} a + \frac{2(N-1)}{N} a \approx 3a$. Here $N=8$. So $a_{new}$ should be $\frac{6}{8}(-a) + \frac{2}{8}(7a) = \frac{14-6}{8} a = \frac{8}{8} a = a$? No.
        *   $U_s | \psi \rangle = 2 |s\rangle \langle s | \psi \rangle - | \psi \rangle$.
        *   $| \psi \rangle = a |w\rangle + \sum_{x \neq w} b |x\rangle$.
        *   After Oracle: $a = -1/\sqrt{8}$, $b = 1/\sqrt{8}$.
        *   $\langle s | \psi \rangle = -1/8 + 7/8 = 6/8 = 3/4$.
        *   $|s\rangle \langle s | \psi \rangle = (3/4) |s\rangle = (3/4) (1/\sqrt{8} \sum |x\rangle)$.
        *   $a' = 2(3/4)(1/\sqrt{8}) - (-1/\sqrt{8}) = 6/4

## isqTrain/3248

- task_id: `isqTrain/3248`
- task_type: `code_generation`
- category: `amplitude_amplification`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `490`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: prepare |00> on 2 qubits, then apply Grover-like circuit but with S gate (pi/2 phase) as oracle instead of Z.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

**Initial state**: |00⟩

**After H⊗H**: (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

**S-phase oracle** (applies S to q[1] controlled by q[0], with X gates before and after):
- After X⊗X: (1/2)(|11⟩ + |10⟩ + |01⟩ + |00⟩)
- After ctrl S(q[0], q[1]): applies S to q[1] when q[0]=|1⟩
  - |11⟩ → i|11⟩, |10⟩ → |10⟩, |01⟩ → i|01⟩, |00⟩ → |00⟩
  - State: (1/2)(i|11⟩ + |10⟩ + i|01⟩ + |00⟩)
- After X⊗X: (1/2)(i|00⟩ + |01⟩ + i|10⟩ + |11⟩)

**Diffusion operator** (H⊗H, X⊗X, CZ, X⊗X, H⊗H):

After H⊗H:
(1/2)[i(H⊗H)|00⟩ + (H⊗H)|01⟩ + i(H⊗H)|10⟩ + (H⊗H)|11⟩]

H⊗H|00⟩ = (1/2)(|00⟩+|01⟩+|10⟩+|11⟩)
H⊗H|01⟩ = (1/2)(|00⟩-|01⟩+|10⟩-|11⟩)
H⊗H|10⟩ = (1/2)(|00⟩+|01⟩-|10⟩-|11⟩)
H⊗H|11⟩ = (1/2)(|00⟩-|01⟩-|10⟩+|11⟩)

Sum = (1/2)[i(1/2)(|00⟩+|01⟩+|10⟩+|11⟩) + (1/2)(|00⟩-|01⟩+|10⟩-|11⟩) + i(1/2)(|00⟩+|01⟩-|10⟩-|11⟩) + (1/2)(|00⟩-|01⟩-|10⟩+|11⟩)]

= (1/4)[(i+1+i+1)|00⟩ + (i-1+i-1)|01⟩ + (i+1-i-1)|10⟩ + (i-1-i+1)|11⟩]

= (1/4)[(2+2i)|00⟩ + (-2+2i)|01⟩ + 0|10⟩ + 0|11⟩]

= (1/4)(2+2i)|00⟩ + (1/4)(-2+2i)|01⟩

After X⊗X:
= (1/4)(2+2i)|11⟩ + (1/4)(-2+2i)|10⟩

After CZ (applies -1 when both are |1⟩):
= (1/4)(2+2i)(-1)|11⟩ + (1/4)(-2+2i)|10⟩
= -(1/4)(2+2i)|11⟩ + (1/4)(-2+2i)|10⟩

After X⊗X:
= -(1/4)(2+2i)|00⟩ + (1/4)(-2+2i)|01⟩

After H⊗H:
Let me denote α = -(1/4)(2+2i) = -(1+i)/2 and β = (1/4)(-2+2i) = (-1+i)/2

State = α(H⊗H)|00⟩ + β(H⊗H)|01⟩

= α(1/2)(|00⟩+|01⟩+|10⟩+|11⟩) + β(1/2)(|00⟩-|01⟩+|10⟩-|11⟩)

= (1/2)[(α+β)|00⟩ + (α-β)|01⟩ + (α+β)|10⟩ + (α-β)|11⟩]

α+β = -(1+i)/2 + (-1+i)/2 = (-1-i-1+i)/2 = -2/2 = -1
α-β = -(1+i)/2 - (-1+i)/2 = (-1-i+1-i)/2 = -2i/2 = -i

So final state = (1/2)[-1|00⟩ - i|01⟩ - 1|10⟩ - i|11⟩]

Probabilities:
|00⟩: |−1/2|² = 1/4 = 0.25
|01⟩: |−i

## isqTrain/3250

- task_id: `isqTrain/3250`
- task_type: `code_generation`
- category: `amplitude_amplification`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1049`

### Prompt

Code this in isQ: an isQ program: prepare |10> on 2 qubits, then apply Grover-like circuit but with S gate (pi/2 phase) as oracle instead of Z.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

1. Start with |00>

2. Apply H(q[0]); H(q[1]):
   |00> → (|0>+|1>)/√2 ⊗ (|0>+|1>)/√2 = (|00>+|01>+|10>+|11>)/2

3. S-phase oracle on |10>:
   First X(q[0]): |00>+|01>+|10>+|11>)/2 → (|10>+|11>+|00>+|01>)/2
   Then ctrl S(q[0], q[1]): applies S to q[1] when q[0]=|1>
   S = [[1,0],[0,i]], so |0>→|0>, |1>→i|1>
   (|10>+|11>+|00>+|01>)/2 → (|10>+i|11>+|00>+|01>)/2
   Then X(q[0]): (|00>+i|01>+|10>+|11>)/2

   So after oracle: (|00>+i|01>+|10>+|11>)/2

   Wait, let me redo this more carefully. The oracle should apply S phase to the |10> component.

   Actually, let me re-examine. The circuit does:
   - X(q[0]): flips q[0], so |10> becomes |00>, etc.
   - ctrl S(q[0], q[1]): applies S to q[1] when q[0]=|1>. But S acts on q[1].

   Hmm, let me think about what `ctrl S(q[0], q[1])` means. In isQ, `ctrl S(q[0], q[1])` means q[0] is the control, and S is applied to q[1]. But S is a single-qubit gate. So this is a controlled-S gate where q[0] controls whether S is applied to q[1].

   Controlled-S: if q[0] is |1>, apply S to q[1>.

   So starting from (|00>+|01>+|10>+|11>)/2 after H,H:

   X(q[0]): (|10>+|11>+|00>+|01>)/2
   
   ctrl S(q[0], q[1]): When q[0]=|1>, apply S to q[1].
   |10> → |1>(S|0>) = |10> (S|0>=|0>)
   |11> → |1>(S|1>) = i|11> (S|1>=i|1>)
   |00> → |00> (control not activated)
   |01> → |01> (control not activated)
   
   Result: (|10>+i|11>+|00>+|01>)/2

   X(q[0]): (|00>+i|01>+|10>+|11>)/2

   So the state after the oracle is: (|00>+i|01>+|10>+|11>)/2

   The |01> component has an extra phase of i compared to others.

4. Diffusion: H(q[0]); H(q[1]);
   
   Apply H⊗H to (|00>+i|01>+|10>+|11>)/2:
   
   H⊗H |00> = (|00>+|01>+|10>+|11>)/2
   H⊗H |01> = (|00>-|01>+|10>-|11>)/2
   H⊗H |10> = (|00>+|01>-|10>-|11>)/2
   H⊗H |11> = (|00>-|01>-|10>+|11>)/2
   
   So:
   (1/2)[(|00>+|01>+|10>+|11>)/2 + i(|00>-|01>+|10>-|11>)/2 + (|00>+|01>-|10>-|11>)/2 + (|00>-|01>-|10>+|11>)/2]
   
   = (1/4)[(1+i+1+1)|00> + (1-i+1-1)|01> + (1+i-1-1)|10> + (1-i-1+1)|11>]
   
   Coefficient of |00>: (1+i+1+1) = (3+i)
   Coefficient of |01>: (1-i+1-1) = (1-i)
   Coefficient of |10>: (1+i-1-1) = (-1+i)
   Coefficient of |11>: (1-i-1+1

## isqTrain/3107

- task_id: `isqTrain/3107`
- task_type: `code_generation`
- category: `amplitude_amplification`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`
- source: `isq_train_cot`
- dataset_index: `1772`

### Prompt

Create an isQ quantum circuit that an isQ program: apply the 3-qubit Grover diffusion operator WITHOUT an oracle (identity oracle). The state remains uniform since diffusion reflects the uniform state onto itself.

### Chain-of-thought reasoning

Let me analyze this 3-qubit Grover diffusion operator without an oracle.

1. Goal: Apply the 3-qubit Grover diffusion operator with identity oracle, demonstrating that diffusion reflects the uniform superposition onto itself.

2. Qubits: 3 qubits (q[0], q[1], q[2]), all measured.

3. Step-by-step evolution:
   - Initial state: |000⟩
   - After H on all qubits: (H⊗H⊗H)|000⟩ = 1/(2√2) Σ|x⟩ for x∈{0,1}³ = |s⟩ (uniform superposition)
   - Identity oracle: state unchanged, still |s⟩
   - Diffusion operator D = 2|s⟩⟨s| - I
   - D|s⟩ = 2|s⟩⟨s|s⟩ - |s⟩ = 2|s⟩ - |s⟩ = |s⟩
   - The diffusion operator reflects |s⟩ onto itself since ⟨s|s⟩ = 1
   
   Breaking down the diffusion implementation:
   - H⊗H⊗H: transforms |s⟩ back to |000⟩
   - X⊗X⊗X: transforms |000⟩ to |111⟩
   - ctrl ctrl Z: applies -1 phase to |111⟩ (this is a controlled-controlled-Z, which flips phase of |111⟩)
   - Wait, let me reconsider. The standard diffusion is 2|s⟩⟨s| - I.
   
   Actually, the implementation:
   - H⊗H⊗H applied to uniform state |s⟩ gives |000⟩
   - X⊗X⊗X flips all qubits: |000⟩ → |111⟩
   - double-controlled-Z (ctrl @[c1, c2] Z(target)) (controlled-controlled-Z): this applies Z to the target when both controls are |1⟩. But wait, this is written as `ctrl ctrl Z(q[0], q[1], q[2])` which means q[0] and q[1] are controls and q[2] is target. So this is a Toffoli-like gate with Z instead of X, applying -1 phase only to |110⟩ component... 
   
   Actually no, let me think again. The double-controlled-Z (ctrl @[c1, c2] Z(target)) gate in this context: when q[0]=1 and q[1]=1, apply Z to q[2]. Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩. So this only adds -1 phase when all three qubits are |1⟩ (since if q[0]=1, q[1]=1, q[2]=1, then Z applied to q[2] gives -|1⟩, making state -|111⟩). So this is effectively a phase flip on |111⟩ only.
   
   Wait, but in the diffusion operator, after H and X, the state is |111⟩. So the double-controlled-Z (ctrl @[c1, c2] Z(target)) flips the phase of |111⟩ to -|111⟩. Then X and H transform back.
   
   The standard diffusion implementation is:
   D = H⊗3 (2|0⟩⟨0| - I) H⊗3
   And 2|0⟩⟨0| - I = X⊗3 |111⟩⟨111|... no wait.
   
   Actually 2|0⟩⟨0| - I = -(I - 2|0⟩⟨0|) = -(phase oracle for |0...0⟩)
   
   Hmm, let me think more carefully. The diffusion operator is:
   D = 2|s⟩⟨s| - I where |s⟩ = H⊗3|0⟩
   
   D = H⊗3 (2|0⟩⟨0| - I) H⊗3
   
   Now 2|0⟩⟨0| - I = |0⟩⟨0| - |1⟩⟨1| - ... - |7⟩⟨7| + 2|0⟩⟨0| = -I + 2|0⟩⟨0|
   
   This can be implemented as: flip phase of all states except |000⟩.
   Or equivalently: flip phase of |000⟩ and then flip phase of all states (global phase).
   
   The standard trick: 
   - Apply X to all qubits: |000⟩ → |111⟩
   - Apply double-controlled-Z (ctrl @[c1, c2] Z(target)): flip phase of |111⟩
   - Apply X to all qubits: |111⟩ → |000⟩
   
   This gives the transformation: flip phase of |000⟩ and keep others unchanged. But we need to flip phase of all except |000⟩, which means we need an additional global phase flip.
   
   Actually, let's see: D = H⊗3 (I - 2|0⟩⟨0|) H⊗3 with a global

## isqTrain/3103

- task_id: `isqTrain/3103`
- task_type: `code_generation`
- category: `amplitude_amplification`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2687`

### Prompt

Create an isQ quantum circuit that an isQ program: Grover's algorithm on 2 qubits to find |00>. Use 1 iteration with the appropriate oracle.

### Chain-of-thought reasoning

The user wants a reasoning section for a Grover's algorithm on 2 qubits to find |00>.

1. Goal: Find |00> using Grover's algorithm.
2. Qubits: 2 qubits q[0], q[1] (both measured).
3. Step-by-step evolution:
   - Initialize: |00>
   - H on both: 1/2(|00> + |01> + |10> + |11>)
   - Oracle for |00>:
     - X on both: 1/2(|11> + |10> + |01> + |00>)
     - CZ: flips sign of |11>: 1/2(-|11> + |10> + |01> + |00>)
     - X on both: 1/2(-|00> + |01> + |10> + |11>)
   - Diffusion:
     - H on both: 1/2(-|00> - |01> - |10> + |11>)  ... wait let me recalculate
     
Let me redo this more carefully.

Initial: |00>

After H on both:
1/2 (|00> + |01> + |10> + |11>)

Oracle marks |00>:
- X on both qubits transforms |00>→|11>, |01>→|10>, |10>→|01>, |11>→|00>
  State becomes: 1/2 (|11> + |10> + |01> + |00>)
- CZ(q[0], q[1]): flips sign of |11>
  State becomes: 1/2 (-|11> + |10> + |01> + |00>)
- X on both qubits:
  -|11> → -|00>
  |10> → |01>
  |01> → |10>
  |00> → |11>
  State becomes: 1/2 (-|00> + |01> + |10> + |11>)

So after oracle, the |00> amplitude is -1/2 while others are +1/2.

Diffusion operator:
D = 2|s><s| - I where |s> = H|0>|0> = 1/2(|00>+|01>+|10>+|11>)

Apply H, X, CZ, X, H to both qubits.

After H on both:
Let me compute H⊗H applied to 1/2(-|00> + |01> + |10> + |11>)

H|0> = |+> = 1/√2(|0>+|1>)
H|1> = |-> = 1/√2(|0>-|1>)

H⊗H|00> = |++> = 1/2(|00>+|01>+|10>+|11>)
H⊗H|01> = |+-> = 1/2(|00>-|01>+|10>-|11>)
H⊗H|10> = |-+> = 1/2(|00>+|01>-|10>-|11>)
H⊗H|11> = |--> = 1/2(|00>-|01>-|10>+|11>)

So state after H⊗H:
1/2 * [-1/2(|00>+|01>+|10>+|11>) + 1/2(|00>-|01>+|10>-|11>) + 1/2(|00>+|01>-|10>-|11>) + 1/2(|00>-|01>-|10>+|11>)]
= 1/2 * 1/2 [(-1+1+1+1)|00> + (-1-1+1-1)|01> + (-1+1-1-1)|10> + (-1-1-1+1)|11>]
= 1/4 [2|00> - 2|01> - 2|10> - 2|11>]
= 1/2 [|00> - |01> - |10> - |11>]

After X on both:
= 1/2 [|11> - |10> - |01> - |00>]

After CZ: flips |11>:
= 1/2 [-|11> - |10> - |01> - |00>]
= -1/2 [|00> + |01> + |10> + |11>]

After X on both:
= -1/2 [|11> + |10> + |01> + |00>]
= -1/2 [|00> + |01> + |10> + |11>]

After H on both:
-1/2 * (H⊗H)(|00

# ISQ training COT RAG corpus: phase_oracle shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3145

- task_id: `isqTrain/3145`
- task_type: `code_generation`
- category: `phase_oracle`
- difficulty: `basic`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3989`

### Prompt

Write an isQ program that an isQ program: create a 1-qubit phase oracle that marks state |0> with a phase flip, then verify by creating superposition, applying oracle, and measuring in X-basis.

### Chain-of-thought reasoning

The user wants a reasoning section for a specific isQ quantum program.
The program creates a 1-qubit phase oracle that marks |0> with a phase flip, applies it to a superposition, and measures in the X-basis.

1. Goal: Create a phase oracle for |0> (Z gate on |0>) and verify its action by preparing |+>, applying the oracle to get |->, and measuring in the X-basis to yield |1> with 100% probability.
2. Qubits: 1 qubit (`q[0]`), which is measured.
3. State evolution:
   - Init: |0>
   - H(q[0]): |0> -> |+>
   - Oracle (X, Z, X): |+> -> XZX |+> = -Z |+> = -|-> = |-> (since XZX = -Z, but |+> and |-> are eigenvectors of Z. Actually, Z|+> = |->. So XZX|+> = XZ|1> = -X|1> = -|0> wait.
   Let's trace carefully:
   Start: |0>
   H: |+> = 1/√2 (|0> + |1>)
   X: |1>
   Z: -|1>
   X: -|0>
   Wait! The implementation says X(q[0]); Z(q[0]); X(q[0]); marks |0> with phase flip.
   Let's check:
   XZX |0> = XZ |1> = X |1> = |0> (Wait, Z|1> = -|1>. So X (-|1>) = -|0>)
   XZX |1> = XZ |0> = X |0> = |1>
   So XZX acts as -Z on the computational basis? No, XZX = -Z. It applies a -1 phase to |0> and a +1 phase to |1>. Wait.
   If |0> -> -|0> and |1> -> |1>, then XZX is actually -Z, which is a global phase shift for Z?
   Wait. Z|0> = |0>, Z|1> = -|1>.
   XZX|0> = -|0>. XZX|1> = |1>.
   So XZX applies -1 to |0> and +1 to |1>. This means XZX = -Z.
   Since global phase is unobservable, applying XZX to |+> yields -Z|+> = -|->. But this is physically the same as |->.
   Wait! Let's re-evaluate:
   H|0> = |+>
   Apply XZX to |+>: XZX|+> = XZ |1> = X (-|1>) = -|0>.
   Wait, is XZX|+> = -|->?
   X|1> = |0>, so X(-|1>) = -|0>. No! |-> = 1/√2 (|0> - |1>). -|0> is NOT |->.
   Let's re-trace XZX on |+>.
   |+> = (|0> + |1>) / √2
   XZX |+> = XZ |1> = X (-|1>) = -X |1> = -|0>.
   Wait. If XZX|+> = -|0>, then applying H gives -|1>, so measurement yields 1.
   Let's check the prompt's expected probabilities: {|1>: 1.0}.
   Yes!
   Trace again:
   Init: |0>
   H(q[0]): |+>
   X(q[0]): |1>
   Z(q[0]): -|1>
   X(q[0]): -|0>
   H(q[0]): -|1>
   Measurement: yields 1 with probability 1.0.

4. Reasoning:
   - Goal: Apply a phase oracle marking |0> with a phase flip and measure the result in the X-basis to verify.
   - Qubits: 1 qubit (`q[0]`), measured at the end.
   - Evolution:
     - `q[0]` starts in |0>.
     - `H(q[0])` creates the superposition |+>.
     - The sequence `X`, `Z`, `X` applies a phase flip to |0>. Applying this to |+> yields -|0>.
     - `H(q[0])` rotates -|0> into -|1>.
   - Probabilities: The final state is -|1>, so measuring `q[0]` yields 1 with 100% probability

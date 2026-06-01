# ISQ training COT RAG corpus: phase_estimation shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3301

- task_id: `isqTrain/3301`
- task_type: `code_generation`
- category: `phase_estimation`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1130`

### Prompt

Implement a quantum circuit in isQ: an isQ program: phase estimation building block. Apply H to q[0], ctrl Rz(2*pi/8) from q[0] to q[1] (target in |0>), H on q[0], measure both.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |00>

Step 1: H on q[0]
|00> → (1/√2)(|0> + |1>)|0> = (1/√2)(|00> + |10>)

Step 2: ctrl Rz(2π/8) from q[0] to q[1]

Wait, let me think about this more carefully. The controlled-Rz gate: when the control is |1>, apply Rz to the target.

Rz(θ) = [[1, 0], [0, e^(iθ)]]

So ctrl Rz(π/4, q[0], q[1]) means: when q[0] is |1>, apply Rz(π/4) to q[1].

Since q[1] is in |0>, Rz(π/4)|0> = |0> (Rz only adds a phase to |1>).

So the state after controlled-Rz is:
(1/√2)(|00> + |10>)

The controlled-Rz doesn't change anything because q[1] is |0>.

Step 3: H on q[0]
Apply H to q[0]:
(1/√2)(H|0>|0> + H|1>|0>)
= (1/√2)((1/√2)(|0>+|1>)|0> + (1/√2)(|0>-|1>)|0>)
= (1/2)(|00> + |10> + |00> - |10>)
= (1/2)(2|00>)
= |00>

Hmm, so the final state should be |00> with probability 1?

But the predicted output say {|00>: 0.9619, |10>: 0.0381}.

Wait, let me reconsider. The ctrl Rz might add a phase to the control qubit, not the target.

Actually, let me think about this more carefully. In isQ, `ctrl Rz(theta, q[0], q[1])` - what are the parameters?

Looking at the syntax: `ctrl @[c1, c2] Gate(target);`

So `ctrl Rz(2*pi/8, q[0], q[1])` would mean... wait, Rz takes (theta, qubit), so this is ambiguous.

Let me look at The implementation:

This is applying controlled-Rz with q[0] as control and q[1] as target. The rotation angle is 2π/8 = π/4.

But as I computed, if q[1] is in |0>, the controlled-Rz doesn't add any phase (Rz only phases |1>).

Hmm, but The resulting probabilities should be not exactly 1 and 0. Let me reconsider.

Oh wait, maybe the controlled-Rz applies a phase to the control state when it's |1>, regardless of the target state? No, that's not how controlled gates work.

Let me reconsider the problem. Actually, in phase estimation, we typically have an eigenstate of the unitary. Here, the target q[1] is in |0>, but |0> is an eigenstate of Rz with eigenvalue 1 (since Rz|0> = |0>).

So the phase is 0, and after applying H on q[0], we should get |0> on q[0] with certainty.

But The predicted output 0.9619 for |00> and 0.0381 for |10>. That's strange.

Wait, maybe the implementation of controlled-Rz in isQ is different. Let me think...

Actually, Rz(θ) = e^(-iθ/2) * [[1, 0], [0, e^(iθ)]] - there's a global phase factor!

So Rz(θ)|0> = e^(-iθ/2)|0>

This means Rz does add a phase to |0>! It's a global phase factor.

So controlled-Rz(π/4) when control is |1>:
|Rz(π/4)|0>_target = |e^(-iπ/8)|0>>

The state becomes:
(1/√2)(|00> + e^(-iπ/8)|10>)

Step 3: H on q[0]
= (1/√2)(H|0>|0> + e^(-iπ/8) H|1>|0>)
= (1/√2)((1/√2)(|0>+

## isqTrain/3302

- task_id: `isqTrain/3302`
- task_type: `code_generation`
- category: `phase_estimation`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2755`

### Prompt

实现以下量子计算任务（使用isQ）：an isQ program: phase estimation building block. Apply H to q[0], ctrl Rz(2*pi/16) from q[0] to q[1] (target in |0>), H on q[0], measure both.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement a phase estimation building block that uses Hadamard interference to detect the phase accumulated by a controlled-Rz rotation.

**Qubits:** 2 qubits (q[0] as control/interference, q[1] as target), both measured.

**State evolution:**
- Initial: |00⟩
- After H(q[0]): (|00⟩ + |10⟩)/√2
- After ctrl Rz(π/8): (|00⟩ + e^{-iπ/16}|10⟩)/√2 (phase on |10⟩ from Rz acting on |0⟩ of q[1])
- After H(q[0]): ½[(1 + e^{-iπ/16})|00⟩ + (1 - e^{-iπ/16})|10⟩]

**Probabilities:** P(|00⟩) = |1 + e^{-iπ/16}|²/4 = cos²(π/32) ≈ 0.9904, P(|10⟩) = sin²(π/32

## isqTrain/3304

- task_id: `isqTrain/3304`
- task_type: `code_generation`
- category: `phase_estimation`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2672`

### Prompt

Write an isQ program that an isQ program: phase estimation building block. Apply H to q[0], ctrl Rz(2*pi/64) from q[0] to q[1] (target in |0>), H on q[0], measure both.

### Chain-of-thought reasoning

Let me analyze this phase estimation building block circuit step by step.

## Initial State
We start with |q[0]⟩|q[1]⟩ = |0⟩|0⟩ = |00⟩

## Step 1: Apply H to q[0]
H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2

State becomes: (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2

## Step 2: Apply ctrl Rz(2π/64) from q[0] to q[1]

The Rz(θ) gate is: [[1, 0], [0, e^(iθ)]]

When applied with control, if q[0] is |1⟩, Rz is applied to q[1].

Since q[1] is in |0⟩, Rz(θ)|0⟩ = |0⟩ (the phase only applies to |1⟩).

So the controlled-Rz on |0⟩ target does nothing visible - it applies a phase of e^(iθ) only when the target is |1⟩.

Wait, let me reconsider. The controlled-Rz gate applies Rz to the target qubit when the control is |1⟩. Since q[1] is in |0⟩:

Rz(θ)|0⟩ = |0⟩ (just adds global phase factor of 1 to |0⟩ component)
Rz(θ)|1⟩ = e^(iθ)|1⟩

So on |0⟩, Rz just gives |0⟩ with no phase change (the diagonal is [1, e^(iθ)]).

Therefore the controlled-Rz does nothing to our state since q[1] is |0⟩.

Wait, but that would mean the output should be |00⟩ with 50% and |10⟩ with 50% after the final H.

Hmm, let me reconsider the Rz gate definition.

Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]

Actually, there are different conventions. Let me check the isQ convention.

In the isQ syntax reference, it mentions:
- Z = [[1,0],[0,-1]]
- S = [[1,0],[0,i]]
- T = [[1,0],[0,e^(i*pi/4)]]

So Rz(θ) should be consistent with Z being Rz(π). Let's check:
- Rz(π) = [[e^(-iπ/2), 0], [0, e^(iπ/2)]] = [[-i, 0], [0, i]] ≠ Z

Hmm, so maybe isQ uses Rz(θ) = [[1, 0], [0, e^(iθ)]] which is the phase gate convention.

Actually looking at standard definitions:
- If Rz(θ) = [[1, 0], [0, e^(iθ)]], then Rz(π) = [[1, 0], [0, -1]] = Z. This matches!

So Rz(θ) in isQ is likely [[1, 0], [0, e^(iθ)]].

With this convention:
Rz(2π/64)|0⟩ = |0⟩
Rz(2π/64)|1⟩ = e^(i·2π/64)|1⟩ = e^(iπ/32)|1⟩

So controlled-Rz on |10⟩ gives |1⟩⊗Rz(2π/64)|0⟩ = |10⟩ (no change since target is |0⟩).

The state remains (|00⟩ + |10⟩)/√2.

## Step 3: Apply H to q[0]
H(|0⟩ + |1⟩)/√2 ⊗ |0⟩ 

The H gate on q[0]:
H|0⟩ = |+⟩
H|1⟩ = |−⟩

So H((|0⟩ + |1⟩)/√2) = H|+⟩ = |0⟩

Wait, that's not right. Let me redo:

H(|0⟩ + |1⟩)/√2 = (H|0⟩ + H|1⟩)/√2 = (|+⟩ + |−⟩)/√2 = |0⟩

So the state becomes |0⟩⊗|0⟩ = |00⟩.

This would give 100% |00⟩, but The predicted output {|00>: 0.9994, |10>: 0.0006}.

There's something wrong with my analysis. Let me reconsider.

Oh wait! I think the issue is that controlled-Rz might actually apply a phase to the control qubit, not just apply Rz to the target

## isqTrain/3303

- task_id: `isqTrain/3303`
- task_type: `code_generation`
- category: `phase_estimation`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1854`

### Prompt

Help me write isQ code that an isQ program: phase estimation building block. Apply H to q[0], ctrl Rz(2*pi/32) from q[0] to q[1] (target in |0>), H on q[0], measure both.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

1. Initial state: |00⟩

2. Apply H to q[0]: (H⊗I)|00⟩ = |+⟩|0⟩ = (1/√2)(|0⟩ + |1⟩)|0⟩ = (1/√2)(|00⟩ + |10⟩)

3. Apply ctrl Rz(2π/32, q[0], q[1]):
   - When q[0] is |1⟩, apply Rz(2π/32) to q[1]
   - Rz(θ) = [[1,0],[0,e^(iθ)]]
   - When q[1] is |0⟩, Rz only applies a phase of 1, so the state remains unchanged
   - Actually wait, Rz(θ)|0⟩ = |0⟩ and Rz(θ)|1⟩ = e^(iθ)|1⟩
   - So when q[1] = |0⟩, the controlled-Rz does nothing regardless of q[0]
   - State remains: (1/√2)(|00⟩ + |10⟩)

4. Apply H to q[0]:
   - (H⊗I)(1/√2)(|00⟩ + |10⟩)
   - = (1/√2)(H|0⟩|0⟩ + H|1⟩|0⟩)
   - = (1/√2)(|+⟩|0⟩ + |−⟩|0⟩)
   - = (1/√2)((1/√2)(|0⟩+|1⟩)|0⟩ + (1/√2)(|0⟩−|1⟩)|0⟩)
   - = (1/2)(|00⟩ + |10⟩ + |00⟩ − |10⟩)
   - = (1/2)(2|00⟩)
   - = |00⟩

So the final state is |00⟩ with probability 1.

But the expected measurement probabilities say {|00⟩: 0.9976, |10⟩: 0.0024}. This doesn't match |00⟩ with probability 1.

Let me reconsider. Maybe I'm misunderstanding the ctrl gate syntax. Let me look again:

`ctrl Rz(2*pi/32, q[0], q[1])` - this means q[0] is control, q[1] is target. So when q[0] is |1⟩, apply Rz to q[1].

But wait, Rz on |0⟩ just gives |0⟩ (no phase change for |0⟩ state). So the controlled-Rz has no effect when the target is in |0⟩.

Hmm, but the predicted output show it's not exactly |00⟩. Let me re-read...

Oh wait, maybe there's something about the convention of Rz. Some conventions include a global phase: Rz(θ) = e^(-iθ/2)[[e^(iθ/2), 0], [0, e^(-iθ/2)]] = [[1, 0], [0, e^(-iθ)]]... no that's not right either.

Standard Rz(θ) = [[1,0],[0,e^(iθ)]]

So Rz(θ)|0⟩ = |0⟩, Rz(θ)|1⟩ = e^(iθ)|1⟩

When the target q[1] is in |0⟩, the controlled-Rz has no effect on the state at all.

So after the controlled-Rz, state is still (1/√2)(|00⟩ + |10⟩)

Then H on q[0]:
H|0⟩ = |+⟩ = (1/√2)(|0⟩ + |1⟩)
H|1⟩ = |−⟩ = (1/√2)(|0⟩ − |1⟩)

(H⊗I)(1/√2)(|00⟩ + |10⟩) = (1/√2)(|+0⟩ + |−0⟩) = (1/√2)(1/√2)(|0⟩+|1⟩)|0⟩ + (1/√2)(|0⟩−|1⟩)|0⟩)
= (1/2)(|00⟩ + |10⟩ + |00⟩ − |10⟩) = (1/2)(2|00⟩) = |00⟩

So probability of |00⟩ should be 1. But the expected says 0.9976 for |00⟩.

There must be something I'm missing. Let me think about this differently...

Actually, wait. Maybe the issue is with how isQ defines controlled operations. In some frameworks, a controlled gate applies the gate when the control is |0⟩, not |1⟩. But that's unusual

## isqTrain/3300

- task_id: `isqTrain/3300`
- task_type: `code_generation`
- category: `phase_estimation`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `957`

### Prompt

Code this in isQ: an isQ program: phase estimation building block. Apply H to q[0], ctrl Rz(2*pi/4) from q[0] to q[1] (target in |0>), H on q[0], measure both.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

**Initial state:** |00⟩

**Step 1: H on q[0]**
H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2

State: (|00⟩ + |10⟩)/√2

**Step 2: ctrl Rz(2π/4) from q[0] to q[1]**

Rz(θ) = [[1, 0], [0, e^(iθ)]]

Rz(π/2) = [[1, 0], [0, e^(iπ/2)]] = [[1, 0], [0, i]]

The controlled-Rz applies Rz(π/2) to q[1] when q[0] is |1⟩.

Since q[1] is in |0⟩:
- When q[0] = |0⟩: |00⟩ → |00⟩ (no change)
- When q[0] = |1⟩: |10⟩ → |1⟩ ⊗ Rz(π/2)|0⟩ = |1⟩ ⊗ |0⟩ = |10⟩ (Rz(π/2)|0⟩ = |0⟩ since the first element is 1)

Wait, let me reconsider. Rz(π/2)|0⟩ = |0⟩ because the (0,0) element is 1. So actually, when the target is |0⟩, controlled-Rz doesn't change the state at all!

Hmm, but The resulting probabilities should be {|00⟩: 0.8536, |10⟩: 0.1464}, which are not 50/50. Let me reconsider.

Wait, maybe controlled-Rz in isQ also applies a phase to the control when the target is |0⟩? Or maybe the ctrl modifier works differently?

Actually, let me reconsider the controlled-Rz gate. The standard controlled-Rz applies a phase to the |11⟩ component. But Rz(θ) = diag(1, e^{iθ}). So controlled-Rz should be diag(1, 1, 1, e^{iθ}).

But if the target is |0⟩, then controlled-Rz doesn't do anything to the state (|00⟩ stays |00⟩, |10⟩ stays |10⟩).

Hmm, but The predicted output non-trivial probabilities. Let me re-examine.

Actually wait - maybe the issue is that in isQ, `ctrl Rz(theta, q[0], q[1])` means q[0] is control and q[1] is target, but the syntax might be different. Let me look at the reference code again:

So q[0] is the control and q[1] is the target for Rz. But Rz(θ) on |0⟩ gives |0⟩ (no change). So the controlled-Rz should not change the state at all when q[1] is |0⟩.

But The resulting probabilities should be {|00⟩: 0.8536, |10⟩: 0.1464}. Let me check if maybe there's something about how the ctrl modifier works with Rz in isQ.

Actually, wait. Let me reconsider. Maybe in isQ, the ctrl gate applies a global phase or something?

Actually, let me reconsider the problem. Maybe I need to think about what `ctrl Rz(theta, control, target)` actually does in isQ. 

Looking at the syntax: `ctrl @[c1, c2] Gate(target);` - so the qubits after @ are controls, and the argument to the gate is the target.

But in the reference code: `ctrl Rz(2.0*.../4.0, q[0], q[1]);` - this seems to have Rz taking two qubit arguments plus a theta. 

Hmm, in the reference, Rz has parameters (theta, q[0], q[1]). Maybe when used with ctrl, the first qubit after theta is the control and the second is the target? Or maybe Rz normally takes (theta, qubit) but with ctrl, it becomes ctrl Rz(theta, control, target)?

Actually, let me re-read the syntax. The reference says: `ctrl @[c1, c2] Gate(target);`. So the controls go in the @[] list, and the target is the regular argument.

But in the reference code, it's written as `ctrl Rz(2.0*.../4.0, q[0], q[1]);`. Maybe in this case, q[0] is implicitly the control (specified by ctrl modifier) and

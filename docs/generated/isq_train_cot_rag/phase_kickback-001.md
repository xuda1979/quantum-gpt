# ISQ training COT RAG corpus: phase_kickback shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3121

- task_id: `isqTrain/3121`
- task_type: `code_generation`
- category: `phase_kickback`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4769`

### Prompt

I need an isQ program to an isQ program: phase kickback with controlled-Rz(2*pi/16). Use 2 qubits. Apply X to q[1] (target |1>), H to q[0] (control), controlled Rz(2*pi/16) from q[0] to q[1], H on q[0], measure q[0] only. Add M(q[1]) too for completeness.

### Chain-of-thought reasoning

Let me analyze this phase kickback circuit step by step.

1. Goal: Demonstrate phase kickback with a controlled-Rz(2π/16) gate.

2. Qubits: 2 qubits (q[0] = control, q[1] = target), both measured.

3. Step-by-step evolution:
- Initial state: |00⟩
- After X(q[1]): |01⟩
- After H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |1⟩ = (|01⟩ + |11⟩)/√2
- After ctrl Rz(2π/16, q[0], q[1]):
  - When q[0] = |1⟩, Rz(2π/16) is applied to q[1]
  - Rz(θ)|1⟩ = e^{-iθ/2}|1⟩
  - So: (|01⟩ + e^{-iπ/16}|11⟩)/√2
  - The phase has kicked back to the control qubit!
- After H(q[0]): 
  - H on q[0] transforms: (|0⟩ + e^{-iπ/16}|1⟩)/√2 ⊗ |1⟩
  - Applying H to first qubit: |+⟩ → |0⟩, |-⟩ → |1⟩
  - Actually: H(|0⟩ + e^{-iθ}|1⟩)/√2 = cos(θ/2)|0⟩ - i sin(θ/2)|1⟩... 
  
  Let me recalculate. Rz(θ)|1⟩ = e^{-iθ/2}|1⟩

  After H(q[0]): (|01⟩ + e^{-iπ/16}|11⟩)/√2
  Apply H on q[0]:
  H|0⟩|1⟩ = |+⟩|1⟩
  H|1⟩|1⟩ = |−⟩|1⟩
  
  So: (|+⟩|1⟩ + e^{-iπ/16}|−⟩|1⟩)/√2
  = ((|0⟩ + |1⟩)/2 + e^{-iπ/16}(|0⟩ - |1⟩)/2)|1⟩
  = ((1 + e^{-iπ/16})|0⟩ + (1 - e^{-iπ/16})|1⟩)|1⟩/2
  
  P(|01⟩) = |1 + e^{-iπ/16}|²/4 = (1 + cos(π/16))²/4 + sin²(π/16)/4
  Actually: |1 + e^{-iπ/16}|² = 1 + 1 + 2cos(π/16) = 2 + 2cos(π/16) = 4cos²(π/32)
  P(|01⟩) = cos²(π/32) ≈ cos²(0.098) ≈ 0.9904... hmm

  Let me recalculate more carefully.
  
  θ = 2π/16 = π/8
  
  Rz(θ)|1⟩ = e^{-iθ/2}|1⟩ = e^{-iπ/16}|1⟩
  
  After controlled-Rz: (|01⟩ + e^{-iπ/16}|11⟩)/√2
  
  After H(q[0]):
  = ((1 + e^{-iπ/16})|01⟩ + (1 - e^{-iπ/16})|11⟩)/2
  
  P(|01⟩) = |1 + e^{-iπ/16}|²/4 = (2 + 2cos(π/16))/4 = (1 + cos(π/16))/2 = cos²(π/32)
  
  cos(π/32) ≈ cos(0.0982) ≈ 0.9952
  cos²(π/32) ≈ 0.9904

  But The predicted output 0.9619 and 0.0381... Let me check again.

  Wait, maybe I should check if the Rz convention is different. Let me reconsider.

  If Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]], then Rz(θ)|1⟩ = e^{iθ/2}|1⟩.

  So with θ = π/8:
  Rz(π/8)|1⟩ = e^{iπ/16}|1⟩
  
  After controlled-Rz: (|01⟩ + e^{iπ/16}|11⟩)/√2
  
  After H(q[0]):
  P(|01⟩) = |1 + e^{iπ/

## isqTrain/3120

- task_id: `isqTrain/3120`
- task_type: `code_generation`
- category: `phase_kickback`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4141`

### Prompt

用isQ实现an isQ program: phase kickback with controlled-Rz(2*pi/8). Use 2 qubits. Apply X to q[1] (target |1>), H to q[0] (control), controlled Rz(2*pi/8) from q[0] to q[1], H on q[0], measure q[0] only. Add M(q[1]) too for completeness.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Demonstrate phase kickback where a controlled-Rz(π/4) imparts a relative phase to the control qubit, observable via X-basis measurement.

**Qubits**: 2 (q[0] control, q[1] target); both measured.

**State evolution**:
1. **Init**: |00⟩
2. **X(q[1])**: |01⟩
3. **H(q[0])**: (|01⟩ + |11⟩)/√2
4. **ctrl Rz(π/4)**: Rz only acts when control=|1⟩; since target is |1⟩, Rz(π/4)|1⟩ = e^{iπ/8}|1⟩ → (|01⟩ + e^{iπ/8}|11⟩)/√2
5. **H(q[0])**: [(1+e^{iπ/8})|01⟩ + (1-e^{iπ/8})|11⟩]/2

**Probabilities**: P(|01⟩) = |1+e^{iπ/8}|²/4 = cos²(π/16) ≈ 0.9619; P(|11⟩) = |1-e^{iπ/8}|²/4 = sin²(π/16) ≈ 0.0381. The phase θ=π/4 is detected as amplitude ratio cos(θ/2):sin(θ/2) after kickback to the control.

## isqTrain/3119

- task_id: `isqTrain/3119`
- task_type: `code_generation`
- category: `phase_kickback`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2314`

### Prompt

Write an isQ program that an isQ program: phase kickback with controlled-Rz(2*pi/4). Use 2 qubits. Apply X to q[1] (target |1>), H to q[0] (control), controlled Rz(2*pi/4) from q[0] to q[1], H on q[0], measure q[0] only. Add M(q[1]) too for completeness.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |00⟩

1. X(q[1]): |00⟩ → |01⟩

2. H(q[0]): |01⟩ → (|0⟩ + |1⟩)/√2 ⊗ |1⟩ = (|01⟩ + |11⟩)/√2

3. ctrl Rz(2π/4) with q[0] as control, q[1] as target:
   Rz(π/2) = [[1, 0], [0, e^(iπ/2)]] = [[1, 0], [0, i]]
   
   When control is |1⟩, Rz(π/2) is applied to target. This means:
   - |01⟩ stays |01⟩ (control is |0⟩)
   - |11⟩ → e^(iπ/2)|11⟩ = i|11⟩ (control is |1⟩, Rz adds phase i to |1⟩ component of target)
   
   Wait, let me reconsider. The controlled-Rz applies Rz to the target when control is |1⟩. But the target qubit is already in |1⟩, so Rz(π/2)|1⟩ = e^(iπ/2)|1⟩ = i|1⟩.
   
   State becomes: (|01⟩ + i|11⟩)/√2

   This is the phase kickback - the phase is "kicked back" to the control qubit's |1⟩ component.
   
   In terms of the control qubit: |0⟩⊗|1⟩ + i|1⟩⊗|1⟩ = (|0⟩ + i|1⟩)⊗|1⟩/√2

4. H(q[0]): Apply H to the control qubit.
   H(|0⟩ + i|1⟩)/√2 = (|0⟩ + |1⟩ + i|0⟩ - i|1⟩)/(2) = ((1+i)|0⟩ + (1-i)|1⟩)/2
   
   Final state: ((1+i)|0⟩ + (1-i)|1⟩)⊗|1⟩/2

5. Measurement probabilities for q[0]:
   P(|0⟩) = |(1+i)/2|² = (1+i)(1-i)/4 = 2/4 = 0.5
   
   Wait, that doesn't match the predicted output. Let me reconsider.

Hmm, The resulting probabilities should be {|01⟩: 0.8536, |11⟩: 0.1464}. That's approximately cos²(π/8) and sin²(π/8). Let me re-examine.

Actually, wait. The controlled-Rz might be defined differently. In some definitions, Rz(θ) = e^(-iθZ/2) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]. In others, Rz(θ) = [[1, 0], [0, e^(iθ)]].

If Rz(θ) = [[1, 0], [0, e^(iθ)]] (no global phase), then:
Rz(π/2) = [[1, 0], [0, i]]

When applied controlled, to |11⟩, the target |1⟩ → i|1⟩, so |11⟩ → i|11⟩.
State: (|01⟩ + i|11⟩)/√2

H on q[0]:
(|0⟩ + i|1⟩)|1⟩/√2 → H(|0⟩ + i|1⟩)|1⟩/√2

H(|0⟩ + i|1⟩) = (|0⟩+|1⟩)/√2 + i(|0⟩-|1⟩)/√2 = ((1+i)|0⟩ + (1-i)|1⟩)/√2

So total state: ((1+i)|0⟩ + (1-i)|1⟩)|1⟩/2

P(|01⟩) = |(1+i)/2|² = 2/4 = 0.5
P(|11⟩) = |(1-i)/2|² = 2/4 = 0.5

That gives 50/50, not matching the expected.

Let me try Rz(θ) = e^(-iθZ/2):
Rz(π/2) = [[e^(-iπ/4), 0], [0, e^(iπ/4)]]

For controlled-Rz, when control is |1⟩:
|01⟩ → |01⟩ (control |0⟩, unchanged)
|11⟩ → e^(iπ/4)|1⟩ (target gets phase e^(iπ/4) for |1⟩ component

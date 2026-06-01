# ISQ training COT RAG corpus: quantum_algorithms shard 61

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4128

- task_id: `isqTrain/4128`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3980`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[2]);
    H(q[0]); H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 * 3.0 / 4.0 * 1.0, q[0], q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 3.0 / 4.0 * 2.0, q[1], q[2]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    H(q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

We have 3 qubits q[0], q[1], q[2].

Initial state: |000>

Step 1: X(q[2])
State: |001>

Step 2: H(q[0]); H(q[1])
H|0> = |+>
H|1> = |->
State: |+>|+>|1>

In computational basis:
|+>|+>|1> = (1/2)(|0> + |1>)(|0> + |1>)|1>
= (1/2)(|001> + |011> + |101> + |111>)

Step 3: ctrl Rz(2π * 3/4 * 1, q[0], q[2])
This is a controlled-Rz with q[0] as control and q[2] as target, with angle θ = 3π/2.

Rz(θ)|0> = |0>
Rz(θ)|1> = e^{-iθ/2}|1>

So controlled-Rz(3π/2, q[0], q[2]) applies Rz(3π/2) to q[2] when q[0] = |1>.

The effect on each basis state:
|001> → |001> (q[0]=0, no action)
|011> → |011> (q[0]=0, no action)
|101> → e^{-i3π/4}|101> (q[0]=1, q[2]=1, multiply by e^{-i3π/4})
|111> → e^{-i3π/4}|111> (q[0]=1, q[2]=1, multiply by e^{-i3π/4})

Wait, let me reconsider. Rz(θ) matrix is:
[[1, 0],
 [0, e^{iθ}]]

Hmm, actually let me check the isQ convention. In many conventions, Rz(θ) = [[1,0],[0,e^{iθ}]].

So Rz(θ)|1> = e^{iθ}|1>

But some conventions use Rz(θ) = e^{-iθ/2}[[1,0],[0,e^{iθ}]] which gives Rz(θ)|1> = e^{iθ/2}|1>.

Let me use the standard convention Rz(θ) = [[1,0],[0,e^{iθ}]] (up to global phase).

For controlled-Rz, when control is |1>, we apply Rz to the target.

So:
|001> → |001>
|011> → |011>  
|101> → e^{i*3π/2}|101> = e^{i3π/2}|101>
|111> → e^{i3π/2}|111>

State: (1/2)(|001> + |011> + e^{i3π/2}|101> + e^{i3π/2}|111>)

Step 4: ctrl Rz(2π * 3/4 * 2, q[1], q[2])
Angle = 3π

Rz(3π) applies e^{i3π} = -1 to |1> state of q[2] when q[1] = |1>.

|001> → |001> (q[1]=0)
|011> → e^{i3π}|011> = -|011> (q[1]=1, q[2]=1)
|101> → e^{i3π}*e^{i3π/2}|101> = (-1)(e^{i3π/2})|101> = -e^{i3π/2}|101> (q[1]=1, q[2]=1)
|111> → e^{i3π}*e^{i3π/2}|111> = -e^{i3π/2}|111>

State: (1/2)(|001> - |011> - e^{i3π/2}|101> - e^{i3π/2}|111>)

Hmm wait, let me be more careful. For |101>: q[0]=1, q[1]=0, q[2]=1. q[1]=0, so the controlled-Rz doesn't apply. 

Let me redo:
|001> → |001> (q[1]=0, no action)
|011> → e^{i3π}|011> = -|011> (q[1]=1, q[2]=1)
|101> → e^{i3π/2}|101> (q[1

### Reference answer

Dominant output states: |011> with probability ~0.50 each

## isqTrain/727

- task_id: `isqTrain/727`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3603`

### Prompt

实现以下量子计算任务（使用isQ）：implements the ripple_carry_adder pattern but with a different initial state preparation (flip q[[0, 1, 2]] -> q[3]).

### Chain-of-thought reasoning

Looking at this problem, I need to implement a ripple carry adder pattern. The task says to "flip q[[0, 1, 2]] -> q[3]" which means instead of initializing q[0], q[1], q[2] (which would represent a=3 in binary as a0=1, a1=1 and b0=1), I should initialize q[3] instead.

Wait, let me re-read. The implementation already has `X(q[3])` which encodes a=3 (binary 11) and b=1 (binary 01).

But the task says "flip q[[0, 1, 2]] -> q[3]". This means the initial state preparation should flip q[3] instead of q[0, 1, 2].

So In the implementation, the initial state is prepared with `X(q[3])` only.

Let me trace through the circuit:

Initial state: |000001> (only q[3] = |1>)

After X(q[3]): q[3] is flipped to |1>
State: |000100> (q[3]=1)

Wait, let me be more careful with indexing. q[0] to q[5]:
- q[0], q[1] = a (2-bit number)
- q[2], q[3] = b (2-bit number)  
- q[4] = carry0
- q[5] = carry_out

Actually, Analyzing the circuit requirements comments:
- "Encode a=3 (binary 11) and b=1 (binary 01)"
- X(q[3]) sets q[3]=1

But wait, if a=3 (binary 11), then a0=1, a1=1, which would be q[0]=1, q[1]=1
And b=1 (binary 01), then b0=1, b1=0, which would be q[2]=1, q[3]=0

But the reference only does X(q[3])... That doesn't match encoding a=3, b=1.

Let me re-read the task: "flip q[[0, 1, 2]] -> q[3]"

This means: instead of flipping q[0], q[1], q[2] (which would give a=3, b=1), we flip q[3].

So:
- Original: flip q[0], q[1], q[2] → a=3 (11), b=1 (01)
- New: flip q[3] → a=0 (00), b=2 (10)

Wait, let me reconsider. If q[0], q[1] represent a, and q[2], q[3] represent b:
- q[0] = a0 (LSB of a)
- q[1] = a1 (MSB of a)
- q[2] = b0 (LSB of b)
- q[3] = b1 (MSB of b)

So flipping q[0], q[1], q[2] gives a=3 (11), b=1 (01) ✓

Flipping q[3] instead gives a=0 (00), b=2 (10)

Now let's trace through the adder circuit with a=0, b=2:

Initial state: |000000>

After X(q[3]): |000100> (q[3] = 1)

Now the circuit operations:
1. Toffoli(q[0], q[2], q[4]): carry0 = a0 AND b0 = 0 AND 0 = 0, q[4] unchanged
   State still: |000100>

2. CNOT(q[0], q[2]): sum0 = a0 XOR b0 = 0 XOR 0 = 0, q[2] unchanged
   State: |000100>

3. Toffoli(q[1], q[3], q[5]): MSB of a AND MSB of b
   q[1]=0, q[3]=1 → q[5] unchanged
   State: |000100>

4. Toffoli(q[1], q[4], q[5]): 
   q[1]=0, q[4]=0 → q[5] unchanged
   State: |000100>

5. Toffoli(q[3], q[4], q[5]):
   q[3]=1, q[4]=0 → q[5] unchanged
   State: |000100>

6. CNOT(q[1], q[3]): q[3] = q[1] XOR q[3] = 0 XOR 1 = 1
   State

## isqTrain/2895

- task_id: `isqTrain/2895`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2545`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;
qbit q[1];
// Single qubit with Rz(pi/2) after H
procedure main() {
    // H(q[0]); // BUG: missing Hadamard
    Rz(1.5707963, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The Hadamard gate `H(q[0])` is commented out. Without it, the qubit stays in |0⟩; Rz(π/2) only adds a global phase (no observable effect on |0⟩), yielding P(|0⟩)=1 instead of the expected 50/50 split.

2. **Fix**: Uncomment `H(q[0])` so the circuit applies H followed by Rz(π/2) before measurement.

3. **Corrected state evolution**:
   - Start: |0⟩
   - H(q[0]) → |+⟩ = (1/√2)(|0⟩ + |1⟩)
   - Rz(π/2) → (1/√2)(|0⟩ + i|1⟩) — a phase shift on |1⟩
   - Measure: P(|0⟩) = 0.5, P(|1⟩) = 0.5 ✓

## isqTrain/4198

- task_id: `isqTrain/4198`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1798`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[0], q[3]);
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    Rx(2.0 * 0.500, q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

Initial state: |0000>

After H on all qubits: |++++> = (1/4)(|0>+|1>)⊗( |0>+|1>)⊗(|0>+|1>)⊗(|0>+|1>)

Let me trace through the gates carefully.

The circuit applies:
1. H on all 4 qubits → |++++>
2. CNOT(q[0], q[1]) → This entangles q[0] and q[1]
3. Rz(1.0, q[1])
4. CNOT(q[0], q[1])
5. CNOT(q[0], q[2])
6. Rz(1.0, q[2])
7. CNOT(q[0], q[2])
8. CNOT(q[0], q[3])
9. Rz(1.0, q[3])
10. CNOT(q[0], q[3])
11. Rx(1.0, q[0])
12. Rx(1.0, q[1])
13. Rx(1.0, q[2])
14. Rx(1.0, q[3])

Let me analyze each CNOT-Rz-CNOT block on qubit q[i].

The pattern CNOT(q[0], q[i]); Rz(θ, q[i]); CNOT(q[0], q[i]) applies a controlled-Rz(θ) on q[i] controlled by q[0], or equivalently, it applies Rz(θ) on q[i] when q[0] is |1>.

Wait, let me think more carefully. 

CNOT(c, t): |00>→|00>, |01>→|01>, |10>→|11>, |11>→|10>

So CNOT(q[0], q[1]) followed by Rz(θ, q[1]) followed by CNOT(q[0], q[1]):

For |00>: → |00> → |00> → |00> (no phase)
For |01>: → |01> → e^{-iθ/2}|01> → e^{-iθ/2}|01>
For |10>: → |11> → e^{-iθ/2}|11> → e^{-iθ/2}|10>
For |11>: → |10> → |10> → |11>

Wait, let me be more careful with Rz matrix:
Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

So Rz|0> = e^{-iθ/2}|0>, Rz|1> = e^{iθ/2}|1>

For the CNOT-Rz-CNOT sequence on q[0] (control) and q[1] (target):

|00> → CNOT → |00> → Rz on q[1]: e^{-iθ/2}|00> → CNOT → e^{-iθ/2}|00>
|01> → CNOT → |01> → Rz on q[1]: e^{iθ/2}|01> → CNOT → e^{iθ/2}|01>
|10> → CNOT → |11> → Rz on q[1]: e^{iθ/2}|11> → CNOT → e^{iθ/2}|10>
|11> → CNOT → |10> → Rz on q[1]: e^{-iθ/2}|10> → CNOT → e^{-iθ/2}|11>

So this gives:
|00> → e^{-iθ/2}|00>
|01> → e^{iθ/2}|01>
|10> → e^{iθ/2}|10>
|11> → e^{-iθ/2}|11>

This is like CZ(θ/2) or more precisely, it applies a phase of e^{iθ/2} when q[0] XOR q[1] = 1, and e^{-iθ/2} when q[0] XOR q[1] = 0.

Actually, let me factor this differently:
- When q[0]=0: phase e^{-iθ/2} on |00>, e^{iθ/2} on |01>
- When q[0]=1: phase e^{iθ/2} on |10>, e^{-iθ/2} on |11>

Hmm, this is equivalent to: Rz(θ) on q[1] only when q[0]=0? No...

Wait, let me reconsider. The phase factor is:
- |00>: e^{-iθ/2}
- |01>: e^{iθ/2}  
- |10>: e

### Reference answer

Uniform distribution across 10 states

## isqTrain/3728

- task_id: `isqTrain/3728`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3214`

### Prompt

Create an isQ quantum circuit that QAOA (p=1) for MaxCut on a 4-node path graph with edges [(0, 1), (1, 2), (2, 3)], gamma=0.500, beta=0.500. Use CNOT-Rz-CNOT for cost unitary and Rx for mixer.

### Chain-of-thought reasoning

Let me analyze this QAOA circuit step by step.

1. Goal: Implement QAOA (p=1) for MaxCut on a 4-node path graph with edges [(0,1), (1,2), (2,3)], with γ=0.5 and β=0.5.

2. We need 4 qubits (q[0] through q[3]), all measured.

3. State evolution:

Step 1: Initialize all qubits to |0000⟩

Step 2: Apply H to all qubits - creates equal superposition:
|ψ⟩ = |+++⟩ = (1/4) Σ_{x∈{0,1}^4} |x⟩

Step 3: Cost unitary for edge (0,1):
- CNOT(q[0], q[1]): This entangles q[0] and q[1]
- Rz(1.0, q[1]): Applies phase e^{-i*0.5} when q[1]=|1⟩
- CNOT(q[0], q[1]): Uncomputes, leaving phase based on q[0]⊕q[1]

The CNOT-Rz(2γ)-CNOT sequence applies the phase e^{-iγ(Z_0⊗Z_1)} for the edge. The net effect is:
- When q[0] ⊕ q[1] = 0: no phase change (actually the phase is e^{-iγ} for both, but since we're looking at relative phases...)
- When q[0] ⊕ q[1] = 1: phase factor e^{-i*2γ} = e^{-i}

Actually, let me be more careful. The Rz(2γ, q[1]) gate is:
Rz(θ) = |0⟩⟨0| + e^{-iθ}|1⟩⟨1|

So Rz(2γ) = |0⟩⟨0| + e^{-i*2γ}|1⟩⟨1|

The CNOT-Rz-CNOT sequence:
- Start with computational basis state |a,b⟩
- CNOT: |a, a⊕b⟩
- Rz(2γ): if a⊕b=1, multiply by e^{-i*2γ}
- CNOT: |a, b⟩ (uncompute)

So the effect is: multiply by e^{-i*2γ*(a⊕b)} = e^{-i*γ*((-1)^a*(-1)^b - 1)/2}... wait let me think again.

For edge (0,1), the cost Hamiltonian term is C_{01} = (1 - Z_0 Z_1)/2, which equals 1 when nodes are in different partitions (one 0, one 1).

The unitary e^{-iγ C_{01}} gives:
- When q[0] ⊕ q[1] = 0 (same partition): e^{-iγ*0} = 1
- When q[0] ⊕ q[1] = 1 (different partition): e^{-iγ*1} = e^{-iγ}

But the CNOT-Rz-CNOT implementation:
- The phase applied is e^{-i*2γ*(q[0]⊕q[1])}

So when q[0]⊕q[1] = 1, phase is e^{-i*2γ} = e^{-i*1} = e^{-i}

Hmm, there's a factor of 2. Let me reconsider...

Actually, for MaxCut, the cost unitary is often written as:
e^{-iγ H_C} where H_C = Σ_{(i,j)∈E} (1-Z_i Z_j)/2

This can be decomposed as:
e^{-iγ Σ_{(i,j)} (1-Z_iZ_j)/2} = e^{-iγ|E|/2} Π_{(i,j)} e^{iγ Z_i Z_j / 2}

The gate sequence CNOT-Rz(-2γ)-CNOT would implement e^{iγ Z_i Z_j / 2}... but I need to be careful about conventions.

Let me just trace through the actual circuit with γ=0.5 (so 2γ=1.0):

Starting state: |ψ₀⟩ = |0000⟩

After H gates: |ψ₁⟩ = (1/4) Σ_{x∈{0,1}⁴} |x⟩

Edge (0,1): CNOT(q0,q1)-Rz(1.0,q1)-CNOT(q0,q1)
- For basis state |a,b,c,d⟩, this applies phase e^{-i*1.0*(a⊕b)}
- So |ψ₂⟩ = (1/4) Σ_x e^{-i

## isqTrain/4099

- task_id: `isqTrain/4099`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3647`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[3];

procedure main() {
    X(q[1]);

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

Initial state: |000⟩

1. X(q[1]): Flips q[1] from |0⟩ to |1⟩
   State: |010⟩

2. H(q[0]): Apply Hadamard to q[0]
   State: (|010⟩ + |110⟩)/√2

3. ctrl Rz(π/2, q[1], q[0]): This is a controlled-Rz gate where q[1] is the control and q[0] is the target. When q[1] is |1⟩, apply Rz(π/2) to q[0].
   
   Rz(π/2) = e^(-iπ/4) * [[1, 0], [0, e^(iπ/2)]] = e^(-iπ/4) * [[1, 0], [0, i]]
   
   So when q[1]=1 and q[0]=0: no phase change (just global)
   When q[1]=1 and q[0]=1: multiply by i (up to global phase)
   
   State: (|010⟩ + i|110⟩)/√2 (up to global phase)

   Wait, let me be more careful. The Rz(θ) matrix is:
   Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
   
   So Rz(π/2) = [[e^(-iπ/4), 0], [0, e^(iπ/4)]]
   
   When we have ctrl Rz with q[1] as control and q[0] as target, we apply Rz to q[0] only when q[1]=1.
   
   State before: (|010⟩ + |110⟩)/√2
   
   For |010⟩: q[0]=0, q[1]=1, q[2]=0. Since q[1]=1, we apply Rz to q[0]. |0⟩ on q[0] gets multiplied by e^(-iπ/4).
   For |110⟩: q[0]=1, q[1]=1, q[2]=0. Since q[1]=1, we apply Rz to q[0]. |1⟩ on q[0] gets multiplied by e^(iπ/4).
   
   State: (e^(-iπ/4)|010⟩ + e^(iπ/4)|110⟩)/√2

   Since the e^(-iπ/4) is a global phase (both terms would have it if we factor it out):
   = e^(-iπ/4)(|010⟩ + e^(iπ/2)|110⟩)/√2
   = e^(-iπ/4)(|010⟩ + i|110⟩)/√2
   
   Dropping global phase: (|010⟩ + i|110⟩)/√2

4. ctrl Rz(π/4, q[2], q[0]): When q[2]=1, apply Rz(π/4) to q[0]. But q[2] is always |0⟩ in our current state, so nothing happens.
   State: (|010⟩ + i|110⟩)/√2

5. H(q[1]): Apply Hadamard to q[1].
   
   |0⟩ → (|0⟩ + |1⟩)/√2
   |1⟩ → (|0⟩ - |1⟩)/√2
   
   State: (1/√2)[(|0⟩(0) + (|0⟩ - |1⟩)1⟩ + i(|1⟩(0) + (|1⟩ - |0⟩)1⟩)]... 
   
   Let me be more careful. The state is (|010⟩ + i|110⟩)/√2.
   
   In terms of q[0], q[1], q[2]:
   = (|0⟩_q0 ⊗ |1⟩_q1 ⊗ |0⟩_q2 + i|1⟩_q0 ⊗ |1⟩_q1 ⊗ |0⟩_q2)/√2
   
   After H on q[1], |1⟩_q1 → (|0⟩_q1 - |1⟩_q1)/√2
   
   = (1/√2)[|0⟩_q0 ⊗ (|0⟩_q1 - |1⟩_q1)/√2 ⊗ |0⟩_q2 + i|1⟩_q0 ⊗ (|0⟩_q1 - |1⟩_q1)/√2 ⊗ |0⟩_q2]

### Reference answer

Uniform distribution across 8 states

## isqTrain/659

- task_id: `isqTrain/659`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `991`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;

qbit q[2];

procedure main() {
    H(q[0]);
    X(q[1]);
    
    ctrl Rx(3.14159265, q[0], q[1]);
    
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction for a given isQ program.
    *   Program: `H(q[0]); X(q[1]); ctrl Rx(3.14159265, q[0], q[1]); H(q[0]); M(q[0]);`
    *   predicted output format: "## Circuit Analysis" section, ending with the probability distribution.
    *   Constraint: Concise (3-15 lines), use Dirac notation.

2.  **Analyze the Circuit:**
    *   Initial state: $|00\rangle$
    *   `H(q[0])`: $|00\rangle \to \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
    *   `X(q[1])`: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle) \to \frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$
    *   `ctrl Rx(pi, q[0], q[1])`: Controlled-Rx($\pi$) on q[1], controlled by q[0].
        *   $Rx(\pi) = e^{-i \pi X / 2} = \cos(\pi/2)I - i\sin(\pi/2)X = -iX$.
        *   Applying to $|01\rangle + |11\rangle$:
            *   $|01\rangle$ remains $|01\rangle$.
            *   $|11\rangle \to -i |10\rangle$.
        *   State becomes $\frac{1}{\sqrt{2}}(|01\rangle - i|10\rangle)$.
    *   `H(q[0])`: Applies to the first qubit.
        *   $|01\rangle \to \frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$
        *   $|10\rangle \to \frac{1}{\sqrt{2}}(|00\rangle - |10\rangle)$
        *   Total state: $\frac{1}{2}(|01\rangle + |11\rangle - i|00\rangle + i|10\rangle)$.
    *   `M(q[0])`: Measure q[0].
        *   Probability of $0$ in q[0]: $P(0) = |\frac{1}{2}|^2 + |\frac{1}{2}|^2 = \frac{1}{4} + \frac{1}{4} = 0.5$.
        *   Probability of $1$ in q[0]: $P(1) = |\frac{1}{2}|^2 + |\frac{1}{2}|^2 = \frac{1}{4} + \frac{1}{4} = 0.5$.
        *   Wait, is $3.14159265$ exactly $\pi$?
        *   The prompt says "Expected measurement probabilities: {|0>: 0.5000000008974483, |1>: 0.49999999910255166}".
        *   Ah, $3.14159265 \neq \pi$. $\pi \approx 3.1415926535...$
        *   So $Rx(3.14159265) \approx Rx(\pi)$.
        *   Let's check the difference. $\pi - 3.14159265 = 0.0000000035...$
        *   If it's just $Rx(\theta)$, $Rx(\theta)|0\rangle = \cos(\theta/2)|0\rangle - i\sin(\theta/2)|1\rangle$.
        *   Actually, the prompt just says "Expected measurement probabilities: {|0>: 0.5..., |1>: 0.499...}". I can just state it's roughly 50/50 due to $Rx(\pi)$, or mention the slight difference.
        *   Let's just trace it with $\theta = 3.14159265$:
            *   $Rx(\theta)|1\rangle = \cos(\theta/2)|1\rangle - i\sin(\theta/2)|0\rangle$.
            *   State after C-Rx: $\frac{1}{\sqrt{2}}(|01\rangle + [\cos(\theta/2)|1\rangle - i\sin(\theta/2)|0\rangle] \otimes |1\rangle)$? No, q[1] is the target.
            *   Let's re-evaluate:
                *   Initial: $|00\rangle$
                *

### Reference answer

{'predicted_probs': {'0': 0.5000000008974483, '1': 0.49999999910255166}, 'explanation': 'Parametric variant of isqHumanEval/215. Dimension: predict probabilities for reference circuit.'}

## isqExpand/algo/39

- task_id: `isqExpand/algo/39`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `modular_exponentiation`, `shor`, `quantum_arithmetic`, `repeated_squaring`
- source: `qa_pipeline`
- dataset_index: `485`

### Prompt

模幂运算（modular exponentiation）是Shor算法中最耗资源的部分。请解释量子模幂运算 |x>|0> → |x>|a^x mod N> 的实现原理，以及为什么它在量子门数量上是多项式级别的。

### Chain-of-thought reasoning

## 推理
目标：解释量子模幂运算的实现和复杂度。

关键点：
1. 经典反复平方法的量子推广
2. 受控模乘的分解：模加法 → 模乘法 → 模幂
3. 复杂度：O((log N)^3) 基本门 — 多项式
4. 为什么是Shor算法的瓶颈（常数因子大）
5. 优化方案

这是理解Shor算法资源需求的关键。

### Reference answer

## 量子模幂运算

### 基本思想

模幂运算将经典的反复平方法（repeated squaring）推广到量子电路：

a^x mod N = a^{x_{n-1}·2^{n-1}} · a^{x_{n-2}·2^{n-2}} · ... · a^{x_0·2^0} mod N

其中 x = x_{n-1}...x_1 x_0 是 x 的二进制表示。

### 量子实现

**步骤**：
1. 预计算：经典地计算 a^{2^j} mod N（j = 0, 1, ..., n-1）
2. 受控乘法：|x_j>|y> → |x_j>|y · a^{2^j·x_j} mod N>
   - 当 x_j = 0 时不操作
   - 当 x_j = 1 时执行模乘
3. 级联：依次对每个比特 x_j 执行受控模乘

### 受控模乘的分解

受控模乘 |y> → |y·c mod N> 进一步分解为：
1. **模加法**：基于 QFT 的模加法器（Draper/Beauregard方案）
2. **模乘法**：通过 O(n) 次模加法实现
3. **可逆性**：通过计算-复制-逆计算（compute-copy-uncompute）模式保证酉性

### 复杂度分析

- 每次受控模乘：O(n^2) 基本门（使用 QFT 加法器）
- 共 n 个比特需要控制：总计 O(n^3) 基本门
- n = O(log N)，所以总复杂度 O((log N)^3)
- 这是**多项式级别的**，使 Shor 算法整体保持多项式

### 为什么是瓶颈

虽然渐进复杂度是多项式的，但常数因子很大：
- 分解 n 位数需要约 2n 个逻辑 qubit
- 加上纠错开销，物理 qubit 数量巨大
- 例如分解 2048 位 RSA：约 4000 逻辑 qubit，数百万物理 qubit

### 优化方向
- Beauregard 方案：减少到 2n+3 个 qubit
- Windowed arithmetic：减少乘法次数
- 近似 QFT：减少旋转门精度

## isqTrain/986

- task_id: `isqTrain/986`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3809`

### Prompt

I need an isQ program to implements the suzuki_trotter pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this Suzuki-Trotter circuit step by step.

**Goal**: Implement a second-order Suzuki-Trotter decomposition S2(t) = e^(-i*t/2*ZZ) * e^(-i*t*XX) * e^(-i*t/2*ZZ) with t = π/8, starting from |10⟩, with identity H-H pair before measurement.

**Qubits**: 2 qubits q[0] and q[1], both measured.

**State evolution**:

1. Initial state: |00⟩
2. After X(q[0]): |10⟩

3. First half-step e^(-i*t/2*ZZ) with t = π/8:
   - CNOT(q[0], q[1]): |10⟩ → |11⟩
   - Rz(0.392699081698724, q[1]): This is Rz(t) on q[1]. Since q[1] is |1⟩, this adds phase e^(-i*t/2) = e^(-i*π/16)
   - State: e^(-iπ/16)|11⟩
   - CNOT(q[0], q[1]): e^(-iπ/16)|11⟩ → e^(-iπ/16)|10⟩

Wait, let me recalculate. Rz(θ) = [[1, 0], [0, e^(-iθ)]]

So Rz(t) with t = π/8 on |1⟩ gives e^(-i*t)|1⟩ = e^(-iπ/8)|1⟩

After first half-step: e^(-iπ/8)|10⟩

Wait, but ZZ eigenvalues: ZZ|00⟩ = +|00⟩, ZZ|01⟩ = -|01⟩, ZZ|10⟩ = -|10⟩, ZZ|11⟩ = +|11⟩

So e^(-i*t/2*ZZ)|10⟩ = e^(i*t/2)|10⟩ = e^(iπ/16)|10⟩

Let me verify the decomposition. For ZZ:
CNOT(0,1) * Rz(θ, 1) * CNOT(0,1) = e^(-i*θ/2*ZZ) * (some global phase)

Actually, let me be more careful. The standard decomposition:
e^(-iθ/2 ZZ) = CNOT(0,1) · Rz(θ, 1) · CNOT(0,1) up to global phase.

Let me verify: CNOT(0,1) maps |10⟩ → |11⟩. Then Rz(t, 1) on |11⟩: the |11⟩ component gets e^(-it) phase → e^(-it)|11⟩. Then CNOT: e^(-it)|10⟩.

But e^(-it/2*ZZ)|10⟩ should give e^(it/2)|10⟩ since ZZ has eigenvalue -1 for |10⟩.

Hmm, the mapping is:
CNOT(0,1) Rz(θ, 1) CNOT(0,1) = e^(-iθ/2) e^(-iθ/2 * Z0⊗Z1) ... let me just compute directly.

Actually for the Suzuki-Trotter, the important thing is the final probabilities. Let me track the state numerically.

t = π/8

Starting: |10⟩

**First half ZZ step** (e^{-it/2 ZZ}):
CNOT(0,1): |10⟩ → |11⟩
Rz(t, 1): |11⟩ → e^{-it}|11⟩ = e^{-iπ/8}|11⟩
CNOT(0,1): e^{-iπ/8}|10⟩

So after first half-step: e^{-iπ/8}|10⟩ (global phase, so effectively |10⟩)

Wait, but e^{-it/2 ZZ}|10⟩ = e^{it/2}|10⟩. With t = π/8, this is e^{iπ/16}|10⟩.

Let me recheck the decomposition. The claim is Rz(t) in the circuit corresponds to angle 2*(t/2) = t for the half-step.

The circuit CNOT(0,1) Rz(α, 1) CNOT(0,1) implements:
- |00⟩ → |00⟩ → |00⟩ (Rz doesn't affect |0⟩)
- |01⟩ → |01⟩ → e^{-iα}|01⟩
- |10⟩ → |11⟩ → e^{-iα}|11⟩ → e^{-iα}|10⟩
- |11⟩ → |10⟩ → |10⟩ → |11⟩

So the

## isqTrain/2956

- task_id: `isqTrain/2956`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `821`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    H(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    H(q[0]);
    H(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

Let me trace through this quantum circuit step by step.

Initial state: |00⟩

Step 1: H(q[0])
H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2
State: (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2

Step 2: H(q[1])
H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2
State: (|0⟩ + |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

Step 3: CNOT(q[0], q[1]) - q[0] is control, q[1] is target
|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩
State: (|00⟩ + |01⟩ + |11⟩ + |10⟩)/2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
This is the same state! CNOT just permutes the basis states.

Step 4: CNOT(q[1], q[0]) - q[1] is control, q[0] is target
|00⟩ → |00⟩
|01⟩ → |11⟩
|10⟩ → |10⟩
|11⟩ → |01⟩
State: (|00⟩ + |11⟩ + |10⟩ + |01⟩)/2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
Still the same state!

So after the first 4 gates, we're back to (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2.

Steps 5-8 are identical to steps 1-4, so they'll produce the same result.
After step 8: (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

Wait, let me reconsider. The pattern repeats, so the final state should be:
(|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

This means each outcome has probability 1/4.

But The predicted output {'00': 1.0}. Let me re-check.

Actually, wait. Let me be more careful.

After H(q[0]), H(q[1]):
State = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

This can be written as |++⟩ where both qubits are in |+⟩ state.

Now, CNOT(q[0], q[1]):
CNOT|++⟩ = CNOT((|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2)
= (|00⟩ + |11⟩ + |10⟩ + |01⟩)/2
Wait, let me be more careful.

CNOT with q[0] as control and q[1] as target:
- |00⟩ → |00⟩
- |01⟩ → |01⟩
- |10⟩ → |11⟩
- |11⟩ → |10⟩

So (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 → (|00⟩ + |01⟩ + |11⟩ + |10⟩)/2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

OK so CNOT doesn't change the state |++⟩.

Now CNOT(q[1], q[0]):
- |00⟩ → |00⟩
- |01⟩ → |11⟩
- |10⟩ → |10⟩
- |11⟩ → |01⟩

(|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 → (|00⟩ + |11⟩ + |10⟩ + |01⟩)/2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

So the state remains unchanged.

Now H(q[0]), H(q[1]):
H⊗H applied to |++⟩.
H|+⟩ = |0⟩
So H⊗H|++⟩ = |00⟩

Then CNOT(q[0], q[1]): |00⟩ → |00⟩
Then CNOT(q[1], q[0]): |00⟩ → |00⟩

Final state: |00⟩

So the probability is {'00': 1.0}.

Let me verify step by step more carefully:

Initial: |00⟩

H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

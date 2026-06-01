# ISQ training COT RAG corpus: quantum_algorithms shard 78

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/867

- task_id: `isqTrain/867`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4948`

### Prompt

I need an isQ program to implements the quantum_logic_gate pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement OR(a,b) using De Morgan's law (OR = NOT(NOT a AND NOT b)) with an explicit H-H identity pair to show gate cancellation.

2. **Qubits**: 3 qubits; q[0]=a, q[1]=b, q[2]=result. All measured.

3. **State evolution**:
   - |000⟩ → X(q[0]) → |100⟩ (set a=1, b=0)
   - X(q[0]); X(q[1]) → |010⟩ (negate inputs: a'=0, b'=1)
   - Toffoli → |010⟩ (AND requires both controls |1⟩; only q[1]=1, so no flip)
   - X(q[0]); X(q[1]) → |100⟩ (restore original inputs)
   - X(q[2]) → |101⟩ (negate AND result → OR result)
   - H(q[0]) → (|001⟩ − |101⟩)/√2 (superposition)
   - H(q[0]) → |101⟩ (H-H = I, gate cancellation restores deterministic state)

4. **Result**: Since H-H cancels to identity, the state remains |101⟩. OR(1,0)=1 is stored in q[2], and the H-H pair explicitly demonstrates that successive identical Hadamards form an identity operation, preserving the classical result with probability |101⟩: 1.0.

## isqTrain/4185

- task_id: `isqTrain/4185`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1742`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[1], q[2]);
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[0], q[2]);
    Rx(2.0 * 0.393, q[0]);
    Rx(2.0 * 0.393, q[1]);
    Rx(2.0 * 0.393, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

This circuit involves 3 qubits with several entangling gates and rotations. Let me trace through it carefully.

Initial state: |000⟩

After H on all three qubits:
H|0⟩⊗H|0⟩⊗H|0⟩ = |+++⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

Now I need to understand the sequence of CNOT-Rz-CNOT operations.

CNOT(q[0], q[1]) followed by Rz(θ, q[1]) followed by CNOT(q[0], q[1]) is a controlled-Rz gate where q[0] controls the Rz on q[1].

Similarly:
- CNOT(q[1], q[2]); Rz(2*0.785, q[2]); CNOT(q[1], q[2]) = CRz on q[2] controlled by q[1]
- CNOT(q[0], q[2]); Rz(2*0.785, q[2]); CNOT(q[0], q[2]) = CRz on q[2] controlled by q[0]

So the entangling part applies:
1. CRz(2*0.785, q[1]) controlled by q[0]
2. CRz(2*0.785, q[2]) controlled by q[1]  
3. CRz(2*0.785, q[2]) controlled by q[0]

Wait, let me reconsider. The CNOT-Rz-CNOT pattern:

CNOT(c, t); Rz(θ, t); CNOT(c, t)

This applies Rz(θ) to the target only when the control is |1⟩. So it's a controlled-Rz gate.

The angle is 2.0 * 0.785 = 1.57 ≈ π/2.

So we have:
1. CRz(π/2) with q[0] controlling q[1]
2. CRz(π/2) with q[1] controlling q[2]
3. CRz(π/2) with q[0] controlling q[2]

Then Rx(2*0.393) = Rx(0.786) ≈ Rx(π/4) on each qubit.

Wait, 0.393 ≈ π/8, so 2*0.393 ≈ π/4.

Actually let me be more precise:
- 0.785 ≈ π/4, so 2*0.785 = π/2
- 0.393 ≈ π/8, so 2*0.393 = π/4

This looks like it could be related to a QAOA circuit or some optimization circuit.

Let me compute the state step by step.

Starting from |+++⟩ = (1/2√2) Σ_{x∈{0,1}³} |x⟩

The controlled-Rz gates apply a phase to computational basis states.

CRz(θ) with control q[0] and target q[1]:
- When q[0]=1, applies Rz(θ) to q[1], which adds phase -θ/2 to |0⟩_1 and +θ/2 to |1⟩_1... wait no.

Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

So CRz(π/2) with control q[0], target q[1]:
- When q[0]=1 and q[1]=0: phase e^{-iπ/4}
- When q[0]=1 and q[1]=1: phase e^{iπ/4}

Similarly for the others.

Let me track the phase accumulated by each computational basis state |q[0]q[1]q[2]⟩.

For state |abc⟩ where a, b, c ∈ {0,1}:

Phase from CRz₁ (control q[0], target q[1]):
- If a=1: phase = e^{-iπ/4} if b=0, e^{iπ/4} if b=1
- So phase factor: (-1)^a * ... wait, let me just track it as:
  - If a=1, b=0: e^{-iπ/4}
  - If a=1, b=1: e^{iπ/4}
  - If a=0: 1

Phase from CRz₂ (control q[1], target q[2]):
- If b=1, c=0: e^{-iπ/4}
- If b=1

### Reference answer

Uniform distribution across 8 states

## isqTrain/2899

- task_id: `isqTrain/2899`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `958`

### Prompt

Implement a quantum circuit in isQ: implementing the Deutsch-Jozsa algorithm for a constant oracle on 2 input qubits. The oracle always returns true.

Requirements:
- Use 2 input qubits and 1 ancilla.
- Declare qubits at global scope.
- Use `procedure main()` as entry point.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement Deutsch-Jozsa algorithm for a 2-bit constant oracle that always returns 1, distinguishing constant from balanced functions.
2. **Qubits**: 3 total — 2 input qubits (q[0], q[1]) and 1 ancilla (anc[0]); all measured.
3. **State evolution**:
   - Initialize |000⟩; X(anc[0]) → |001⟩; H(anc[0]) → |00⟩⊗|−⟩
   - H(q[0]), H(q[1]) → |+⟩|+⟩⊗|−⟩ = (1/2)(|00⟩+|01⟩+|10⟩+|11⟩)⊗|−⟩
   - Oracle f_const(x)=1 applies phase (-1)^1 = -1 to all basis states → -|+⟩|+⟩⊗|−⟩
   - H(q[0]), H(q[1]) → -|00⟩⊗|−⟩ (since H|+⟩=|0⟩)
4. **Expected probabilities**: Input qubits deterministically measure as |00⟩; ancilla in |−⟩=(|0⟩-|1⟩)/√2 yields 50/50 outcomes → {|000⟩: 0.5, |001⟩: 0.5}.

## isqTrain/2932

- task_id: `isqTrain/2932`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_for_loop`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1703`

### Prompt

Code this in isQ: creates a uniform superposition over 3 qubits by applying Hadamard to each qubit.

Requirements:
- Declare `qbit q[3];` at global scope.
- Use a for loop to apply H gates.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a uniform superposition over all 3-qubit basis states using Hadamard gates.
2. **Qubits**: 3 qubits declared globally as `qbit q[3]`, all measured at the end.
3. **State evolution**:
   - Initial: |000⟩
   - After H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |00⟩ = (|000⟩ + |100⟩)/√2
   - After H(q[1]): (|000⟩ + |010⟩ + |100⟩ + |110⟩)/2
   - After H(q[2]): (|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)/2√2
4. **Expected probabilities**: The final state is an equal superposition of all 8 basis states, each with amplitude 1/2√2 = 1/√8. Thus each basis state has probability |1/√8|² = 1/8 = 0.125.

## isqTrain/4475

- task_id: `isqTrain/4475`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `interference`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5439`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;

qbit q[3];

procedure main() {
    
    X(q[2]);
    
    H(q[0]);
    
    ctrl SWAP(q[0], q[1], q[2]);
    
    H(q[0]);
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the probability distribution of measurement outcomes for a given isQ program.
    *   Program involves 3 qubits `q[3]`.
    *   Output format: "## Circuit Analysis", Dirac notation, step-by-step state evolution, 3-15 lines (since it's relatively simple), ending with the probability distribution.

2.  **Analyze the isQ Code:**
    *   Initial state: $|000\rangle$
    *   `X(q[2])`: Applies X to q[2]. State becomes $|001\rangle$ (q[2] is the least significant bit if we follow standard convention where q[0] is highest or vice versa. Let's trace carefully: in Dirac notation, $|q_2 q_1 q_0\rangle$ or $|q_0 q_1 q_2\rangle$? Standard Qiskit/isQ uses $|q_{n-1}\dots q_0\rangle$ usually, but let's just track basis states. `X(q[2])` flips the 3rd qubit to $|1\rangle$).
    *   `H(q[0])`: Hadamard on q[0]. State: $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle) + \frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$? Wait.
        If $|001\rangle$ means $q_0=0, q_1=0, q_2=1$:
        `X(q[2])` -> $|q_0q_1q_2\rangle = |001\rangle$
        `H(q[0])` -> $\frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$
    *   `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])`: Controlled-swap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)). If $q_0=1$, swap $q_1$ and $q_2$.
        If $q_0=0$, state is $|001\rangle$. No swap.
        If $q_0=1$, state is $|101\rangle$. Swap $q_1$ and $q_2$. $q_1=0, q_2=1$ -> $q_1=1, q_2=0$. New state for this branch: $|110\rangle$.
        State after ctrl swap (three-CNOT decomposition): $\frac{1}{\sqrt{2}}(|001\rangle + |110\rangle)$.
    *   `H(q[0])`: Hadamard on q[0] again.
        $|001\rangle \to \frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$
        $|110\rangle \to \frac{1}{\sqrt{2}}(|110\rangle - |010\rangle)$
        Combined state: $\frac{1}{2}|001\rangle + \frac{1}{2}|101\rangle + \frac{1}{2}|110\rangle - \frac{1}{2}|010\rangle$.
    *   `H(q[0]); Z(q[0]); H(q[0]);`: This is X applied to q[0].
        $|0\rangle \to |1\rangle$, $|1\rangle \to |0\rangle$.
        Flipping $q_0$:
        $|001\rangle \to |101\rangle$
        $|101\rangle \to |001\rangle$
        $|110\rangle \to |010\rangle$
        $|010\rangle \to |110\rangle$
        Final state: $\frac{1}{2}|101\rangle + \frac{1}{2}|001\rangle + \frac{1}{2}|010\rangle - \frac{1}{2}|110\rangle$.
        Wait! Is this right? Let's re-read the predicted output.
        Expected measurement probabilities: `{|000>: 0.5000000000000001, |001>: 0.4999999999999999}`
        Why is the predicted output only `|000>` and `|001>`?
        Let's re-evaluate `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])`. Does it mean "control on q[0], swap q[1] and q[2]"? Yes.
        Let's check initial states and gates again.
        Is `q[0]` the *last* qubit in the tensor product?
        If bitstring is `q[2]q[1]q[0]`, then:

### Reference answer

{'predicted_probs': {'000': 0.5, '001': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.5000, P(|001>) = 0.5000.'}

## isqTrain/4533

- task_id: `isqTrain/4533`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3832`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];

procedure main() {
    
    H(q[1]); T(q[1]);
    
    
    H(q[0]);
    
    CNOT(q[0], q[1]);
    inv T(q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

The user wants a circuit analysis for an isQ program.
The program defines two qubits `q[0]` and `q[1]`.
Initial state: $|00\rangle$
1. `H(q[1]); T(q[1]);`
   `H` on $q_1$: $|00\rangle \to \frac{1}{\sqrt{2}}(|00\rangle + |01\rangle)$
   `T` on $q_1$: $\frac{1}{\sqrt{2}}(|00\rangle + e^{i\pi/4}|01\rangle)$

2. `H(q[0]);`
   Apply H to $q_0$: $\frac{1}{2}(|00\rangle + |10\rangle + e^{i\pi/4}|01\rangle + e^{i\pi/4}|11\rangle)$

3. `CNOT(q[0], q[1]);`
   CNOT with $q_0$ as control and $q_1$ as target.
   $|00\rangle \to |00\rangle$
   $|10\rangle \to |11\rangle$
   $|01\rangle \to |01\rangle$
   $|11\rangle \to |10\rangle$
   State: $\frac{1}{2}(|00\rangle + |11\rangle + e^{i\pi/4}|01\rangle + e^{i\pi/4}|10\rangle)$

4. `inv T(q[1]);`
   Apply $T^\dagger$ to $q_1$. This is $e^{-i\pi/4}$ to the $|1\rangle$ component of $q_1$.
   $|00\rangle \to |00\rangle$
   $|11\rangle \to e^{-i\pi/4}|11\rangle$
   $|01\rangle \to e^{-i\pi/4}|01\rangle$
   $|10\rangle \to |10\rangle$
   State: $\frac{1}{2}(|00\rangle + e^{-i\pi/4}|11\rangle + e^{i\pi/4}e^{-i\pi/4}|01\rangle + e^{i\pi/4}|10\rangle)$
   $= \frac{1}{2}(|00\rangle + |01\rangle + e^{i\pi/4}|10\rangle + e^{-i\pi/4}|11\rangle)$

5. `CNOT(q[0], q[1]);`
   Apply CNOT again with $q_0$ as control, $q_1$ as target.
   $|00\rangle \to |00\rangle$
   $|01\rangle \to |01\rangle$
   $|10\rangle \to |11\rangle$
   $|11\rangle \to |10\rangle$
   State: $\frac{1}{2}(|00\rangle + |01\rangle + e^{i\pi/4}|11\rangle + e^{-i\pi/4}|10\rangle)$
   Rearrange to be in standard order (optional):
   $\frac{1}{2}(|00\rangle + |01\rangle + e^{-i\pi/4}|10\rangle + e^{i\pi/4}|11\rangle)$
   Notice that $q_0$ and $q_1$ are in a product state!
   $q_0$ is in $\frac{1}{\sqrt{2}}(|0\rangle + e^{-i\pi/4}|1\rangle)$. Wait, let's check.
   $\frac{1}{2}(|0\rangle_0(|0\rangle_1 + |1\rangle_1) + e^{-i\pi/4}|1\rangle_0(|1\rangle_1 + e^{i\pi/2}|0\rangle_1))$. Not exactly.
   Let's just trace:
   $q_0$ is $\frac{1}{\sqrt{2}}(|0\rangle + e^{-i\pi/4}|1\rangle)$
   $q_1$ is $\frac{1}{2}(|0\rangle + |1\rangle + e^{i\pi/4}|0\rangle + e^{-i\pi/4}|1\rangle)$ Wait, this is not right.
   State: $\frac{1}{2} [ |0\rangle_0(|0\rangle_1 + |1\rangle_1) + e^{-i\pi/4}|1\rangle_0(|0\rangle_1 + e^{i\pi/2}|1\rangle_1) ]$.

### Reference answer

{'predicted_probs': {'00': 0.073223, '01': 0.073223, '10': 0.426777, '11': 0.426777}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.0732, P(|01>) = 0.0732, P(|10>) = 0.4268, P(|11>) = 0.4268.'}

## isqTrain/3591

- task_id: `isqTrain/3591`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `960`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should Toffoli decomposition into CNOT + single-qubit gates.

### Chain-of-thought reasoning

Let me analyze the buggy code and the corrected version to identify the bug.

Looking at the buggy code vs the corrected version:

Buggy code has:

Fixed code has:

This is the only difference. The CNOT direction is swapped - in the buggy version, q[1] is the control and q[0] is the target, but it should be the other way around.

Let me trace through the corrected Toffoli decomposition to verify it works for |110> -> |111>:

The standard Toffoli decomposition into CNOT + single-qubit gates:

1. Start: |110>
2. H(q[2]): |110> ⊗ H|0> = |11> ⊗ |+> = |11+>
3. CNOT(q[1], q[2]): Since q[1]=|1>, flips q[2]: |11-> (since H|0>=|+>, CNOT on |+>=|->)
4. T†(q[2]) = Rz(-π/4)(q[2])
5. CNOT(q[0], q[2]): Since q[0]=|1>, applies X to q[2]
6. T(q[2])
7. CNOT(q[1], q[2]): Since q[1]=|1>, applies X to q[2]
8. T†(q[2]) = Rz(-π/4)(q[2])
9. CNOT(q[0], q[2]): Since q[0]=|1>, applies X to q[2]
10. T(q[1])
11. T(q[2])
12. H(q[2])
13. CNOT(q[0], q[1]): q[0] control, q[1] target. Since q[0]=|1>, flips q[1]: q[1] goes from |1> to |0>
14. T(q[0])
15. T†(q[1]) = Rz(-π/4)(q[1])
16. CNOT(q[0], q[1]): q[0] control, q[1] target. Since q[0]=|1>, flips q[1]: q[1] goes from |0> to |1>

Wait, let me think more carefully about this decomposition. The standard Toffoli decomposition using H, T, T†, and CNOT gates:

The Toffoli gate can be decomposed as follows:
1. H on target
2. CNOT(control2, target)
3. T† on target
4. CNOT(control1, target)
5. T on target
6. CNOT(control2, target)
7. T† on target
8. CNOT(control1, target)
9. T on control2
10. T on target
11. H on target
12. CNOT(control1, control2)
13. T on control1
14. T† on control2
15. CNOT(control1, control2)

In the code:
- q[0] = control1
- q[1] = control2
- q[2] = target

So the CNOT at step 12 should be CNOT(q[0], q[1]) - q[0] is control, q[1] is target.

The buggy code had CNOT(q[1], q[0]) which is the wrong direction.

Let me verify the state evolution more carefully for the input |110> (q[0]=|1>, q[1]=|1>, q[2]=|0>):

Actually, let me just verify that the corrected circuit produces |111>.

The Toffoli gate flips the target (q[2]) when both controls (q[0] and q[1]) are |1>. 

Input: |110> (q[0]=1, q[1]=1, q[2]=0)
After Toffoli: |111> (q[2] flips because both controls are 1)

This is correct! The Toffoli decomposition should achieve this.

Now let me verify step by step:

Initial: |110>

1. H(q[2]): |11+>
2. CNOT(q[1], q[2]): |11-> (control q[1]=1, so flip q[2])
3. Rz(-π/4)(q[2]): phase on |1> component of q[2]
4. CNOT(q[0], q[2]): |11+> (control q[0]=1, so flip q[2] back)
5. T(q[2]): phase on |1> component
6. CNOT(q[1], q[2]): |

## isqQA/quantum_algorithms/90_principle_advantage

- task_id: `isqQA/quantum_algorithms/90_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `Bernstein-Vazirani算法原理`
- source: `qa_pipeline`
- dataset_index: `1503`

### Prompt

请详细解释Bernstein-Vazirani算法的宏观原理，并说明它与经典算法相比在时间复杂度上的优势。另外，这种量子加速的物理本质和数学来源是什么？能否用isQ代码演示一个具体的3量子位Bernstein-Vazirani算法的实现？

### Reference answer

<cratch>
数学推导：
假设秘密字符串为 $s \in \{0,1\}^n$。黑盒函数实现 $f_s(x) = s \cdot x \pmod 2$。
在量子线路中，初始化 $|0\rangle^{\otimes n}|1\rangle$。
经过第一个Hadamard层：
$H^{\otimes n}|0\rangle^{\otimes n} \otimes H|1\rangle = \frac{1}{\sqrt{2^n}} \sum_{x \in \{0,1\}^n} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$
应用Oracle $U_f$：
$U_f|x\rangle|y\rangle = |x\rangle|y \oplus f_s(x)\rangle$
当目标寄存器为 $\frac{|0\rangle - |1\rangle}{\sqrt{2}}$ 时，相位被踢回：
$\frac{1}{\sqrt{2^n}} \sum_{x} (-1)^{s \cdot x} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$
对前n个量子比特再次施加Hadamard变换：
$H^{\otimes n} \sum_{x} (-1)^{s \cdot x} |x\rangle = \sum_{z} \left( \frac{1}{2^n} \sum_{x} (-1)^{s \cdot x + z \cdot x} \right) |z\rangle$
根据正交性，当 $z = s$ 时，内积为1，否则为0。因此结果即为 $|s\rangle$。测量输入寄存器直接得到 $s$。
</cratch>
Bernstein-Vazirani（BV）算法是量子计算中用于展示量子查询复杂度优势的经典算法之一。

宏观原理：
BV算法解决的问题非常明确：给定一个黑盒函数 $f: \{0,1\}^n \rightarrow \{0,1\}$，已知其计算形式为 $f(x) = s \cdot x \pmod 2$，其中 $s$ 是一个未知的 $n$ 位二进制秘密字符串，我们的目标是找出 $s$。在量子算法中，我们将输入寄存器制备为等权叠加态，并将其作为控制比特通过相位反冲机制将函数值存储在相位中；随后再次施加Hadamard变换，利用量子态的干涉效应，使得只有与 $s$ 对应的量子态的振幅相长干涉为1，其他态的振幅相消干涉为0。最后测量输入寄存器，只需1次查询就能100%确定 $s$ 的值。

时间复杂度对比与量子加速来源：
在经典计算中，要找出 $s$，我们必须通过构造特定的输入来提取 $s$ 的每一位。例如，依次输入只有第 $i$ 位为1的字符串，通过 $f(e_i) = s_i$ 逐个确定 $s$ 的每一位。这至少需要 $n$ 次查询，时间复杂度为 $O(n)$。
而量子算法之所以能够实现 $O(1)$ 的查询复杂度（只需1次查询），其加速的物理和数学本质来源于**量子并行性**与**量子干涉**。量子并行性允许算法同时将所有 $2^n$ 种可能的输入叠加在一个量子态上，并通过一次查询将所有结果打包进相位中；而量子干涉（在此表现为Hadamard变换）则巧妙地将包含目标信息的相位差异转化为可测量的概率幅差异，这是经典概率计算无法实现的。

isQ代码演示：
下面是一个使用isQ语言实现的3位BV算法示例，假设秘密字符串 $s = 101$（即 $s_0=1, s_1=0, s_2=1$）。

```isq
import std;

qbit q[4];

procedure main() {
    // 初始化辅助比特（目标比特）为 |1>，即 q[3]
    X(q[3]);
    
    // 对所有比特施加Hadamard门，使输入寄存器进入叠加态，辅助比特进入(|0>-|1>)/sqrt(2)
    for i in 0:4 {
        H(q[i]);
    }
    
    // 实现 Oracle f(x) = s.x mod 2，假设秘密字符串 s = 101 (对应q[2]q[1]q[0])
    // 只需对 s 中为 1 的位置施加 CNOT 门即可实现相位反冲
    CNOT(q[0], q[3]);
    CNOT(q[2], q[3]);
    
    // 对输入寄存器（前3位）再次施加Hadamard门，利用干涉提取信息
    for i in 0:3 {
        H(q[i]);
    }
    
    // 测量输入寄存器，结果应为 101
    for i in 0:3 {
        M(q[i]);
    }
}
```
在这段isQ代码中，我们使用了4个量子比特，前3个用于编码输入，最后1个作为辅助比特。通过受控非门（CNOT）模拟黑盒Oracle，最后对前3位进行测量即可一次性获得秘密字符串。

## isqTrain/1374

- task_id: `isqTrain/1374`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2595`

### Prompt

Create an isQ quantum circuit that Grover's algorithm on 2 qubits to search for the state |00>. Use a single Grover iteration (which gives certainty for 2 qubits).

### Chain-of-thought reasoning

## Reasoning
**Goal**: Implement Grover's search on 2 qubits to find marked state |00> using one iteration (optimal for 4-element search space).

**Qubits**: 2 global qubits q[0], q[1], both measured.

**State evolution**:
1. **Init**: |00>
2. **H⊗H**: (|00>+|01>+|10>+|11>)/2 = |+⟩⊗|+⟩
3. **Oracle** (X⊗X → CZ → X⊗X): Flips phase of |00> → (-|00>+|01>+|10>+|11>)/2
4. **Diffusion** (H⊗H → X⊗X → CZ → X⊗X → H⊗H): Reflects amplitudes about mean (1/4), mapping -1/2→1 and 1/2→0
5. **Result**: |00> with probability 1.0

**Why P(|00>)=1.0**: For N=4 with M=1 solution, one Grover iteration gives sin²(3π/4·arcsin(1/2)) = sin²(π/2) = 1. The amplitude reflection exactly cancels all non-target amplitudes, leaving pure |00>.

## isqTrain/3440

- task_id: `isqTrain/3440`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `506`

### Prompt

Write an isQ program that QPE in isQ for the T gate using 3 precision qubits.

T|1> = exp(i*pi/4)|1>, phase = pi/4, theta = 1/8.
Binary: 0.001 with 3 bits -> |001>.

Controlled operations:
- prec[0] controls T^4 = Z
- prec[1] controls T^2 = S
- prec[2] controls T^1 = T

Apply 3-qubit inverse QFT after controlled unitaries.
Declare prec[3] and tgt[1]. Measure only prec[0..2].

### Chain-of-thought reasoning

The user wants me to analyze the QPE circuit for the T gate with 3 precision qubits.

Let me trace through the circuit:

1. Initial state: |000>|0> (3 prec qubits + 1 target)
2. After X(tgt[0]): |000>|1>
3. After H on all prec: 1/2√2 * (|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>) |1>

Now controlled unitaries:
- prec[0] controls T^4 = Z: phases for states where prec[0]=1 (states |100>, |101>, |110>, |111>)
- prec[1] controls T^2 = S: phases for states where prec[1]=1 (states |010>, |011>, |110>, |111>)
- prec[2] controls T^1 = T: phases for states where prec[2]=1 (states |001>, |011>, |101>, |111>)

The phase accumulated for state |abc> is exp(i*pi/4 * (4a + 2b + c)) where a,b,c are bits.

So:
|000>: phase 0
|001>: phase π/4 (T)
|010>: phase π/2 (S)
|011>: phase 3π/4 (S+T)
|100>: phase π (Z)
|101>: phase 5π/4 (Z+T)
|110>: phase 3π/2 (Z+S)
|111>: phase 7π/4 (Z+S+T)

After controlled unitaries: 1/2√2 * Σ |abc> exp(iφ_abc) |1>

Then inverse QFT on prec register.

The QFT maps |k> -> 1/√8 Σ_j exp(2πijk/8) |j>
So inverse QFT maps Σ_j exp(2πijk/8) |j> -> |k> (up to normalization)

Our state has phases exp(iπk/4) = exp(2πik/8) for |k> where k is the integer 4a+2b+c.

So the state is 1/2√2 * Σ_k=0^7 exp(2πik·θ) |k>|1> where θ = 1/8 (but wait, we need to check)

Actually, for QPE with T gate, the phase is π/4, so θ = (π/4)/(2π) = 1/8.

The ideal output of QPE would be |001> (binary for 1/8 = 0.001_2).

But the predicted output show a distribution, not just |001>. Let me re-examine...

Wait, looking at the predicted output:
|000>: 0.038582
|001>: 0.086418
|010>: 0.027729
|011>: 0.700824
|100>: 0.004758
|101>: 0.120242
|110>: 0.00662
|111>: 0.014827

Hmm, the highest probability is |011> not |001>. That seems wrong for theta = 1/8.

Wait, let me reconsider. The controlled operations are:
- prec[0] controls T^4 = Z → applies phase e^(iπ) when prec[0]=1
- prec[1] controls T^2 = S → applies phase e^(iπ/2) when prec[1]=1
- prec[2] controls T^1 = T → applies phase e^(iπ/4) when prec[2]=1

So for state |a,b,c> (prec[0]=a, prec[1]=b, prec[2]=c):
Phase = a*π + b*π/2 + c*π/4 = (4a + 2b + c)*π/4

The integer k = 4a + 2b + c ranges from 0 to 7.

So the state before IQFT is:
(1/2√2) Σ_k=0^7 e^(iπk/4) |k>|1>

Now IQFT on 3 qubits maps:
IQFT: |k> → (1/√8) Σ_j=0^7 e^(-2πijk/8) |j>

So the result on prec register:
(1/2√2)(1/√8) Σ_j Σ_k e^(iπk/4) e^(-2πijk/8) |j>|1>
= (1/4) Σ_j (Σ_k e^(

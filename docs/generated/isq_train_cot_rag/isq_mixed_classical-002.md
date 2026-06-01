# ISQ training COT RAG corpus: isq_mixed_classical shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/514

- task_id: `isqTrain/514`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4688`

### Prompt

用isQ实现implements the bell_state_preparation pattern with modified rotation parameters (pi2_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a modified U3 gate with angle π/4 (instead of π/2 for H) to create a biased superposition on a single qubit.
2. **Qubits**: 1 qubit `q[0]`, which is measured.
3. **State evolution**:
   - Initial state: |0⟩
   - U3(θ, φ, λ) matrix: [[cos(θ/2), -e^(iλ)sin(θ/2)], [e^(iφ)sin(θ/2), e^(i(φ+λ))cos(θ/2)]]
   - With θ=π/4, φ=0, λ=π: U3 = [[cos(π/8), sin(π/8)], [sin(π/8), -cos(π/8)]]
   - Final state: cos(π/8)|0⟩ + sin(π/8)|1⟩
4. **Probabilities**: P(|0⟩) = cos²(π/8) ≈ 0.8536, P(|1⟩) = sin²(π/8) ≈ 0.1464, matching expected values.

## isqTrain/1979

- task_id: `isqTrain/1979`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1722`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    S(q[0]);
    S(q[0]);
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations**: H → S → S → H → Measurement

2. **State evolution**:
   - Start: |0⟩
   - H: |+⟩ = (1/√2)(|0⟩ + |1⟩)
   - S: (1/√2)(|0⟩ + i|1⟩)
   - S: (1/√2)(|0⟩ + i²|1⟩) = (1/√2)(|0⟩ - |1⟩) = |−⟩
   - H: H|−⟩ = |1⟩

3. **Final state**: |1⟩

4. **Measurement**: Always yields outcome 1.

**Predicted probabilities**: {'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Verifies S·S = Z identity. H·S·S·H = H·Z·H = X on |0⟩ → |1⟩. P(|1⟩) = 1.0.'}

## isqTrain/445

- task_id: `isqTrain/445`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2815`

### Prompt

I need an isQ program to implements a variant of the phase_kickback pattern using u[1] -> u[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement iterative phase estimation (IPE) for the S gate (phase θ=π/4) on eigenstate |1⟩ using ancilla qubits, producing binary phase 0.01 (=1/4).
2. **Qubits**: Three registers — `u[3]` (eigenstate, only u[0] used), `anc1[1]` (round 1 ancilla), `anc0[1]` (round 2 ancilla). Only anc1[0] and anc0[0] are measured.
3. **State evolution**:
   - `X(u[0])`: Prepares eigenstate |ψ₀⟩ = |0⟩⊗²|1⟩ (ancillas in |0⟩, u[0] in |1⟩)
   - **Round 1** (U^(2¹)=S²=Z): `H(anc1)`

## isqTrain/435

- task_id: `isqTrain/435`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `1711`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the bell_state_preparation pattern using a[1] -> a[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this circuit carefully.

The circuit has:
- q[0]: Alice's state to teleport
- a[0], a[1]: Alice's half of EPR pair (expanded register)
- b[0]: Bob's half of EPR pair

Let me trace through the state evolution:

Initial state: |0000⟩ (q[0], a[0], b[0], a[1])
Wait, let me think about the ordering. We have q[0], a[0], a[1], b[0].

Initial state: |0⟩_q ⊗ |0⟩_a0 ⊗ |0⟩_a1 ⊗ |0⟩_b = |0000⟩

1. H(a[0]); CNOT(a[0], b[0]):
   After H(a[0]): |0⟩ ⊗ |+⟩ ⊗ |0⟩ ⊗ |0⟩
   After CNOT(a[0], b[0]): |0⟩ ⊗ (|00⟩ + |11⟩)/√2 ⊗ |0⟩ (for a[0],b[0])
   Wait, a[1] is separate. Let me reconsider the qubit ordering.
   
   State: |0⟩_q ⊗ (|00⟩ + |11⟩)/√2_{a0,b0} ⊗ |0⟩_a1
   = (|0000⟩ + |0110⟩)/√2 in order q[0], a[0], a[1], b[0]
   
   Hmm, wait. Let me be more careful. The CNOT is between a[0] and b[0], and a[1] is just sitting there as |0⟩.
   
   In order q[0], a[0], a[1], b[0]:
   = (|0000⟩ + |0101⟩)/√2

2. X(q[0]):
   State: (|1000⟩ + |1101⟩)/√2

3. CNOT(q[0], a[0]):
   q[0] is control, a[0] is target
   = (|1000⟩ + |1011⟩)/√2 ... wait let me redo.
   
   Starting: (|1⟩|0⟩|0⟩|0⟩ + |1⟩|1⟩|0⟩|1⟩)/√2
   CNOT(q[0], a[0]) flips a[0] when q[0]=|1⟩:
   = (|1⟩|1⟩|0⟩|0⟩ + |1⟩|0⟩|0⟩|1⟩)/√2
   = (|1100⟩ + |1001⟩)/√2

4. H(q[0]):
   H|1⟩ = |−⟩ = (|0⟩ - |1⟩)/√2
   = ((|0⟩ - |1⟩)|1⟩|0⟩|0⟩ + (|0⟩ - |1⟩)|0⟩|0⟩|1⟩)/2
   = (|0100⟩ - |1100⟩ + |0001⟩ - |1001⟩)/2

5. Measurements:
   mq = M(q[0]), ma = M(a[0]), M(a[1])
   
   The four terms have:
   - |0100⟩: q[0]=0, a[0]=1, a[1]=0, b[0]=0 → mq=0, ma=1
   - |1100⟩: q[0]=1, a[0]=1, a[1]=0, b[0]=0 → mq=1, ma=1
   - |0001⟩: q[0]=0, a[0]=0, a[1]=0, b[0]=1 → mq=0, ma=0
   - |1001⟩: q[0]=1, a[0]=0, a[1]=0, b[0]=1 → mq=1, ma=0

6. Conditional operations on b[0]:
   - |0100⟩: ma=1 → X(b[0]) → |0101⟩, mq=0 → no Z → |0101⟩
   - |1100⟩: ma=1 → X(b[0]) → |1101⟩, mq=1 → Z(b[0]) → Z|1⟩ = -|1⟩, so -|1101⟩
   - |0001⟩: ma=0 → no X → |0001⟩, mq=0 → no Z → |0001⟩
   - |1001⟩: ma=0 → no X → |1001⟩, mq=1 → Z(b[0]) → Z|1⟩ = -|1⟩,

## isqTrain/436

- task_id: `isqTrain/436`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `2903`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the bell_state_preparation pattern using b[1] -> b[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Looking at this problem, I need to analyze a quantum teleportation circuit that uses an expanded qubit register with `b[2]` instead of the base version.

Let me trace through the circuit:

1. **Initial state**: |0000⟩ for qubits q[0], a[0], b[0], b[1]

2. **EPR pair creation**:
   - H(a[0]): |0000⟩ → |0⟩⊗(|0⟩+|1⟩)/√2⊗|0⟩⊗|0⟩
   - CNOT(a[0], b[0]): → |0⟩⊗(|00⟩+|11⟩)/√2⊗|0⟩

3. **Alice's state preparation**:
   - X(q[0]): |1⟩⊗(|00⟩+|11⟩)/√2⊗|0⟩

4. **Alice's operations**:
   - CNOT(q[0], a[0]): |1⟩⊗(|10⟩+|01⟩)/√2⊗|0⟩ (entangling q[0] with a[0])
   - H(q[0]): (|0⟩-|1⟩)/√2 ⊗ (|10⟩+|01⟩)/√2 ⊗ |0⟩
   Wait, let me recalculate. After CNOT(q[0], a[0]):
   - State is |1,1,0,0⟩ + |1,0,1,0⟩ (ignoring normalization)
   After H(q[0]):
   - (|0⟩-|1⟩)⊗(|10⟩+|01⟩)⊗|0⟩/2
   - = (|0100⟩+|0010⟩-|1100⟩-|1010⟩)/2

5. **Measurements**:
   - M(q[0]) and M(a[0]) collapse the state

Let me think about the measurement outcomes:

The state before measurement is:
(|0⟩|1⟩|0⟩|0⟩ + |0⟩|0⟩|1⟩|0⟩ - |1⟩|1⟩|0⟩|0⟩ - |1⟩|0⟩|1⟩|0⟩)/2

In terms of (q, a, b[0], b[1]):
- |0100⟩ + |0010⟩ - |1100⟩ - |1010⟩ all divided by 2

Measurement outcomes (q, a):
- (0, 1): probability 1/4, post-measure state is |0100⟩ → after corrections, b[0] gets X, so |0110⟩
- (0, 0): probability 1/4, post-measure state is |0010⟩ → no corrections, |0010⟩... wait

Let me redo this more carefully.

After H(q[0]), the state is:
(|0⟩ - |1⟩)/√2 ⊗ (|10⟩ + |01⟩)/√2 ⊗ |0⟩

Expanding:
= (|0100⟩ + |0010⟩ - |1100⟩ - |1010⟩)/2

where the order is q[0], a[0], b[0], b[1].

Now measuring q[0] and a[0]:

- mq=0, ma=1: |0100⟩/√(1/4) → b[0]=0, apply X(b[0]) → |0110⟩
- mq=0, ma=0: |0010⟩/√(1/4) → b[0]=1, no X → |0010⟩
- mq=1, ma=1: |1100⟩/√(1/4) → b[0]=0, apply X(b[0]) → |1110⟩, then Z(b[0]) → -|1110⟩
- mq=1, ma=0: |1010⟩/√(1/4) → b[0]=1, no X, apply Z(b[0]) → -|1010⟩

Hmm, but The predicted output {|0000>, |0110>, |1000>, |1110>} with probability 0.25 each.

Let me reconsider. The measurements are:
- mq = M(q[0])
- ma = M(a[0])
- Then M(b[0]) and M(b[1])

For the output bitstring, earlier measured qubit = higher bit. So if we measure q[0], a[0], b[0], b[1] in that order, the bitstring would be q[0] as highest bit.

Actually wait, looking at the predicted output {|0000>, |0110>, |1000>, |1110>}, this suggests:
- b[1] is always 0 (since it

## isqTrain/433

- task_id: `isqTrain/433`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `intermediate`
- concept_tags: `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `3314`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

qbit c[1], q[1];

procedure main() {
    H(c[0]);
    int x = M(c[0]);
    if (x == 1) {
        X(q[0]);
    }
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ program**:
    *   Initialization: `qbit c[1], q[1];` -> 2 qubits. Both start in |0> state. State is |00> (where first qubit is c, second is q).
    *   Gate 1: `H(c[0]);` -> Apply H gate to `c[0]`. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   Measurement 1: `int x = M(c[0]);` -> Measure `c[0]`.
        *   If `c[0]` is |0>, x = 0. The state collapses to |00>. Probability = 0.5.
        *   If `c[0]` is |1>, x = 1. The state collapses to |10>. Probability = 0.5.
    *   Conditional: `if (x == 1) { X(q[0]); }`
        *   If state was |00>, nothing happens. State remains |00>.
        *   If state was |10>, X is applied to `q[0]`. State becomes |11>.
    *   Measurement 2: `M(q[0]);` -> Measure `q[0]`.
        *   If state was |00>, q[0] measurement yields 0. State was |00>.
        *   If state was |11>, q[0] measurement yields 1. State was |11>.
    *   The predicted measurement format is for both measurements.
    *   The prompt specifies: "Expected measurement probabilities: {|01>: 0.5, |11>: 0.5}". Wait, `|01>`? Let me re-read.
    *   Ah! `c[0]` is measured first. If x=1, `c[0]` was 1.
    *   Wait, let's look at the predicted output: `{|01>: 0.5, |11>: 0.5}`.
    *   Let's trace carefully:
        *   Initial: |00> (c[0]=0, q[0]=0).
        *   H(c[0]): $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
        *   M(c[0]) -> yields 0 with prob 0.5. Bitstring for c[0] is 0.
        *   M(c[0]) -> yields 1 with prob 0.5. Bitstring for c[0] is 1.
        *   "earlier measured qubit = higher bit". Wait, if c[0] is measured first, it's the higher bit.
        *   So if c[0] is 0, the bitstring starts with 0.
        *   If c[0] is 0, x=0, no X gate on q[0]. q[0] is 0. So bitstring is |00>.
        *   If c[0] is 1, the bitstring starts with 1.
        *   If c[0] is 1, x=1, X gate on q[0]. q[0] becomes 1. So bitstring is |11>.
        *   Wait, why does the reference say `{|01>: 0.5, |11>: 0.5}`? Let me re-read carefully.
        *   Is it possible that "higher bit" means index 0 is the left-most bit? Yes. So `c[0]` = 1 means the bitstring is `1_`.
        *   If `c[0]` = 0, bitstring is `0_`.
        *   Let's re-read the predicted output in the prompt: `Expected measurement probabilities: {|01>: 0.5, |11>: 0.5}`. Wait, if `{|01>: 0.5, |11>: 0.5}` is the expected, it implies `c[0]` is ALWAYS 1? No, that's impossible.
        *   Let's re-read the code.
        
        *   If x = 0 (50%), state is |00>, measure q[0] -> 0. Outcome: |00>.
        *   If x = 1 (50%), state is |10>, apply X -> |11>, measure q[0] -> 1. Outcome: |11

### Reference answer

{'predicted_probs': {'1': 0.5, '3': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/127. Dimension: predict probabilities for reference circuit.'}

## isqTrain/430

- task_id: `isqTrain/430`
- task_type: `code_generation`
- category: `isq_mixed_classical`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_if_else`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `4023`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the gate_decomposition pattern using c[1] -> c[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants a reasoning section for an isQ quantum program based on a provided circuit implementation.

circuit implementation Analysis:
- Qubits: `c[2]` and `q[1]`. Total 3 qubits: `c[0]`, `c[1]`, `q[0]`.
- Operations:
  1. `H(c[0])`: Puts `c[0]` into superposition `(|0> + |1>)/sqrt(2)`.
  2. `int x = M(c[0]); M(c[1]);`: Measures `c[0]` and `c[1]`. Wait, the reference says `int x = M(c[0]); M(c[1]);`. This collapses the states of `c[0]` and `c[1]`. Since `c[1]` is initialized to `|0>`, `M(c[1])` gives 0. `M(c[0])` gives 0 or 1 with equal probability.
  3. `if (x == 1) { X(q[0]); }`: If `c[0]` was 1, flip `q[0]` from `|0>` to `|1>`.
  4. `M(q[0]);`: Measures `q[0]`.
- Expected probabilities: {|001>: 0.5, |101>: 0.5}. Wait, let's check the order. `c[0]` is measured first, then `c[1]`, then `q[0]`.
  - Earlier measured qubit = higher bit. So `c[0]` is highest bit (bit 2), `c[1]` is bit 1, `q[0]` is bit 0.
  - If `c[0]=0`, `c[1]=0`, `q[0]=0` -> bitstring `000` -> wait, the expected says `001` and `101`.
  - Let me re-analyze the code and expected.
  - Ah, wait. The prompt says "expected measurement probabilities: {|001>: 0.5, |101>: 0.5}".
  - If `M(c[0])` is first, it's the highest bit (bit 2).
  - If `M(c[1])` is second, it's bit 1.
  - If `M(q[0])` is third, it's bit 0.
  - Let's trace:
    - Initial: `|000>` (c[0]=0, c[1]=0, q[0]=0).
    - After H(c[0]): `(|000> + |100>)/sqrt(2)`.
    - Measure c[0] and c[1]:
      - If result is 0,0: state is `|000>`, x=0. `q[0]` is not flipped. Measure `q[0]` -> result 0. Bitstring = `000`.
      - If result is 1,0: state is `|100>`, x=1. `q[0]` is flipped to `|1>`. State becomes `|101>`. Measure `q[0]` -> result 1. Bitstring = `101`.
  - Wait! The prompt says expected measurement probabilities: {|001>: 0.5, |101>: 0.5}. This doesn't match `000` and `101`. Why `001`?
  - Let's re-read the reference code:
    
    Wait, if the code is exactly as written, why would it be `001` and `101`?
    Is there a difference in bit order?
    Maybe `c[1]` is measured first? No, `M(c[0])` is first.
    Let's check the predicted output again: {|001>: 0.5, |101>: 0.5}. This means the highest bit is always 0, the middle bit is always 0, the lowest bit varies? No, `001` is 1, `101` is 5.
    In binary: `001` -> c[0]=0, c[1]=0, q[0]=1.
    `101` -> c[0]=1, c[1]=0, q[0]=1.
    If x=0, q[0] remains 0. If q[0] is 0, the bitstring ends in 0.
    Ah, maybe the expected measurement in the prompt is slightly mismatched or I am misinterpreting.
    Actually, the prompt says "Write an isQ program that implements a variant of the gate_de

## isqTrain/1978

- task_id: `isqTrain/1978`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `659`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[1];
procedure main() {
    U3(pi/2.0, 0.0, pi, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit, q[0], in the |0> state.
2. The gate `U3(pi/2, 0, pi)` is applied. Using the standard U3 matrix definition, this evaluates to the Hadamard (H) gate.
3. The H gate transforms the initial state into an equal superposition: (|0> + |1>)/√2, which is the |+> state.
4. Measuring the |+> state in the computational basis collapses it to either |0> or |1> with equal likelihood.

Predicted probability distribution: {'0': 0.5, '1': 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'U3(π/2, 0, π) ≡ H gate. P(|0⟩) ≈ P(|1⟩) ≈ 0.5.'}

## isqTrain/1955

- task_id: `isqTrain/1955`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2729`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];
procedure main() {
    H(q);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis

**Operations applied:**
1. H(q) — applies Hadamard gate to both q[0] and q[1]
2. M(q[0]) and M(q[1]) — measures both qubits

**State evolution:**
1. Initial state: |00⟩
2. After H(q[0]): (1/√2)(|00⟩ + |10⟩)
3. After H(q[1]): (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

**Final state:** (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩) — equal superposition of all four basis states.

**Predicted probability distribution:** {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'QRNG 0-3'}

## isqTrain/510

- task_id: `isqTrain/510`
- task_type: `output_prediction`
- category: `isq_mixed_classical`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2947`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[1];
procedure main() {
    X2P(q[0]);
    M(q[0]); // Rx(pi/2) -> 50/50
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit `q[0]` in the state |0> and applies an X2P gate, which corresponds to an Rx(π/2) rotation.
2. Initial state: |0⟩.
3. After X2P gate: The state evolves to cos(π/4)|0⟩ - i*sin(π/4)|1⟩ = (1/√2)|0⟩ - (i/√2)|1⟩.
4. Measuring the qubit in the computational basis yields a 50/50 probability distribution because the absolute squares of the amplitudes for |0⟩ and |1⟩ are equal.
Predicted probability distribution: {|0>: 0.5, |1>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5000000000000001, '1': 0.4999999999999999}, 'explanation': 'Parametric variant of isqHumanEval/147. Dimension: predict probabilities for reference circuit.'}

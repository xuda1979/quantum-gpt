# ISQ training COT RAG corpus: isq_advanced shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1631

- task_id: `isqTrain/1631`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1215`

### Prompt

Implement a quantum circuit in isQ: Bell state as a reusable procedure, then call it from main(). Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
- Goal: Create a reusable procedure to prepare the Bell state and measure the qubits.
- Qubits: 2 global qubits are used, both are measured.
- Evolution:
  1. Start in the initial state |00>.
  2. Apply H to q[0], creating a superposition: (1/sqrt(2))(|00> + |10>).
  3. Apply CNOT(q[0], q[1]), entangling the qubits into: (1/sqrt(2))(|00> + |11>).
- Probabilities: Measuring this maximally entangled state yields a 50% probability for |00> and 50% for |11>.

## isqTrain/4645

- task_id: `isqTrain/4645`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3352`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;

qbit q[2];
qbit anc[1];

procedure my_dj_oracle() {
    CNOT(q[0], anc[0]);
    nctrl X(q[1], anc[0]);
} deriving gate

procedure main() {
    
    H(q);
    X(anc[0]); 
    H(anc[0]);
    
    my_dj_oracle();
    
    
    
    
    
    H(q);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   `qbit q[2]; qbit anc[1];`: Three qubits total. `q[0]`, `q[1]`, `anc[0]` start at `|000>`.
    *   `H(q);`: Apply H to `q[0]` and `q[1]`. State becomes `1/2 (|00> + |01> + |10> + |11>)_q \otimes |0>_anc`.
    *   `X(anc[0]); H(anc[0]);`: Apply X then H to `anc[0]`. State of `anc[0]` becomes `|->`.
        Overall state: `1/2 (|00> + |01> + |10> + |11>) \otimes |->`.
    *   `my_dj_oracle();`:
        *   `CNOT(q[0], anc[0]);` flips `anc[0]` if `q[0]` is 1. The `anc[0]` is in `|-> = 1/\sqrt{2}(|0> - |1>)`. Phase kickback applies a -1 phase if `q[0]=1`.
        *   `nctrl X(q[1], anc[0]);`: This is a negative control CNOT. It flips `anc[0]` if `q[1]` is `|0>`. Phase kickback applies a -1 phase if `q[1]=0`.
        *   Let's trace the oracle's effect on the amplitudes:
            *   `|00>|->` -> `q[0]=0` (no flip), `q[1]=0` (flip) -> `-|00>|->`
            *   `|01>|->` -> `q[0]=0` (no flip), `q[1]=1` (no flip) -> `|01>|->`
            *   `|10>|->` -> `q[0]=1` (flip), `q[1]=1` (no flip) -> `-|10>|->`
            *   `|11>|->` -> `q[0]=1` (flip), `q[1]=1` (no flip) -> `-|11>|->`
            Wait, let's re-evaluate `nctrl X`.
            `nctrl X(q[1], anc[0])` means if `q[1] == 0`, apply X to `anc[0]`.
            Wait, `nctrl` is negative control.
            Let's re-read isQ `nctrl` syntax. Usually `nctrl X(q[1], anc[0])` is a negative controlled X.
            So:
            `|00>|->` -> CNOT(q[0]=0) does nothing. nctrl X(q[1]=0) applies X to anc. X|-> = -|->. So `-|00>|->`.
            `|01>|->` -> CNOT(q[0]=0) does nothing. nctrl X(q[1]=1) does nothing. So `|01>|->`.
            `|10>|->` -> CNOT(q[0]=1) applies X to anc. X|-> = -|->. nctrl X(q[1]=1) does nothing. So `-|10>|->`.
            `|11>|->` -> CNOT(q[0]=1) applies X to anc. X|-> = -|->. nctrl X(q[1]=1) does nothing. So `-|11>|->`.
            So overall state of q is `1/2 (-|00> + |01> - |10> - |11>) \otimes |->`.
    *   `H(q);`: Apply H to `q[0]` and `q[1]`.
        `H^{\otimes 2} \frac{1}{2}(-|00> + |01> - |10> - |11>)`.
        Let's compute H on each qubit:
        `q[1]`: `1/\sqrt{2}(-|0> + |1>) \xrightarrow{H} |1>`.
        `q[0]`: `1/\sqrt{2}(-|0> - |1>) \xrightarrow{H} -|1>`.
        So state is `-|11>`.
    *   `X(q[0]);`: Apply X to `q[0]`.
        `-|11> -> -|01>`.
    *   `M(q[0]); M(q[1]);`: Measure `q[0]` and `q[1]`.
        State is `-|01>`.

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|10>) = 1.0000.'}

## isqTrain/1724

- task_id: `isqTrain/1724`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2944`

### Prompt

Write an isQ program that a Bell state using nested procedures: apply_h wraps H, bell_via_h calls apply_h then CNOT.

### Chain-of-thought reasoning

## Reasoning
1. The circuit creates a maximally entangled Bell state by utilizing nested procedures where an inner function applies a Hadamard gate.
2. It requires 2 qubits, both of which are measured at the end of the routine.
3. Starting in the initial state $|00\rangle$, the `apply_h` procedure acts on the first qubit, evolving the state to $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
4. The `bell_via_h` procedure then applies a CNOT with the first qubit as control and the second as target, transforming the state to the entangled Bell state $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
5. Because the amplitudes for both $|00\rangle$ and $|11\rangle$ in the final state are $\frac{1}{\sqrt{2}}$, the probability of measuring either outcome is $\left|\frac{1}{\sqrt

## isqTrain/1970

- task_id: `isqTrain/1970`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4716`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[3];
procedure QFT(qbit arr[], int N) {
    for i in 0:N {
        H(arr[i]);
        for j in i+1:N {
            double angle = pi / (1 << (j - i));
            ctrl Rz(angle, arr[j], arr[i]);
        }
    }
}
procedure main() {
    X(q[0]);
    QFT(q, 3);
    CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program and predict the probability distribution of measurement outcomes.
The circuit has 3 qubits.
1. X(q[0]) -> state is |100>
2. QFT(q, 3) applied to |100>
3. 3 CNOTs: CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]); this is swap (three-CNOT decomposition)(q[0], q[2]).

Let's trace QFT(q, 3) on |q[2], q[1], q[0]> = |001>.
Wait, standard QFT index mapping:
The state |100> means q[0]=0, q[1]=0, q[2]=1.
QFT definition in code:
for i in 0:3:
  i=0: H(q[0]), Rz(pi/2, q[1], q[0]), Rz(pi/4, q[2], q[0])
  i=1: H(q[1]), Rz(pi/2, q[2], q[1])
  i=2: H(q[2])

Let's apply to |100> (q[0]=0, q[1]=0, q[2]=1):
i=0:
  H(q[0]) -> |100> becomes |+00> = 0.5 (|000> + |100>)
  Rz(pi/2, q[1], q[0]): ctrl is q[1], target is q[0]. Wait, ctrl Rz(angle, arr[j], arr[i])
  `ctrl Rz(angle, arr[j], arr[i])` means arr[j] is control, arr[i] is target.
  Wait, in standard QFT, arr[j] is control, arr[i] is target? Or arr[i] is control, arr[j] is target?
  `ctrl Rz(angle, arr[j], arr[i]);` -> this applies Rz(angle) to arr[i] controlled by arr[j].
  But standard isQ syntax might be `ctrl Rz(angle, target, control)` or `ctrl Rz(angle, control, target)`?
  Wait, if it's `ctrl Rz(angle, arr[j], arr[i])` where arr[j] is the first argument, usually CNOT is CNOT(control, target). So arr[j] is control, arr[i] is target?
  Wait! `ctrl Rz(angle, arr[j], arr[i])` The gate is Rz. The parameters for ctrl Rz are (angle, target, control)? No, the syntax is `ctrl @[*] Gate(...)`.
  Let's look at the syntax reference: "Control modifier: `ctrl @[c1, c2] Gate(target);`" - wait, but here it's just `ctrl Rz(angle, arr[j], arr[i])`. This means arr[j] is control and arr[i] is target?
  Actually, `ctrl Rz(angle, control, target)` is a common convention in some frameworks (like PyAQ), but in isQ, `ctrl Rz(angle, q[j], q[i])` usually means q[j] is control, q[i] is target. Wait! No!
  Let's check standard QFT. In QFT, if we process qubit i, we apply H(q[i]), then for each j>i, we apply controlled phase from q[j] to q[i] (if q[j] is less significant) OR from q[i] to q[j].
  Wait, the phase in QFT is $Z_{2^{j-i}}$. It's controlled by q[j].
  If it's controlled by q[j], then q[j] is the control. `ctrl Rz(angle, arr[j], arr[i])` -> arr[j] is control, arr[i] is target.
  Let's see: q[0] is initially 0, q[1] is 0, q[2] is 1.
  Initial state: |100>.
  i=0:
  H(q[0]) -> 1/sqrt(2) (|000> + |100>)
  Rz(pi/2) on q[0] ctrl q[1] -> q[1] is 0, so nothing happens.
  Rz(pi/4) on q[0] ctrl q[2] -> q[2] is 1, so Rz(pi/4) on q[0].
  1/sqrt(2) (|000> + e^{i\pi/4} |100>)
  i=1:
  H(q[1]) -> q[1] is 0, so H does nothing to the phase, just splits q[1]:
  1/sqrt(2) [ 1/sqrt

### Reference answer

{'predicted_probs': {'000': 0.125, '001': 0.125, '010': 0.125, '011': 0.125, '100': 0.125, '101': 0.125, '110': 0.125, '111': 0.125}, 'explanation': 'Template procedure dynamics'}

## isqTrain/499

- task_id: `isqTrain/499`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4006`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the oracle_boolean pattern using p[1] -> p[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Analyzing the isQ circuit step by step.

1. Goal: Implement a variant of the oracle_boolean pattern using q[1] and p[2] registers with two different oracle operations.

2. Qubits: 3 qubits total (q[1], p[2]). All three are measured: q[0], p[0], p[1].

3. State evolution:

Initial state: |000⟩ (q[0], p[0], p[1])

**First oracle on q[0]: execute_oracle(q[0], oracleA)**
- H(q[0]): |000⟩ → (|000⟩ + |100⟩)/√2
- oracleA = X(q[0]): (|100⟩ + |000⟩)/√2 = (|000⟩ + |100⟩)/√2
- H(q[0]): |000⟩ (back to |0⟩)
  
Wait, let me redo this more carefully.

H X H on |0⟩:
- H|0⟩ = |+⟩
- X|+⟩ = |+⟩ (X doesn't change |+⟩)
- H|+⟩ = |0⟩

So after execute_oracle(q[0], oracleA): q[0] is back in |0⟩.
State: |000⟩

**Second oracle on p[0]: execute_oracle(p[0], oracleB)**
- H(p[0]): |000⟩ → (|000⟩ + |010⟩)/√2
- oracleB = Z(p[0]): Z(|+⟩) = |−⟩, so (|000⟩ - |010⟩)/√2
- H(p[0]): H|−⟩ = |1⟩, so |010⟩

Wait, but p[1] is never touched, so it stays in |0⟩.

State after all operations: |010⟩

But wait, p[1] is measured too. p[1] is never operated on, so it's |0⟩.

State: q[0]=0, p[0]=1, p[1]=0 → |010⟩

But The predicted output {|100>: 1.0}.

Measurement order: M(q[0]), M(p[0]), M(p[1]).
Earlier measured qubit = higher bit.

So the bitstring is: q[0] as highest bit, p[0] as middle, p[1] as lowest.
q[0]=0, p[0]=1, p[1]=0 → bitstring = 010 (binary) = 2

But expected is |100⟩ which means q[0]=1, p[0]=0, p[1]=0.

Hmm, that doesn't match my calculation. Let me re-examine.

Wait, H Z H on |0⟩:
- H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2
- Z|+⟩ = (|0⟩-|1⟩)/√2 = |−⟩
- H|−⟩ = |1⟩

So HZH = X, and X|0⟩ = |1⟩. So p[0] becomes |1⟩.

And H X H on |0⟩:
- H|0⟩ = |+⟩
- X|+⟩ = |+⟩
- H|+⟩ = |0⟩

So q[0] stays |0⟩.

State: q[0]=0, p[0]=1, p[1]=0

Bitstring with earlier measured = higher bit: q[0] is bit 2, p[0] is bit 1, p[1] is bit 0.
= 0*4 + 1*2 + 0*1 = 2 = 010 in binary

But the expected says {|100>: 1.0}. That would be q[0]=1, p[0]=0, p[1]=0 = bitstring 100 = 4.

There's a discrepancy. Let me re-analyze the output: "Expected measurement probabilities: {|100>: 1.0}"

Hmm, maybe the comment in the code says "should be 01 (index 1)" which seems to suggest only measuring q[0] and p[0], giving 01. But the problem says 3 qubits are measured and the result is |100⟩.

Actually wait, let me re-read: "Expected measurement probabilities: {|100>: 1.0}" and "Number of qubits measured: 3"

But the comment says "// should be 01 (index 1)". This seems inconsistent.

Let me just go with what makes mathematical sense. The final state should be |010⟩ with q[0]=0, p[0]=1, p[1]=0.

Actually, I think there might be an error in

## isqTrain/537

- task_id: `isqTrain/537`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `5341`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the gate_decomposition pattern using w[5] -> w[7]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. The circuit implements an entangling gate decomposition pattern on a 7-qubit register, then applies Hadamard-based mixing, measuring the first 5 qubits while leaving w[5], w[6] in the ground state.

2. Uses 7 qubits (w[0]-w[6]), measuring w[0]-w[4] (5 qubits); w[5], w[6] remain unmeasured in |0⟩.

3. **State evolution:**
   - **Initialization:** |0000000⟩
   - **First loop (i=0:3):** X2P(w[i]) and Y2P(w[i+1]) rotate neighboring pairs, then CNOT(w[i],w[i+1]) entangles them, creating a cascade of entangled states across w[0]-w[4]
   - **Nested Hadamard loop:** H applied to indices (i+j+k)%5 for i,j,k∈0:3 applies Hadamard gates to the first 5 qubits in specific patterns, creating superposition
   - The combination yields an entangled superposition state on the first 5 qubits

4. **Final state and probabilities:** The circuit produces an equal superposition over 8 computational basis states (|00000⟩, |00100⟩, |01000⟩, |01100⟩, |10000⟩, |10100⟩, |11000⟩, |11100⟩), each with probability 1/8 ≈ 0.125. Bits at positions 3,4 (qubits w[3],w[4]) remain |0⟩ due to the gate structure, while bits 0-2 (qubits w[0]-w[2]) form the 8-state superposition.

## isqTrain/2605

- task_id: `isqTrain/2605`
- task_type: `code_equivalence`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `global_phase`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5112`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;

qbit q[4];

defgate MY_H = [
    0.7071067811865476, 0.7071067811865476;
    0.7071067811865476, -0.7071067811865476
];

procedure main() {
    for i in 0:4 {
        MY_H(q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

程序B：
```isq
import std;

qbit q[4];

defgate MY_H = [
    0.7071067811865476, 0.7071067811865476;
    0.7071067811865476, -0.7071067811865476
];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    for i in 0:4 {
        MY_H(q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A initializes 4 qubits to |0>, applies the custom `MY_H` gate (equivalent to the standard Hadamard gate) to each, putting them in the |+> state, and measures them.
2. Program B performs the exact same operations but precedes them with the `GPhase(0.0)` gate.
3. The key difference is the inclusion of `GPhase(0.0)` in Program B.
4. `GPhase(0.0)` multiplies the state vector by a global phase of $e^{i \cdot 0} = 1$, which acts strictly as an identity operation and has no effect on the quantum state.
5. Therefore, the quantum states before measurement are identical, resulting in the exact same measurement probability distributions.
Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/492

- task_id: `isqTrain/492`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4179`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;

qbit q[3];

procedure QFT(qbit arr[], int N) {
    for i in 0:N {
        H(arr[i]);
        for j in i+1:N {
            // Controlled Rz rotation
            double angle = pi / (1 << (j - i));
            ctrl Rz(angle, arr[j], arr[i]);
        }
    }
}

procedure main() {
    X(q[0]); // prepare |100>
    QFT(q, 3);
    
    // Manual SWAP for 3 qubits
    CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The program implements a Quantum Fourier Transform (QFT) on 3 qubits, starting from the state |100⟩.

1. Initial state: X(q[0]) is applied, so the state is |100⟩ (q[0]=1, q[1]=0, q[2]=0).

2. QFT on 3 qubits:
   - For i=0:
     - H(q[0]): |100⟩ → 1/√2(|000⟩ + |100⟩)
     - For j=1: ctrl Rz(π/1, q[1], q[0]) - since q[1]=|0⟩, this controlled gate does nothing
     - For j=2: ctrl Rz(π/2, q[2], q[0]) - since q[2]=|0⟩, this controlled gate does nothing
   
   Wait, I need to reconsider. The ctrl Rz gate with control q[j] and target q[i] applies Rz to q[i] when q[j] is |1⟩.
   
   Actually, looking at the code more carefully:
   
   
   In isQ, `ctrl Rz(angle, arr[j], arr[i])` means the control is arr[j] and the target is arr[i]. Wait, but typically in the QFT, we have controlled rotations where the more significant qubit controls the less significant one. Let me think about this more carefully.

   Actually, the syntax `ctrl Rz(angle, arr[j], arr[i])` in isQ means the control is the first qubit argument after the angle, so arr[j] controls, and arr[i] is the target. But wait, in standard QFT, the control is typically the lower index qubit and target is the higher index.

   Hmm, let me re-read the isQ syntax. The control modifier: `ctrl @[c1, c2] Gate(target);`. So `ctrl Rz(angle, arr[j], arr[i])` means arr[j] is the control and arr[i] is the target of the Rz rotation.

   But actually, I think there might be an issue with my interpretation. Let me reconsider.

   In the QFT, the standard implementation has:
   - H on qubit i
   - Controlled rotations from qubit j to qubit i, where j > i

   The rotation Rz(π/2^(j-i)) is applied to qubit i, controlled by qubit j.

   So in this code:
   - i=0: H(q[0]), then ctrl Rz(π, q[1], q[0]) and ctrl Rz(π/2, q[2], q[0])
     - The Rz rotations are applied to q[0], controlled by q[1] and q[2] respectively.
   
   But wait, the standard QFT uses controlled phase gates, not controlled Rz. Let me think about this...

   Actually, in the standard QFT, the controlled operation is a controlled phase rotation. The phase rotation R_k is defined as:
   R_k = [[1, 0], [0, e^(2πi/2^k)]]
   
   And Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]

   So R_k = e^(iπ/2^k) * Rz(π * 2/2^k) = e^(iπ/2^k) * Rz(2π/2^k)

   Hmm, this is getting complicated. Let me just trace through the state evolution.

   Initial state: |100⟩

   Step 1: H(q[0])
   |100⟩ → 1/√2(|000⟩ + |100⟩)

   Step 2: ctrl Rz(π, q[1], q[0])
   This applies Rz(π) to q[0] when q[1]=1. Since q[1]=0 in both terms, nothing happens.
   State: 1/√2(|000⟩ + |100⟩)

   Step 3: ctrl Rz(π/2, q[2], q[0])
   This applies Rz(π/2) to q[0] when q[2]=1. Since q[2]=0 in both terms, nothing happens.
   State: 1/√2(|000⟩ + |100⟩)

   Step 4: H(q[1])
   1/√2(|000⟩ + |100⟩) → 1/2(|000⟩ + |010⟩ + |100⟩ + |110⟩)

   Step 5: ctrl Rz(π, q

### Reference answer

{'predicted_probs': {'0': 0.12499999999999999, '1': 0.12499999999999999, '2': 0.12499999999999999, '3': 0.12499999999999999, '4': 0.12499999999999999, '5': 0.12499999999999999, '6': 0.12499999999999999, '7': 0.12499999999999999}, 'explanation': 'Parametric variant of isqHumanEval/141. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1635

- task_id: `isqTrain/1635`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3436`

### Prompt

Implement a quantum circuit in isQ: Apply X then inv X to |0>. Since X is self-inverse, result is |0>.

### Chain-of-thought reasoning

## Reasoning
The goal is to verify that the X gate is self-inverse by applying X followed by `inv X` to a qubit.
One qubit is required and measured.
State evolution:
1. Start with the initial state |0>.
2. Apply the X gate, which flips the state to |1>.
3. Apply `inv X`, which acts as another X gate (since X is its own inverse), flipping the state back to |0>.
The final quantum state is exactly |0>, so the measurement yields |0> with a probability of 1.0.

## isqTrain/1637

- task_id: `isqTrain/1637`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5279`

### Prompt

Help me write isQ code that Apply nctrl X (X when control is |0>) to |00>. Target flips when control=|0>.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply a negative-control X gate to |00⟩, where the target flips when control is |0⟩.
2. Two qubits needed (q[0] control, q[1] target), both measured.
3. State evolution: Initial state |00⟩ → nctrl X checks if q[0]=|0⟩ (true), so X applied to q[1] → |01⟩.
4. Measurement yields |01⟩ with probability 1.0.

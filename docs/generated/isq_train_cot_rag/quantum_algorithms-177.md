# ISQ training COT RAG corpus: quantum_algorithms shard 177

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3436

- task_id: `isqTrain/3436`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1846`

### Prompt

请用isQ语言编写一个量子电路：2 Trotter steps of a 4-qubit Ising chain in isQ.

H = -J*sum(Z_i*Z_{i+1}) - h*sum(X_i) for i=0..3.
Use J=1.0, h=0.5, dt=0.2.

Each Trotter step:
1. ZZ on pairs (0,1), (1,2), (2,3)
2. Rx on all 4 qubits

Repeat the step twice. Start from |0000>.
Declare 4 qubits, measure all.

### Chain-of-thought reasoning

Let me analyze this quantum circuit step by step.

The goal is to implement 2 Trotter steps of a 4-qubit Ising chain Hamiltonian evolution.

Hamiltonian: H = -J*sum(Z_i*Z_{i+1}) - h*sum(X_i) with J=1.0, h=0.5, dt=0.2

The Trotter decomposition splits this into:
1. ZZ interactions: e^{-i(-J)(Z_i*Z_j)dt} = e^{iJ*Z_i*Z_j*dt}
2. X field: e^{-i(-h)X_i*dt} = e^{ih*X_i*dt}

For ZZ interactions, exp(iθ*Z⊗Z) can be implemented as:
CNOT(0,1) * Rz(2θ, target) * CNOT(0,1)

The angle for ZZ is: 2*J*dt = 2*1.0*0.2 = 0.4
The angle for Rx is: 2*h*dt = 2*0.5*0.2 = 0.2

Let me trace the state evolution:

Initial state: |0000>

Trotter Step 1:
1. ZZ on (0,1): CNOT(q0,q1), Rz(0.4, q1), CNOT(q0,q1)
   - For |00⟩ on q0,q1: CNOT does nothing, Rz(0.4) applies e^{-i0.2}|0⟩, CNOT does nothing
   - So |00⟩ → e^{-i0.2}|00⟩
   
   After ZZ on (0,1): e^{-i0.2}|0000⟩

2. ZZ on (1,2): Same logic for q1,q2 in state |00⟩
   After: e^{-i0.4}|0000⟩

3. ZZ on (2,3): Same logic for q2,q3 in state |00⟩
   After: e^{-i0.6}|0000⟩

4. Rx(0.2) on all qubits: Rx(θ)|0⟩ = cos(θ/2)|0⟩ - i*sin(θ/2)|1⟩
   With θ=0.2: cos(0.1)|0⟩ - i*sin(0.1)|1⟩ ≈ 0.995|0⟩ - 0.0998i|1⟩

   The state becomes:
   e^{-i0.6} ⊗^4 (cos(0.1)|0⟩ - i*sin(0.1)|1⟩)
   
   Let c = cos(0.1) ≈ 0.995, s = sin(0.1) ≈ 0.0998
   
   State ≈ e^{-i0.6}(c|0⟩ - is|1⟩)^4

Trotter Step 2:
Similar operations on this now-superposition state.

The ZZ interactions will now create entanglement between the qubits since they're in superposition.

Let me think about this more carefully. After the first Rx applications, each qubit is in state α|0⟩ + β|1⟩ where α = cos(0.1), β = -i*sin(0.1).

The product state is:
(α|0⟩ + β|1⟩)⊗4 = α^4|0000⟩ + α^3β(|0001⟩+|0010⟩+|0100⟩+|1000⟩) + ... 

After Trotter step 2 ZZ interactions on this superposition, the phases will differ for different bitstrings depending on how many neighboring pairs of 1s there are.

For ZZ interaction: exp(i*0.2*Z⊗Z) applies:
- e^{i*0.2} to |00⟩ and |11⟩
- e^{-i*0.2} to |01⟩ and |10⟩

So for a 4-qubit state, the ZZ on (0,1), (1,2), (2,3) applies phase:
- exp(i*0.2*sum over neighboring pairs of (-1)^(z_i ⊕ z_{i+1}))
- Or equivalently: for each pair (i,i+1), if z_i = z_{i+1}, phase +0.2, else phase -0.2

Let me compute the phase for each computational basis state:
|0000⟩: all pairs same → 3*0.2 = 0.6
|0001⟩: (0,1)=0.2, (1,2)=0.2, (2,3)=-0.2 → 0.2
|0010⟩: (0,1)=0

## isqTrain/4643

- task_id: `isqTrain/4643`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5055`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];

procedure main() {
    
    X(q[0]);

    
    
    
    

    
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(0.785398163397448, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);

    
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(0.785398163397448, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);

    
    H(q[1]); // superposition on last qubit
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The circuit starts with 2 qubits in |00> state.

1. X(q[0]) → |10>

Now let me look at the pattern. The circuit has repeated blocks of:
- CNOT(q[0], q[1]); Rz(θ, q[1]); CNOT(q[0], q[1]);

This is the standard decomposition of CNOT-Rz-CNOT, which implements a controlled-Rz gate. When the control (q[0]) is |1>, the target (q[1]) gets Rz applied; when control is |0>, nothing happens. But actually, the phase is applied regardless of the control - wait, no. Let me think more carefully.

CNOT-Rz(θ)-CNOT on |00>: CNOT does nothing → Rz(θ) on q[1] → |0>⊗|0> (phase only on |1>) → CNOT does nothing. So |00> → e^0·|00> = |00>.

CNOT-Rz(θ)-CNOT on |01>: CNOT does nothing → Rz(θ) on q[1] → |0>⊗(e^{-iθ/2}|0> + ... wait, Rz applies phase. Actually Rz(θ)|0> = e^{-iθ/2}|0> and Rz(θ)|1> = e^{iθ/2}|1>. Wait, let me be more precise.

Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

So Rz(θ)|0> = e^{-iθ/2}|0>, Rz(θ)|1> = e^{iθ/2}|1>.

CNOT-Rz(θ)-CNOT on computational basis states:
- |00>: CNOT→|00>, Rz→e^{-iθ/2}|00>, CNOT→e^{-iθ/2}|00>
- |01>: CNOT→|01>, Rz→e^{iθ/2}|01>, CNOT→e^{iθ/2}|01>
- |10>: CNOT→|11>, Rz→e^{iθ/2}|11>, CNOT→e^{iθ/2}|10>
- |11>: CNOT→|10>, Rz→e^{-iθ/2}|10>, CNOT→e^{-iθ/2}|11>

So the effect on basis states:
- |00> → e^{-iθ/2}|00>
- |01> → e^{iθ/2}|01>
- |10> → e^{iθ/2}|10>
- |11> → e^{-iθ/2}|11>

This is actually a diagonal gate: diag(e^{-iθ/2}, e^{iθ/2}, e^{iθ/2}, e^{-iθ/2}).

Now there's also the block:
H(q[0]); H(q[1]); CNOT(q[0], q[1]); Rz(θ, q[1]); CNOT(q[0], q[1]); H(q[0]); H(q[1]);

H⊗H · CNOT-Rz(θ)-CNOT · H⊗H

This is conjugation by H⊗H, which transforms the Z-basis diagonal gate to an X-basis diagonal gate.

Actually, let me think about this differently. The H⊗H conjugation of the CNOT-Rz-CNOT block...

Let me think about what diagonal matrix we get.

Let me denote the CNOT-Rz(θ)-CNOT block as D(θ) = diag(e^{-iθ/2}, e^{iθ/2}, e^{iθ/2}, e^{-iθ/2}).

Then H⊗H · D(θ) · H⊗H transforms to... H⊗H maps |00> to |++>, |01> to |+->, |10> to |-+>, |11> to |-->.

The H⊗H conjugation of a ZZ interaction: since D(θ) = e^{-iθ/2} · diag(1, e^{iθ}, e^{iθ}, 1) = e^{-iθ/2} · exp(iθ/2 (Z⊗I + I⊗Z - Z⊗Z))... hmm, this is getting complicated.

Actually, let me just note: D(θ) = e^{-iθ/2} diag(1, e^{iθ}, e^{iθ}, 1).

In terms of Pauli operators: D(θ) = e^{-iθ/2} exp(iθ |11><11|) ... no.

Actually, diag(1, e^{iθ}, e^{iθ},

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.2500, P(|01>) = 0.2500, P(|10>) = 0.2500, P(|11>) = 0.2500.'}

## isqTrain/3555

- task_id: `isqTrain/3555`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3053`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 5-qubit repetition code: error on q[2], syndrome correction.

### Chain-of-thought reasoning

Let me analyze the bug in this isQ program.

The program is a 5-qubit repetition code with error injection and syndrome correction.

Looking at the encoding section:

Buggy code:

Fixed code:

The bug is in the first CNOT during encoding. In the buggy version, `CNOT(q[1], q[0])` has q[1] as control and q[0] as target. But q[0] is initially |0> and q[1] is also initially |0>. 

The goal is to encode |0> -> |00000>. The initial state is all qubits in |0>. To create |00000>, we need q[0] to be the control and copy its state to q[1], q[2], q[3], q[4].

Actually wait - if all qubits start in |0>, then CNOT(q[1], q[0]) with q[1]=|0> as control would do nothing (since control is |0>). So the state would remain |00000> after that gate. Then CNOT(q[0], q[2]) etc. would also do nothing since q[0] is still |0>.

Hmm, but the issue is the direction. The intent is to use q[0] as the "data" qubit that controls the others. In a repetition code, you typically have one data qubit and you copy it to the others.

If we start with all |0>:
- CNOT(q[0], q[1]) does nothing (q[0]=|0>)

So actually for encoding |0> -> |00000>, it doesn't matter because all qubits are |0>. But the bug would matter if q[0] started in |1> or if the error correction logic depends on proper encoding.

Actually, let me re-read. The encoding is supposed to take |0> on q[0] and produce |00000>. Since all qubits start at |0>, the CNOT gates don't really change anything - the state is already |00000>. 

But the bug description says "Wrong CNOT direction" and the fix changes `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`.

For the repetition code encoding to work correctly in general (not just for |0> input), q[0] should be the control. The buggy first CNOT has q[1] controlling q[0], which would be wrong if we were encoding a |1> state.

However, in this specific program, all qubits start as |0>, so the encoding phase doesn't actually change anything. The state remains |00000> after encoding regardless.

But wait - if q[0] were |1> and q[1] were |0>:
- Buggy: CNOT(q[1], q[0]) - control q[1]=|0>, target q[0]=|1> → no flip, state stays |10...>
- Correct: CNOT(q[0], q[1]) - control q[0]=|1>, target q[1]=|0> → flip, state becomes |11...>

So for encoding |1> -> |11111>, the buggy version would fail.

For this specific case with |0>, the encoding works either way. But the code is still buggy because:
1. It's logically incorrect for the repetition code structure
2. If the code were generalized to encode |1>, it would fail

Let me trace through the corrected circuit:

1. Initial: |00000>|0000> (5 data + 4 ancilla)

2. Encode: CNOT(q[0],q[1]), CNOT(q[0],q[2]), CNOT(q[0],q[3]), CNOT(q[0],q[4])
   - All controls are |0>, so nothing changes
   - State: |00000>|0000>

3. X(q[2]): flip q[2]
   - State: |00100>|0000>

4. Syndrome extraction:
   - CNOT(q[0], anc[0]): q[0]=|0>, nothing → anc[0]=|0>
   - CNOT(q[1], anc[0]): q[1]=|0>, nothing → anc[0]=|0>
   - CNOT(q[1], anc[1]): q[1]=|0>,

## isqTrain/860

- task_id: `isqTrain/860`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3252`

### Prompt

Implement the following in isQ: implements the integer_comparator pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a controlled-swap operation (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) with control=1, then measure in reversed order (q[2] before q[1]).
2. **Qubits**: 3 qubits; q[1] and q[2] are measured (q[0] is control only).
3. **State evolution**:
   - Start: |000⟩
   - X(q[0]): |100⟩ (control=1)
   - X(q[1]): |110⟩ (a=1, b=0)
   - CNOT(q[1],q[2]): |111⟩ (b flips to 1)
   - Toffoli(q[0],q[2],q[1]): |101⟩ (a flips to 0 since both controls are 1)
   - CNOT(q[1],q[2]): |101⟩ (b stays 1 since a=0)
4. **Result**: Final state is |101⟩. Since q[2] is measured first (higher bit) and q[1] second (lower bit), the 2-bit measurement outcome is "10" (q[2]=1, q[1]=0).
5. **Probabilities**: {|10⟩: 1.0} — deterministic result from classical states.

## isqTrain/4497

- task_id: `isqTrain/4497`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4954`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit q[3];

procedure main() {
    
    X(q[2]);
    
    H(q[0]);
    
    ctrl CNOT(q[0], q[1], q[2]);
    ctrl CNOT(q[0], q[2], q[1]);
    ctrl CNOT(q[0], q[1], q[2]);
    
    H(q[2]); // superposition on last qubit
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ program and predict measurement probabilities.
    *   Input Program: Sets q[2] to |1>, H on q[0], three Toffoli gates (ctrl CNOT) with alternating targets, then H on q[2].
    *   Format: "## Circuit Analysis" section, Dirac notation, concise (3-15 lines), end with the probability distribution.
    *   Qubits: q[0], q[1], q[2]

2.  **Trace the Circuit State:**
    *   Initial: |000>
    *   `X(q[2])`: |001> (q[2] is the last qubit, so if we use standard Dirac `q[2]q[1]q[0]`, it's `100`, but let's stick to `q[2]q[1]q[0]` or explicitly state. Let's use `q[2]q[1]q[0]` format internally to match standard bitstrings or just `|q[0]q[1]q[2]>` as requested by standard Qiskit-like or isQ bitstrings where `q[0]` is usually the highest bit if measured first? The prompt says "earlier measured qubit = higher bit" for the `--probs` array. Let's trace state as `|q[0], q[1], q[2]>`.)
    *   Let's use `|q[0], q[1], q[2]>` notation for state vectors.
    *   Init: `|0,0,0>`
    *   `X(q[2])`: `|0,0,1>`
    *   `H(q[0])`: `(1/√2)(|0,0,1> + |1,0,1>)`
    *   `ctrl CNOT(q[0], q[1], q[2])`: Toffoli with controls q[0], q[1], target q[2].
        *   `|0,0,1>` remains `|0,0,1>`
        *   `|1,0,1>` remains `|1,0,1>`
        *   Wait, `ctrl CNOT(q[0], q[1], q[2])` means `q[0]` and `q[1]` are controls, `q[2]` is target? No, wait.
        *   Syntax: `ctrl CNOT(c1, c2, t)`? No, isQ syntax: `ctrl @[c1, c2] Gate(target)` or Toffoli(c1, c2, target).
        *   Let's look at the input: `ctrl CNOT(q[0], q[1], q[2])`.
        *   If `ctrl CNOT(c, t)` is the standard, then `ctrl CNOT(c1, c2, t)` means controls are c1, c2, target is t. No, wait, if `CNOT(c, t)` takes 2 args, then `ctrl CNOT` would take 3. So controls = `q[0], q[1]`, target = `q[2]`.
        *   Let's re-read the prompt syntax reference: `ctrl @[c1, c2] Gate(target);`
        *   Ah! But the code literally says `ctrl CNOT(q[0], q[1], q[2]);`. This is likely isQ's syntax for a multi-controlled gate where all arguments are passed to the gate, or it's a Toffoli.
        *   Let's interpret `ctrl CNOT(q[0], q[1], q[2])` as controls `q[0]`, `q[1]` and target `q[2]`.
        *   Wait, is it `q[0]` is control, `q[1]`, `q[2]` are something else? No, `ctrl CNOT` means add a control to CNOT. CNOT takes (control, target). So `ctrl CNOT` takes (control1, control2, target). So `q[0]` and `q[1]` are controls, `q[2]` is target.
        *   Let's look at the sequence:
            1. `ctrl CNOT(q[0], q[1], q[2])` -> Toffoli(q0, q1, q2)
            2. `ctrl CNOT(q[0], q[2], q[1])` -> Toffoli(q0, q2, q1)
            3. `ctrl CNOT(q[0], q[1], q[2])`

### Reference answer

{'predicted_probs': {'000': 0.25, '001': 0.25, '110': 0.25, '111': 0.25}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.2500, P(|001>) = 0.2500, P(|110>) = 0.2500, P(|111>) = 0.2500.'}

## isqTrain/4194

- task_id: `isqTrain/4194`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2618`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[2], q[3]);
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

The circuit has 4 qubits, all initialized to |0⟩.

Step 1: Apply H to all 4 qubits
H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2

State after H gates: |+⟩|+⟩|+⟩|+⟩ = (1/4)(|0000⟩ + |0001⟩ + |0010⟩ + |0011⟩ + |0100⟩ + |0101⟩ + |0110⟩ + |0111⟩ + |1000⟩ + |1001⟩ + |1010⟩ + |1011⟩ + |1100⟩ + |1101⟩ + |1110⟩ + |1111⟩)

Step 2: CNOT(q[0], q[1])
This flips q[1] when q[0] is |1⟩.

Step 3: Rz(2.0 * 0.500, q[1]) = Rz(1.0, q[1])
Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
Rz(1.0) = [[e^(-i/2), 0], [0, e^(i/2)]]

Step 4: CNOT(q[0], q[1])

The sequence CNOT(c,t); Rz(θ,t); CNOT(c,t) applies a controlled-Rz gate, but let me think more carefully.

Actually, CNOT-Rz-CNOT is a standard decomposition. Let me think about what CNOT(q[0], q[1]); Rz(1.0, q[1]); CNOT(q[0], q[1]) does.

CNOT(c,t): |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩

So the sequence:
- |00⟩: CNOT→|00⟩, Rz on q1→|00⟩ (no change since q1 is |0⟩), CNOT→|00⟩. Result: |00⟩
- |01⟩: CNOT→|01⟩, Rz on q1→e^(i/2)|01⟩, CNOT→e^(i/2)|01⟩. Result: e^(i/2)|01⟩
- |10⟩: CNOT→|11⟩, Rz on q1→e^(i/2)|11⟩, CNOT→e^(i/2)|10⟩. Result: e^(i/2)|10⟩
- |11⟩: CNOT→|10⟩, Rz on q1→e^(-i/2)|10⟩, CNOT→e^(-i/2)|11⟩. Result: e^(-i/2)|11⟩

So this applies Rz(1.0) to the control qubit q[0], not the target! Wait, let me reconsider.

Actually wait - this is equivalent to CRz(θ) = diag(1, 1, 1, e^(iθ)) up to a global phase, applied to (q[0], q[1]).

Hmm, let me reconsider. The standard decomposition of CRz(θ) on (c, t) is:
- CNOT(t, c); Rz(θ, c); CNOT(t, c) — this gives controlled Rz on c with t as control

Actually no, let me just trace through more carefully.

CNOT(q[0], q[1]) means q[0] is control, q[1] is target.

For |00⟩: →|00⟩
For |01⟩: →|01⟩
For |10⟩: →|11⟩
For |11⟩: →|10⟩

After CNOT(q[0],q[1]):
|00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩

After Rz(1.0, q[1]):
|00⟩→|00⟩ (q[1]=0, phase e^(-1/2))
|01⟩→e^(i/2)|01⟩... wait, no. Rz(1.0) on qubit q[1]:

If q[1] is |0⟩: multiply by e^(-i/2)
If q[1] is |1⟩: multiply by e^(i/2)

Wait, Rz(θ)|0⟩ = e^(-iθ/2)|0⟩ and Rz(θ)|1⟩ = e^(iθ/2)|1⟩.

So after the second CNOT(q[0],q[1])

### Reference answer

Uniform distribution across 16 states

## isqExpand/algo/65

- task_id: `isqExpand/algo/65`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `vqe`, `hardware_efficient_ansatz`, `ry_cnot`
- source: `isq_expansion`
- dataset_index: `1059`

### Prompt

Help me write isQ code that implementing a VQE ansatz layer on 2 qubits. Apply Ry(pi/3) on both qubits as the parametric rotation layer, followed by a CNOT(q[0], q[1]) entangling gate. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Single VQE layer with identical Ry(pi/3) rotations on 2 qubits.

State evolution:
- Ry(pi/3) on q[0]: cos(pi/6)|0> + sin(pi/6)|1> = (sqrt3/2)|0> + (1/2)|1>
- Ry(pi/3) on q[1]: same
- Tensor product: (3/4)|00> + (sqrt3/4)|01> + (sqrt3/4)|10> + (1/4)|11>
- CNOT(q[0],q[1]): |10>->|11>, |11>->|10>
  - |00>: amp = (sqrt3/2)*(sqrt3/2) = 3/4
  - |01>: amp = (sqrt3/2)*(1/2) = sqrt3/4
  - |10>: amp from old |11> = (1/2)*(1/2) = 1/4
  - |11>: amp from old |10> = (1/2)*(sqrt3/2) = sqrt3/4

Probabilities: P(00)=9/16=0.5625, P(01)=3/16=0.1875, P(10)=1/16=0.0625, P(11)=3/16=0.1875

## isqTrain/3039

- task_id: `isqTrain/3039`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1564`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    nctrl X(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Gates applied:** `X(q[0])` and `nctrl X(q[0], q[1])` (zero-controlled X, q[0] controls q[1]).
2. **State evolution:**
   - Initial state: |00>
   - `X(q[0])` flips q[0]: |10>
   - `nctrl X(q[0], q[1])` applies X to q[1] only when q[0] is |0>. Since q[0] is |1>, the gate does nothing: |10>
3. **Final state before measurement:** |10>
4. **Predicted probability distribution:** The system is deterministically in the state |10>. Measurement of q[0] (higher bit) yields 1, and q[1] yields 0.

Probability distribution:
- "10": 1.0
- All other outcomes ("00", "01", "11"): 0.0

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2908

- task_id: `isqTrain/2908`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `927`

### Prompt

I need an isQ program to implementing the Bernstein-Vazirani algorithm with secret string s=1010 on 4 qubits.

Requirements:
- Use 4 input qubits and 1 ancilla.
- Define the oracle using the isQ `oracle` keyword.
- Declare main qubits at global scope.
- Use `procedure main()` as entry point.
- Measure all 4 input qubits.

### Chain-of-thought reasoning

## Reasoning
The goal is to implement the Bernstein-Vazirani algorithm to find the secret string s=1010.
The circuit uses 4 input qubits and 1 ancilla, measuring only the 4 input qubits.
The ancilla is initialized to |-> by applying X and H, while the input qubits are put into |+>⊗4 using H gates.
The oracle computes f(x) = s·x mod 2, applying a phase (-1)^(s·x) to each |x> via the ancilla.
Applying H gates to the input qubits again interferes the phases, collapsing the state to exactly |s> = |1010>.
The expected measurement probabilities are therefore P(|1010>) = 1.0.

## isqExpand/algo/107

- task_id: `isqExpand/algo/107`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `basis_change`, `reversible_computing`
- source: `isq_expansion`
- dataset_index: `2154`

### Prompt

帮我写一个isQ程序：prepares the state |101> (X on q[0] and q[2]), then applies the 3-qubit inverse Quantum Fourier Transform (IQFT). Use isQ's inv modifier for the Hadamard and controlled phase gates. The IQFT circuit is: inv H(q[0]), inv ctrl @[q[1]] S(q[0]), inv ctrl @[q[2]] T(q[0]), inv H(q[1]), inv ctrl @[q[2]] S(q[1]), inv H(q[2]), then SWAP q[0] and q[2] via 3 CNOTs. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply IQFT to |101> = |5>.

IQFT maps any computational basis state |j> to a uniform-magnitude superposition:
IQFT|j> = (1/sqrt(N)) sum_k exp(-2*pi*i*j*k/N) |k>

All amplitudes have magnitude 1/sqrt(8), so all probabilities = 1/8 = 0.125.
This holds for any computational basis input.

Expected: [0.125]*8

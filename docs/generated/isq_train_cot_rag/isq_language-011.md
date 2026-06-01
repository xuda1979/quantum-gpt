# ISQ training COT RAG corpus: isq_language shard 11

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/70

- task_id: `isqExpand/isqd/70`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `deriving_gate`, `custom_unitary`, `single_qubit`
- source: `isq_expansion`
- dataset_index: `1496`

### Prompt

Code this in isQ: defines a custom single-qubit gate equivalent to the Pauli-X gate using the `deriving gate` syntax with a 2x2 unitary matrix:

```
deriving gate myX = [[0, 1], [1, 0]];
```

Then apply `myX` to q[0] (which starts in |0>), and measure q[0].

Expected result: q[0] should be |1> with probability 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: Define a custom X gate via deriving gate with 2x2 matrix [[0,1],[1,0]].

1. deriving gate myX = [[0,1],[1,0]] defines the Pauli-X matrix.
2. myX(q[0]) on |0> -> |1>
3. M(q[0]) measures q[0]
4. Expected: P(|1>) = 1.0 at index 1

The 2x2 matrix is unitary (X†X = I), so the compiler accepts it.

## isqExpand/isqd/173

- task_id: `isqExpand/isqd/173`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `array_indexing`, `for_loop`, `qubit_register`, `out_of_bounds`
- source: `isq_expansion`
- dataset_index: `2770`

### Prompt

The following isQ code is supposed to apply a Hadamard gate to every qubit in a 3-qubit register, creating a uniform superposition over all basis states. However, it contains an array out-of-bounds error: the loop 'for i in 0:4' accesses q[3], which is invalid for qbit q[3] (valid indices are 0, 1, 2). Fix the loop range so that only valid indices are accessed.

### Chain-of-thought reasoning

The buggy code declares qbit q[3], meaning valid indices are 0, 1, and 2. The loop 'for i in 0:4' iterates i = 0, 1, 2, 3, so when i=3 it tries to access q[3], which is out of bounds for a size-3 array. The fix is to change the loop range to 'for i in 0:3', which iterates i = 0, 1, 2 — exactly the valid indices. After applying H to all three qubits, each qubit is in the |+⟩ state, and the joint state is an equal superposition over all 8 basis states, each with probability 1/8 = 0.125.

## isqExpand/isqd/8

- task_id: `isqExpand/isqd/8`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `nctrl_modifier`, `ctrl_modifier`, `wrong_modifier`
- source: `isq_expansion`
- dataset_index: `1619`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;
qbit q[2];

procedure main() {
    nctrl X(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
nctrl fires when the control qubit is |0>. Since q[0] starts in |0>, nctrl @[q[0]] X(q[1]) incorrectly flips q[1].

The intent is to flip q[1] only when q[0]=|1>. Since q[0] starts at |0> and is never flipped, neither qubit should change.

Fix: Replace nctrl with ctrl. With ctrl, the condition q[0]=|1> is not met, so X is not applied. Both qubits remain |0>.

## isqExpand/isqd/76

- task_id: `isqExpand/isqd/76`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `gate_decomposition`, `cz_gate`, `h_cnot_h`
- source: `isq_expansion`
- dataset_index: `250`

### Prompt

Help me write isQ code that implements the CZ (controlled-Z) gate using the decomposition CZ(a,b) = H(b); CNOT(a,b); H(b).

Define a procedure `my_cz(qbit a, qbit b)` implementing this decomposition.

In `main()`:
1. Prepare the state |+1> by applying H(q[0]) and X(q[1])
2. Apply my_cz(q[0], q[1])
3. Apply H(q[0]) to convert q[0] back from superposition to computational basis
4. Measure both qubits

Analysis: CZ on |+1> gives |−1> = (|0>−|1>)/sqrt(2)⊗|1>. H(q[0]) on |−> gives |1>. Final state: |11>.

Expected: P(|11>) = 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement CZ via H+CNOT+H and verify using |+1>.

1. H(q[0]): |0> -> |+> = (|0>+|1>)/sqrt(2)
2. X(q[1]): |0> -> |1>
3. State: |+>⊗|1> = (|01>+|11>)/sqrt(2)
4. my_cz(q[0],q[1]) = CZ:
   CZ|01> = |01> (not both 1)
   CZ|11> = -|11> (both 1)
   Result: (|01>-|11>)/sqrt(2) = |->⊗|1>
5. H(q[0]) on |->: |-> -> |1>
6. Final: |1>⊗|1> = |11>
7. P(|11>) = 1.0 at index 3.

## isqExpand/isqd/176

- task_id: `isqExpand/isqd/176`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `ctrl`, `nctrl`, `toffoli`, `positive_control`, `negative_control`, `mixed_control`
- source: `isq_expansion`
- dataset_index: `5638`

### Prompt

I need an isQ program to combining ctrl and nctrl: apply X to q[2] when q[0]=|1> AND q[1]=|0>. Use H gates on q[0] and q[1] to create superposition, then implement the mixed control using the X-flip technique (flip the negative control qubit, apply ctrl, then flip back).

### Chain-of-thought reasoning

The task requires applying X to q[2] when q[0]=|1> AND q[1]=|0>, combining positive and negative controls. After H(q[0]) and H(q[1]), we have equal superposition: (|000>+|100>+|010>+|110>)/2. To implement the negative control on q[1], we flip q[1] with X, making the condition q[1]=|0> become q[1]=|1>. Then we use ctrl @[q[0],q[1]] X(q[2]) as a standard doubly-controlled-X (Toffoli). Finally we flip q[1] back with X. The operation triggers only on |100> (q[0]=1, q[1]=0 flipped to q[1]=1), flipping q[2]: |100> -> |101>. Other basis states are unaffected. Final probabilities: |000>=0.25, |010>=0.25, |101>=0.25, |110>=0.25, all others 0.

## isqExpand/isqd/47

- task_id: `isqExpand/isqd/47`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `entanglement`
- source: `isq_expansion`
- dataset_index: `1110`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
qbit q[4];

procedure main() {
    for i in 0:4 {
        H(q[i]);
    }
    for i in 0:4 {
        CNOT(q[i], q[i+1]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The CNOT loop runs `for i in 0:4`, meaning i takes values 0,1,2,3. When i=3, q[i+1]=q[4] is out of bounds (array size is 4, indices 0-3).

Fix: Change `for i in 0:4` to `for i in 0:3` for the CNOT loop. This gives 3 CNOTs: (q[0],q[1]), (q[1],q[2]), (q[2],q[3]).

Result: H on all 4 + CNOT chain creates uniform distribution (P=1/16 each).

## isqExpand/isqd/62

- task_id: `isqExpand/isqd/62`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `procedure`, `bell_state`, `global_qbit`, `code_reuse`, `best_practice`
- source: `isq_expansion`
- dataset_index: `3087`

### Prompt

Code this in isQ: demonstrates the best practice of using a reusable procedure for creating Bell pairs. Define a procedure `bell_pair(qbit a, qbit b)` that applies H to the first qubit and CNOT(first, second). Then in main(), call bell_pair on q[0] and q[1], and measure both qubits. Declare qubits globally.

### Chain-of-thought reasoning

## Reasoning
Best practice task: demonstrate procedure reuse with global qubits.

1. Declare qbit q[2] globally (required for --probs).
2. Define bell_pair(qbit a, qbit b): H(a); CNOT(a,b);
3. In main(): call bell_pair(q[0], q[1]); then M(q[0]); M(q[1]);

Circuit trace:
- H(q[0]): (|0>+|1>)/sqrt(2) x |0> = (|00>+|10>)/sqrt(2)
- CNOT(q[0],q[1]): (|00>+|11>)/sqrt(2)
- P(|00>)=0.5, P(|11>)=0.5.

## isqExpand/isqd/182

- task_id: `isqExpand/isqd/182`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `h_gate`, `t_gate`, `inverse_gate`, `gate_cancellation`, `state_preparation`
- source: `isq_expansion`
- dataset_index: `3816`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    T(q[0]);
    inv T(q[0]);
    H(q[0]);
}
```

### Chain-of-thought reasoning

Starting from |0>, apply H to get (|0>+|1>)/sqrt(2). Apply T which adds phase e^(i*pi/4) to |1> component, giving (|0>+e^(i*pi/4)|1>)/sqrt(2). Apply inv T (T-dagger) which adds phase e^(-i*pi/4) to |1>, canceling exactly: (|0>+e^(-i*pi/4)*e^(i*pi/4)|1>)/sqrt(2) = (|0>+|1>)/sqrt(2). Apply H again: H((|0>+|1>)/sqrt(2)) = |0>. Since T and T-dagger are inverses, they cancel completely, leaving us with H(H|0>) = |0>. The measurement probabilities are P(|0>)=1.0 and P(|1>)=0.0.

### Reference answer

{'predicted_probs': {'0': 1.0, '1': 0.0}, 'explanation': 'Starting from |0>, H maps |0> to (|0>+|1>)/sqrt(2). T applies a phase e^(i*pi/4) to |1>. inv T (T-dagger) applies e^(-i*pi/4) to |1>, which exactly cancels the T phase. So after T then inv T, the state is still (|0>+|1>)/sqrt(2). The second H maps this back to |0>. The final measurement yields |0> with probability 1.0.'}

## isqExpand/isqd/11

- task_id: `isqExpand/isqd/11`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nctrl_modifier`, `ctrl_modifier`, `multi_control`, `mixed_control`
- source: `isq_expansion`
- dataset_index: `1000`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    nctrl ctrl X(q[1], q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[0]): state = q[0]=1, q[1]=0, q[2]=0
2. nctrl @[q[1]] ctrl @[q[0]] X(q[2]):
   - nctrl on q[1]: q[1]=|0> -> condition met
   - ctrl on q[0]: q[0]=|1> -> condition met
   - X applied to q[2]: q[2] -> |1>
3. Final: q[0]=1, q[1]=0, q[2]=1
4. Index = 1*4 + 0*2 + 1 = 5

Expected: [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]

### Reference answer

{'predicted_probs': {'000': 0.0, '001': 0.0, '010': 0.0, '011': 0.0, '100': 0.0, '101': 1.0, '110': 0.0, '111': 0.0}, 'explanation': 'Step-by-step:\n1. X(q[0]): q[0]=1, q[1]=0, q[2]=0. State: |100>\n2. nctrl @[q[1]] ctrl @[q[0]] X(q[2]):\n   - nctrl on q[1]: fires when q[1]=|0> -> YES\n   - ctrl on q[0]: fires when q[0]=|1> -> YES\n   - Both conditions met, X applied to q[2]: q[2] flips to |1>\n3. Final state: q[0]=1, q[1]=0, q[2]=1 = |101>\n4. Index = q[0]*4 + q[1]*2 + q[2] = 4 + 0 + 1 = 5\n\nResult: P(|101>) = 1.0 at index 5.\nFull distribution: [0, 0, 0, 0, 0, 1, 0, 0].'}

## isqExpand/isqd/158

- task_id: `isqExpand/isqd/158`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `global_phase`, `GPhase`, `Z_gate`, `measurement_invariance`
- source: `isq_expansion`
- dataset_index: `2074`

### Prompt

帮我写一个isQ程序：demonstrates GPhase(pi) followed by Z gives the same measurement probabilities as applying Z alone. Use two qubits: q[0] receives H then GPhase(pi) then Z, while q[1] receives H then Z. Measure both qubits. The expected outcome is uniform distribution over all four basis states, confirming the global phase has no observable effect.

### Chain-of-thought reasoning

Step 1: GPhase(theta) multiplies the entire quantum state by e^(i*theta). This is a global phase and has no effect on measurement probabilities. Step 2: For q[0], we apply H to get (|0⟩+|1⟩)/√2, then GPhase(pi) which gives -( |0⟩+|1⟩)/√2, then Z which gives -( |0⟩-|1⟩)/√2. The probabilities of measuring |0⟩ or |1⟩ are both 0.5. Step 3: For q[1], we apply H to get (|0⟩+|1⟩)/√2, then Z which gives (|0⟩-|1⟩)/√2. The probabilities of measuring |0⟩ or |1⟩ are also both 0.5. Step 4: Both qubits independently have 50/50 measurement outcomes regardless of the global phase, so the joint two-qubit distribution is uniform: [0.25, 0.25, 0.25, 0.25].

# ISQ training COT RAG corpus: isq_language shard 12

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/157

- task_id: `isqExpand/isqd/157`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `gphase`, `global_phase`, `hadamard`, `superposition`, `measurement_probabilities`
- source: `isq_expansion`
- dataset_index: `4025`

### Prompt

用isQ实现demonstrates the GPhase gate has no effect on measurement outcomes. Create a single qubit in superposition using Hadamard, apply GPhase(pi) to introduce a global phase, and confirm via measurement probabilities that the outcome distribution remains unchanged (50/50).

### Chain-of-thought reasoning

We need to show that GPhase(pi) has no effect on measurement probabilities. Starting with qubit in |0⟩, applying H gives (|0⟩+|1⟩)/√2. Then GPhase(π) multiplies the entire state by e^(iπ) = -1, yielding -( |0⟩+|1⟩)/√2. Since global phase is unobservable, the measurement probabilities remain |1/√2|² = 0.5 for both |0⟩ and |1⟩ outcomes. So expected_probs = [0.5, 0.5], confirming the global phase does not affect measurement.

## isqExpand/isqd/5

- task_id: `isqExpand/isqd/5`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `deriving_gate`, `ctrl_modifier`, `swap_decomposition`, `isq_syntax_procedures`
- source: `isq_expansion`
- dataset_index: `1967`

### Prompt

Implement the following in isQ: uses the deriving gate modifier to create a controlled version of a custom SWAP procedure.

Define a procedure swap_qubits(qbit a, qbit b) that swaps two qubits using three CNOT gates, and mark it with "deriving gate". Then in main():
1. Prepare the state |110> (X on q[0] and q[1])
2. Apply a controlled-swap: ctrl swap_qubits(q[0], q[1], q[2])
   Here q[0] is the control (|1>), so the swap of q[1] and q[2] executes.
   q[1]=|1>, q[2]=|0> get swapped to q[1]=|0>, q[2]=|1>.
3. Measure all three qubits.

The final state should be |101> with probability 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: Use deriving gate to make a custom SWAP procedure controllable.

The deriving gate modifier converts a pure-quantum procedure into a gate that supports modifiers like ctrl and inv.

1. Define swap_qubits with 3 CNOTs, mark with "deriving gate"
2. X(q[0]), X(q[1]): prepare |110>
3. ctrl swap_qubits(q[0], q[1], q[2]): q[0]=1 is control, swap executes on q[1],q[2]
4. q[1]=1 and q[2]=0 get swapped: q[1]=0, q[2]=1
5. Final state: q[0]=1, q[1]=0, q[2]=1 = |101>
6. Index = 1*4 + 0*2 + 1 = 5

Expected: P(|101>) = 1.0 at index 5

## isqExpand/isqd/45

- task_id: `isqExpand/isqd/45`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `isq_syntax_procedures`, `isq_syntax_arrays`
- source: `isq_expansion`
- dataset_index: `1513`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```isq
import std;
qbit q[3];

procedure apply_h_all(qbit a) {
    for i in 0:3 {
        H(a[i]);
    }
}

procedure main() {
    apply_h_all(q);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The procedure declares `qbit a` (a single qubit) but then tries to index it with `a[i]`, and main() passes the entire array `q`. The fix is to change the parameter to `qbit a[3]` so it accepts a 3-qubit array.

After fix: H applied to all 3 qubits -> uniform superposition -> each of 8 basis states has P=1/8=0.125.

## isqExpand/isqd/73

- task_id: `isqExpand/isqd/73`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `nctrl_modifier`, `negative_control`, `conditional_flip`
- source: `isq_expansion`
- dataset_index: `3883`

### Prompt

Help me write isQ code that uses the `nctrl` modifier (negative control) to flip a target qubit only when the control qubit is in state |0>.

Use 2 qubits. Leave q[0] in its initial state |0> (do NOT apply X). Apply `nctrl @[q[0]] X(q[1])`. Since q[0] = |0>, the nctrl condition is satisfied and X is applied to q[1].

Measure both qubits. Expected: P(|01>) = 1.0.

Note: nctrl fires when the control qubit is |0>, opposite to ctrl.

### Chain-of-thought reasoning

## Reasoning
Goal: Use nctrl (negative control) to flip q[1] when q[0]=|0>.

1. Initial state: |00>
2. nctrl @[q[0]] X(q[1]): q[0]=|0>, nctrl condition met, X applied to q[1]
3. State: |01>
4. Index = 0*2+1 = 1. P(|01>) = 1.0.

## isqExpand/isqd/178

- task_id: `isqExpand/isqd/178`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `negative_control`, `nctrl`, `x_gate`, `basis_state`
- source: `isq_expansion`
- dataset_index: `4153`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    nctrl X(q[0], q[1]);
}
```

### Chain-of-thought reasoning

Step 1: Start with initial state |00⟩ (both qubits in |0⟩).
Step 2: Apply X(q[0]) to flip q[0] from |0⟩ to |1⟩. State becomes |10⟩.
Step 3: Apply nctrl @[q[0]] X(q[1]). The negative control (nctrl) fires the target gate only when the control qubit is in |0⟩.
Step 4: Check control qubit q[0]: it is |1⟩. Since this is a negative control, the condition for firing is q[0]=|0⟩. Since q[0]=|1⟩, the X gate does NOT execute on q[1].
Step 5: q[1] remains |0⟩. Final state is |10⟩ with probability 1.0.
Step 6: Probabilities: |00⟩=0.0, |01⟩=0.0, |10⟩=1.0, |11⟩=0.0.

### Reference answer

{'predicted_probs': {'00': 0.0, '01': 0.0, '10': 1.0, '11': 0.0}, 'explanation': 'Initial state is |00⟩. After X(q[0]) the state becomes |10⟩. The nctrl (negative control) gate fires the target gate only when the control qubit is |0⟩. Since q[0]=|1⟩, the X gate does NOT fire on q[1], leaving q[1] unchanged at |0⟩. Final state: |10⟩.'}

## isqExpand/isqd/32

- task_id: `isqExpand/isqd/32`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `x_toffoli_x_pattern`, `missing_uncomputation`, `marking_oracle`, `common_error`
- source: `isq_expansion`
- dataset_index: `2387`

### Prompt

The following program intends to implement a phase oracle marking |01> on 2 qubits using the X-Toffoli-X pattern with CZ. The target bitstring is |01> (q[0]=0, q[1]=1), so q[0] needs X gates before and after the CZ. However, the programmer only added X before CZ but forgot to add X after CZ, leaving q[0] in a flipped state.

Fix the bug by adding the missing X(q[0]) after the CZ gate to restore q[0].

Verification: prepare (|0>+|1>)/sqrt(2) on q[0] and |1> on q[1]. State = (|01>+|11>)/sqrt(2). Oracle should mark |01> with -1 phase: (-|01>+|11>)/sqrt(2). Then H on q[0] reveals the phase as |11>.

### Chain-of-thought reasoning

## Bug Analysis
The X-Toffoli-X pattern requires X before and after the multi-controlled gate on qubits that are |0> in the target bitstring. The programmer forgot the second X(q[0]).

Buggy behavior:
1. H(q[0]): q[0] = |+>. X(q[1]): q[1]=|1>
2. State: (|01>+|11>)/sqrt(2)
3. mark_01 (buggy): X(q[0]) flips: (|11>+|01>)/sqrt(2) -> CZ marks |11>: (-|11>+|01>)/sqrt(2)
4. No second X: q[0] stays flipped. State is wrong.

Fixed behavior:
1. State: (|01>+|11>)/sqrt(2)
2. X(q[0]): (|11>+|01>)/sqrt(2)
3. CZ: (-|11>+|01>)/sqrt(2)
4. X(q[0]): (-|01>+|11>)/sqrt(2) (restored)
5. H(q[0]): (-|01>+|11>)/sqrt(2) -> collect: q[0] part: H acts on (-|0>+|1>)/sqrt(2) = -H|-> = -|1>
6. Final: -|1>|1> = -|11>. P(|11>)=1.0. Index=3.

## isqExpand/isqd/28

- task_id: `isqExpand/isqd/28`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `marking_oracle`, `x_toffoli_x_pattern`, `phase_oracle`, `bitstring_oracle`
- source: `isq_expansion`
- dataset_index: `817`

### Prompt

Code this in isQ: implements a phase oracle to mark the specific bitstring |101> using the X-Toffoli-X pattern with a ctrl-Z gate.

The oracle should add a (-1) phase to the |101> component. The X-Toffoli-X pattern works by:
1. Apply X to qubits that are |0> in the target bitstring (here q[1], since |101> has bit 1 = 0)
2. Apply a multi-controlled Z gate: ctrl @[q[0], q[1]] Z(q[2])
3. Apply X again to the same qubits to restore them (uncompute)

To verify: prepare |101> and put q[2] in superposition so the phase is detectable.
- Start: X(q[0]) to set q[0]=|1>, q[1]=|0>, H(q[2]) to put q[2] in |+>
- State before oracle: |10>(|0>+|1>)/sqrt(2) = (|100>+|101>)/sqrt(2)
- Oracle marks |101>: (|100>-|101>)/sqrt(2) = |10>(|0>-|1>)/sqrt(2) = |10>|->
- Apply H(q[2]): |10>|1> = |101>
- Measure: should get |101> with probability 1.0

### Chain-of-thought reasoning

## Reasoning
Goal: Phase oracle to mark |101> using X-Toffoli-X pattern.

Oracle construction for |101> (q[0]=1, q[1]=0, q[2]=1):
- q[1] is 0 in target, so apply X before and after the multi-controlled Z
1. X(q[1]): temporarily flip q[1]
2. ctrl @[q[0], q[1]] Z(q[2]): triggers only when all three are |1> (i.e., original state was |101>)
3. X(q[1]): restore q[1]

Verification circuit:
1. X(q[0]): q[0]=|1>, q[1]=|0>
2. H(q[2]): q[2]=|+>
3. State: (|100>+|101>)/sqrt(2)
4. mark_101(): |101> gets -1 phase -> (|100>-|101>)/sqrt(2) = |10>(|0>-|1>)/sqrt(2) = |10>|->
5. H(q[2]): |-> -> |1>
6. Final: |101>. Index = 5. P=1.0.

## isqExpand/isqd/100

- task_id: `isqExpand/isqd/100`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `compile_error`, `syntax_error`
- source: `isq_expansion`
- dataset_index: `5557`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
qbit q[1];

procedure measure_qubit(qbit a) : int {
    int r = M(a);
    return r;
}

procedure main() {
    H(q[0]);
    int result = measure_qubit(q[0]);
    print result;
}
```

### Chain-of-thought reasoning

## Bug Analysis
Buggy: `procedure measure_qubit(qbit a) : int` -- isQ procedures do not support return types in this form.
Fix: inline measurement into main().
After fix: H creates |+>, M returns 0 or 1. Nondeterministic.

## isqExpand/isqd/180

- task_id: `isqExpand/isqd/180`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `S_gate`, `inverse_gate`, `identity_verification`, `gate_cancellation`
- source: `isq_expansion`
- dataset_index: `1504`

### Prompt

I need an isQ program to demonstrates S followed by inv S gives identity (S†S = I). Apply H to qubit 0 to create superposition, then apply S, then apply inv S, and verify the state is unchanged (50/50 measurement probabilities).

### Chain-of-thought reasoning

The S gate applies a phase of i to the |1⟩ state: S = [[1,0],[0,i]]. Its inverse S† applies a phase of -i to |1⟩: S† = [[1,0],[0,-i]]. The product S†·S = [[1,0],[0,-i·i]] = [[1,0],[0,1]] = I (identity). So applying S then inv S should leave any quantum state unchanged. Starting from |0⟩, after H we have (|0⟩+|1⟩)/√2. After S we have (|0⟩+i|1⟩)/√2. After inv S we return to (|0⟩+|1⟩)/√2. Measuring gives 50% probability for both |0⟩ and |1⟩, confirming the net effect is identity.

## isqExpand/isqd/105

- task_id: `isqExpand/isqd/105`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `toffoli`, `multi_controlled_logic`, `nctrl_modifier`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `998`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    // Toffoli: flip q[2] iff both q[0] AND q[1] are |1>
    ctrl ctrl X(q[0], q[1], q[2]);
    // nctrl: flip q[2] iff q[0] is |0>
    nctrl X(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[0]), X(q[1]): |110>
2. Toffoli: both controls 1 -> q[2] flips. |111>
3. nctrl @[q[0]] X(q[2]): q[0]=1, nctrl needs 0 -> no fire. |111>
4. P(|111>)=1.0 at index 7.
Distribution: all zero except index 7 = 1.0.

### Reference answer

{'predicted_probs': {'000': 0.0, '001': 0.0, '010': 0.0, '011': 0.0, '100': 0.0, '101': 0.0, '110': 0.0, '111': 1.0}, 'explanation': 'Step-by-step:\n1. X(q[0]), X(q[1]): q[0]=|1>, q[1]=|1>, q[2]=|0>. State: |110>\n2. ctrl @[q[0], q[1]] X(q[2]): both |1>, fires. q[2]->|1>. State: |111>\n3. nctrl @[q[0]] X(q[2]): q[0]=|1>, nctrl needs |0>. Does NOT fire. State: |111>\n4. P(|111>) = 1.0 at index 7.\nDistribution: [0,0,0,0,0,0,0,1.0].'}

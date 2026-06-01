# ISQ training COT RAG corpus: isq_language shard 14

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/179

- task_id: `isqExpand/isqd/179`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `controlled_gates`, `negative_control`, `ctrl`, `nctrl`, `bell_state`, `entanglement`
- source: `isq_expansion`
- dataset_index: `1395`

### Prompt

The following isQ program is intended to create a Bell state (|00⟩+|11⟩)/√2 by applying a Hadamard to qubit 0 and then a controlled-X gate with qubit 0 as control and qubit 1 as target. However, the programmer accidentally used 'nctrl' (negative control) instead of 'ctrl' (positive control). The negative control fires the gate when the control is |0⟩ instead of |1⟩, producing the wrong entangled state (|01⟩+|10⟩)/√2. Fix the bug by replacing 'nctrl' with 'ctrl'.

### Chain-of-thought reasoning

Step 1: Analyze the buggy code. After H(q[0]), the state of qubits q[0],q[1] is (|00⟩+|10⟩)/√2. Step 2: The buggy code uses nctrl @[q[0]] X(q[1]), which applies X to q[1] when q[0] is |0⟩. This transforms |00⟩→|01⟩ while leaving |10⟩ unchanged, yielding (|01⟩+|10⟩)/√2 with probabilities [0.0, 0.5, 0.5, 0.0]. Step 3: The intended behavior is to create a Bell state (|00⟩+|11⟩)/√2. This requires X on q[1] when q[0] is |1⟩, which is achieved by ctrl (positive control), not nctrl. Step 4: The fix is replacing 'nctrl' with 'ctrl'. After the fix, ctrl @[q[0]] X(q[1]) fires X on q[1] when q[0]=|1⟩, transforming |10⟩→|11⟩ and yielding (|00⟩+|11⟩)/√2 with probabilities [0.5, 0.0, 0.0, 0.5].

## isqExpand/isqd/39

- task_id: `isqExpand/isqd/39`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `isq_syntax_arrays`, `basis_change`
- source: `isq_expansion`
- dataset_index: `5553`

### Prompt

实现以下量子计算任务（使用isQ）：defines a procedure `apply_ry_layer(qbit reg[3], double angle)` which applies Ry(angle) to every qubit in the 3-qubit array `reg`. In `main()`, declare a global 3-qubit array, call the procedure with angle = 3.14159 (i.e., pi, which is equivalent to a bit-flip), and measure all three qubits.

Since Ry(pi) rotates |0> to |1>, all three qubits should end up in state |1>, producing the deterministic output |111> with probability 1.0.

Requirements:
- The procedure must take `qbit reg[3]` and `double angle` as parameters.
- Use a for loop inside the procedure to apply Ry to each qubit.
- Measure all qubits in main().

### Chain-of-thought reasoning

## Reasoning
Goal: Define procedure with qbit array + double params, apply Ry(pi) to all.

1. procedure apply_ry_layer(qbit reg[3], double angle) iterates 0:3 applying Ry.
2. Ry(pi)|0> = |1> (rotation by pi around Y axis).
3. All three qubits become |1>.
4. Final state: |111>, index = 4+2+1 = 7.
5. Expected: P(|111>) = 1.0 at index 7.

## isqExpand/isqd/160

- task_id: `isqExpand/isqd/160`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `global_phase`, `hadamard_gate`, `measurement_probabilities`, `single_qubit`
- source: `isq_expansion`
- dataset_index: `5680`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[1];
procedure main() {
    GPhase(pi);
    H(q[0]);
}
```

### Chain-of-thought reasoning

Step 1: The initial state of q[0] is |0⟩.
Step 2: GPhase(pi) applies a global phase of π to the entire quantum state. A global phase does not change any measurement probabilities — it is physically unobservable. The state remains effectively |0⟩.
Step 3: H(q[0]) applies the Hadamard gate to |0⟩, producing H|0⟩ = (|0⟩+|1⟩)/√2 = |+⟩.
Step 4: Measuring |+⟩ in the computational basis yields |0⟩ with probability |1/√2|² = 0.5 and |1⟩ with probability |1/√2|² = 0.5.
Therefore, the predicted probabilities are P(0)=0.5 and P(1)=0.5.

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'GPhase(pi) applies a global phase which does not affect measurement probabilities. H(q[0]) applied to |0⟩ creates an equal superposition (|0⟩+|1⟩)/√2, yielding 50% for each outcome.'}

## isqExpand/isqd/174

- task_id: `isqExpand/isqd/174`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `measurement`, `bell_state`, `entanglement`, `bug_fix`
- source: `isq_expansion`
- dataset_index: `94`

### Prompt

The following isQ program creates a Bell state on two qubits but never measures them. As a result, no measurement results are produced. Add the missing M() measurements so that both qubits are measured and the output probabilities can be extracted.

### Chain-of-thought reasoning

The buggy code creates a Bell state by applying H(q[0]) followed by CNOT(q[0], q[1]), which produces the entangled state (|00⟩ + |11⟩)/√2. However, no M() measurement operations are performed on any qubits. Without measurements, no classical outcomes or probability distributions are generated, so the program cannot be verified with check_mode 'probs'. The fix is to add M(q[0]) and M(q[1]) at the end of main(). For the Bell state, the expected probability distribution is P(00)=0.5, P(01)=0.0, P(10)=0.0, P(11)=0.5.

## isqExpand/isqd/151

- task_id: `isqExpand/isqd/151`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `phase_oracle`, `cz_gate`, `superposition`, `hadamard`, `measurement_probabilities`
- source: `isq_expansion`
- dataset_index: `3274`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    H(q[1]);
    CZ(q[0], q[1]);
    int r0 = M(q[0]);
    int r1 = M(q[1]);
}
```

### Chain-of-thought reasoning

Step 1: Initialize 2-qubit system to |00⟩.
Step 2: Apply H(q[0]) and H(q[1]). This creates H⊗H|00⟩ = (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 = (|00⟩+|01⟩+|10⟩+|11⟩)/2. Each basis state has amplitude 1/2.
Step 3: Apply CZ(q[0], q[1]). The CZ gate applies a conditional phase of -1 when both qubits are |1⟩. So:
  - |00⟩ → |00⟩
  - |01⟩ → |01⟩
  - |10⟩ → |10⟩
  - |11⟩ → -|11⟩
The state becomes (|00⟩ + |01⟩ + |10⟩ - |11⟩)/2.
Step 4: Compute measurement probabilities. For each basis state, P(b) = |amplitude|².
  - P(00) = |1/2|² = 0.25
  - P(01) = |1/2|² = 0.25
  - P(10) = |1/2|² = 0.25
  - P(11) = |-1/2|² = 0.25
All four outcomes have equal probability of 0.25. The phase oracle does not change measurement probabilities because it only affects relative phases, not magnitudes.

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'Starting from |00⟩, applying H⊗H gives the equal superposition (|00⟩+|01⟩+|10⟩+|11⟩)/2. The CZ gate applies a phase flip of -1 only to the |11⟩ component, yielding (|00⟩+|01⟩+|10⟩-|11⟩)/2. Since measurement probabilities depend on the squared magnitude of amplitudes, and all amplitudes have magnitude 1/2, each basis state has probability (1/2)² = 0.25.'}

## isqExpand/isqd/33

- task_id: `isqExpand/isqd/33`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `phase_oracle`, `cz_gate`, `cnot_vs_cz`, `wrong_gate`, `common_error`
- source: `isq_expansion`
- dataset_index: `1615`

### Prompt

The following program intends to implement a phase oracle that marks |11> with a (-1) phase using CZ, but mistakenly uses CNOT instead. CNOT is a Boolean operation (flips the target bit) rather than a phase operation. Fix the bug by replacing CNOT with CZ.

The test prepares q[0]=|1> and q[1]=|+>. A correct CZ phase oracle marks |11> with -1 phase, and the final H on q[1] converts the phase to |1>, giving |11>. With the buggy CNOT, q[1] is flipped instead of phase-marked, producing wrong results.

### Chain-of-thought reasoning

## Bug Analysis
CNOT and CZ are fundamentally different:
- CNOT(c,t): flips target qubit when control is |1> (Boolean operation)
- CZ(c,t): adds -1 phase to |11> (phase operation)

For a phase oracle, we need CZ (phase) not CNOT (bit flip).

Buggy behavior with CNOT:
1. X(q[0])=|1>, H(q[1])=|+>
2. State: |1>(|0>+|1>)/sqrt(2) = (|10>+|11>)/sqrt(2)
3. CNOT(q[0],q[1]): control=|1>, flips q[1]: (|11>+|10>)/sqrt(2) = same state (just reordered). Actually CNOT|10>=|11> and CNOT|11>=|10>.
4. Result: (|11>+|10>)/sqrt(2) = (|10>+|11>)/sqrt(2). Same distribution.
5. H(q[1]): back to |1>|+> -> H gives |1>|0>=|10>. P(|10>)=1.0.

Fixed behavior with CZ:
1. State: (|10>+|11>)/sqrt(2)
2. CZ: (|10>-|11>)/sqrt(2) = |1>(|0>-|1>)/sqrt(2) = |1>|->
3. H(q[1]): |1>|1> = |11>. P(|11>)=1.0. Index=3.

## isqExpand/isqd/98

- task_id: `isqExpand/isqd/98`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `global_phase`, `wrong_parameter`, `api_misuse`
- source: `isq_expansion`
- dataset_index: `1312`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    GPhase(3.14159265358979, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
Buggy: GPhase(pi, q[0]) -- GPhase takes only one double parameter, no qbit.
Fix: GPhase(3.14159265358979); -- remove q[0].
After fix: H creates |+>, GPhase(pi) * -1 (global phase). P(|0>)=P(|1>)=0.5.

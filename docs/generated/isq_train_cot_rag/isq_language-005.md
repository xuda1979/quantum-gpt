# ISQ training COT RAG corpus: isq_language shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/103

- task_id: `isqExpand/isqd/103`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `rotation_gate`, `rz_gate`, `phase_manipulation`, `procedure_with_classical_param`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `140`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[1];

procedure main() {
    double angle = 3.14159265358979;
    X(q[0]);
    Rz(angle, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. double angle = pi
2. X(q[0]): |0> -> |1>
3. Rz(pi, q[0]): Rz(pi)|1> = e^{i*pi/2}|1> = i|1>. Phase only.
4. M: P(|1>) = 1.0
Distribution: [0.0, 1.0]

### Reference answer

{'predicted_probs': {'0': 0.0, '1': 1.0}, 'explanation': 'Step-by-step:\n1. X(q[0]): |0> -> |1>\n2. Rz(pi, q[0]): Rz(pi) = diag(e^{-i*pi/2}, e^{i*pi/2}) = diag(-i, i). |1> -> i|1>. Phase only.\n3. M(q[0]): |i*|1>|^2 = 1. P(|1>) = 1.0.\nDistribution: [0.0, 1.0].'}

## isqExpand/isqd/146

- task_id: `isqExpand/isqd/146`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `boolean_oracle`, `toffoli_gate`, `superposition`, `ancilla_qubit`, `and_function`
- source: `isq_expansion`
- dataset_index: `1156`

### Prompt

Write an isQ program that an isQ Boolean oracle that computes f(x) = x0 AND x1 into an ancilla qubit using a Toffoli gate. Initialize qubits q[0] and q[1] in superposition with Hadamard gates, apply the Toffoli gate with q[0] and q[1] as controls and q[2] as target, then measure all three qubits.

### Chain-of-thought reasoning

We need a 3-qubit circuit: q[0]=x0, q[1]=x1, q[2]=ancilla. Step 1: Apply H to q[0] and q[1] to create uniform superposition over all 2-bit inputs. The joint state becomes (|00>+|01>+|10>+|11>)/2 times |0> on q[2]. Step 2: Apply Toffoli(q[0],q[1],q[2]) which flips q[2] only when both controls are 1. This maps: |000>->|000>, |010>->|010>, |100>->|100>, |110>->|111>. Step 3: Measure all three qubits. The resulting probabilities over the 8 basis states are: |000>=0.25, |001>=0.0, |010>=0.25, |011>=0.0, |100>=0.25, |101>=0.0, |110>=0.0, |111>=0.25. These 8 values sum to 1.0.

## isqExpand/isqd/152

- task_id: `isqExpand/isqd/152`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `mid-circuit_measurement`, `feedforward`, `conditional_gate`, `classical_control`
- source: `isq_expansion`
- dataset_index: `3328`

### Prompt

Help me write isQ code that demonstrates mid-circuit measurement and feedforward control. The program should use 2 qubits q[0] and q[1]. Apply H to q[0] to create superposition, measure q[0] mid-circuit, and if the result is 1 apply X to q[1].

### Chain-of-thought reasoning

The program starts with 2 qubits in |00⟩. After H(q[0]), the state is (|00⟩+|10⟩)/√2. Mid-circuit measurement of q[0] collapses it: 50% chance of outcome 0 (state |00⟩, no action on q[1]) and 50% chance of outcome 1 (state |10⟩, X applied to q[1] giving |11⟩). Final measurement probabilities: |00⟩=0.5, |01⟩=0.0, |10⟩=0.0, |11⟩=0.5.

## isqExpand/isqd/71

- task_id: `isqExpand/isqd/71`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `deriving_gate`, `iswap`, `custom_unitary`, `two_qubit_gate`
- source: `isq_expansion`
- dataset_index: `5098`

### Prompt

Write an isQ program that defines an iSWAP gate using `deriving gate` with the following 4x4 unitary matrix:

```
iSWAP = [[1,0,0,0],[0,0,1i,0],[0,1i,0,0],[0,0,0,1]]
```

The iSWAP gate swaps |01> <-> |10> while multiplying by i.

Prepare the state |10> (X on q[0], q[1] stays |0>), apply iSWAP(q[0], q[1]), then measure both qubits.

After iSWAP on |10>: the state becomes i|01>. Since global phase doesn't affect measurement probabilities, the result is P(|01>) = 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: Define iSWAP via 4x4 matrix and verify on |10>.

1. iSWAP matrix: [[1,0,0,0],[0,0,i,0],[0,i,0,0],[0,0,0,1]]
2. Input: |10> (index 2 in 2-qubit basis: |00>=0, |01>=1, |10>=2, |11>=3)
3. iSWAP|10> = i|01> (column 2 of the matrix: [0, i, 0, 0]^T)
4. Measurement probabilities: |i|^2 = 1 for |01>, 0 elsewhere
5. P(|01>) = 1.0 at index 1

The matrix is unitary: columns are orthonormal.

## isqExpand/isqd/97

- task_id: `isqExpand/isqd/97`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `expert`
- concept_tags: `mid_circuit_measurement`, `classical_control`, `feedforward`, `phase_manipulation`
- source: `isq_expansion`
- dataset_index: `5324`

### Prompt

Create an isQ quantum circuit that implements a simplified gate teleportation protocol.

Gate teleportation applies a gate to a qubit by consuming a resource state, performing a Bell measurement, and applying corrections.

Protocol:
1. Prepare q[0] in state |+> using H(q[0])
2. Prepare q[1] by applying H then T: H(q[1]); T(q[1])
3. Apply CNOT(q[0], q[1]) and H(q[0]) for Bell measurement
4. Measure q[0] into int r
5. If r == 1, apply S(q[1]) as correction
6. Measure q[1] and print result

Use local qubits; validated via compile_only since correction depends on random measurement.

### Chain-of-thought reasoning

## Design
Gate teleportation:
1. q[0] = |+> = H|0>
2. q[1] = T|+> = TH|0>
3. CNOT(q[0], q[1]): entangles
4. H(q[0]): Bell measurement basis
5. Measure q[0], if 1 apply S correction to q[1]
Demonstrates mid-circuit measurement + classical feedback. Local qubits + print -> compile_only.

## isqExpand/isqd/0

- task_id: `isqExpand/isqd/0`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `ctrl_modifier`, `multi_control`, `toffoli`, `isq_syntax`
- source: `isq_expansion_qa`
- dataset_index: `5682`

### Prompt

isQ中ctrl修饰符的语法和语义是什么？如何用ctrl实现多控制门（如Toffoli门）？请解释ctrl @[...]语法，并给出具体示例。

### Chain-of-thought reasoning

## 推理
目标：解释ctrl修饰符的语法和多控制门机制。

关键点：
1. ctrl @[...]语法显式指定控制比特
2. 多控制：在@[]中列出多个控制比特
3. Toffoli门 = ctrl @[c1, c2] X(t)
4. 没有原生CCX关键字
5. 位置形式ctrl<N>也可用
6. ctrl可以与其他修饰符组合

### Reference answer

## isQ中的ctrl修饰符

### 基本语法
ctrl修饰符用于创建控制门。当所有控制比特处于|1>状态时，目标门才会执行。

语法形式：
```isq
ctrl @[control_qubit] Gate(target_qubit);
```

### 单控制门
```isq
ctrl @[q[0]] X(q[1]);  // 等价于CNOT(q[0], q[1])
ctrl @[q[0]] Z(q[1]);  // 等价于CZ(q[0], q[1])
ctrl @[q[0]] H(q[1]);  // 控制Hadamard门
```

### 多控制门
在@[]中列出多个控制比特，所有控制比特都为|1>时才执行：
```isq
ctrl @[q[0], q[1]] X(q[2]);  // Toffoli门（双控制X）
ctrl @[q[0], q[1], q[2]] X(q[3]);  // 三控制X门
```

### Toffoli门详解
Toffoli门（CCNOT）是最常见的多控制门：
- 当q[0]=|1>且q[1]=|1>时，翻转q[2]
- 其他情况保持不变
- isQ中没有CCX关键字，用ctrl @[c1, c2] X(t)实现

### 位置形式语法
isQ还支持位置形式：ctrl<N> Gate(c1, c2, ..., cN, target)
```isq
ctrl<2> S(p, q, r);  // p和q为控制比特，r为目标比特
```

### 完整示例
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]); X(q[1]);  // 设置控制比特为|1>
    ctrl @[q[0], q[1]] X(q[2]);  // Toffoli：翻转q[2]
    M(q[0]); M(q[1]); M(q[2]);
    // 结果：|111> 概率1.0
}
```

### 注意事项
- isQ没有原生SWAP门，需要用3个CNOT分解
- isQ没有CCX关键字，用ctrl @[c1, c2] X(t)或Toffoli(c1, c2, t)
- ctrl可以与inv组合使用：ctrl @[q[0]] inv S(q[1])

## isqExpand/isqd/156

- task_id: `isqExpand/isqd/156`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `mid_circuit_measurement`, `classical_control`, `measurement_order`, `conditional_gate`
- source: `isq_expansion`
- dataset_index: `3858`

### Prompt

The following isQ program is intended to apply H to q[0], measure q[0], and if the result is 1, flip q[1] with X. This should create a Bell-like correlation between q[0] and q[1]. However, the if-block using the measurement result variable is placed BEFORE the measurement call. Fix the code so the measurement happens first and its result is used correctly.

### Chain-of-thought reasoning

In the buggy code, the variable r is initialized to 0, then the if(r==1) block is checked before M(q[0]) is ever called. Since r=0, the X gate on q[1] never fires, and the measurement of q[0] happens afterward. The resulting state is (|00⟩+|10⟩)/√2, giving probabilities [0.5, 0.0, 0.5, 0.0]. In the fixed code, M(q[0]) is called first, collapsing q[0]. When r=1 (50% chance), X(q[1]) flips q[1] to |1⟩; when r=0 (50% chance), q[1] stays |0⟩. The final states are |00⟩ and |11⟩ each with probability 0.5, giving expected_probs [0.5, 0.0, 0.0, 0.5].

## isqExpand/isqd/75

- task_id: `isqExpand/isqd/75`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `for_loop`, `layered_circuit`, `recursive_pattern`, `procedure_with_classical_param`
- source: `isq_expansion`
- dataset_index: `769`

### Prompt

用isQ实现implements a recursive-style layered circuit using a `for` loop. The pattern applies `depth` layers of H gates followed by CNOT to a 2-qubit register.

Specifically, define a procedure `layered_circuit(qbit a, qbit b, int depth)` that runs a for loop from 0 to depth. In each iteration:
1. Apply H(a)
2. Apply CNOT(a, b)

In `main()`, apply X(q[0]) to prepare |10>, then call `layered_circuit(q[0], q[1], 2)` (2 layers), and measure.

Trace through the 2 layers:
- Start: |10>
- Layer 0: H(q[0]): (-|0>+|1>)/sqrt(2) ⊗ |0> -> (-|00>+|10>)/sqrt(2). CNOT(q[0],q[1]): (-|00>+|11>)/sqrt(2)
- Layer 1: H(q[0]): -> (-|0>-|1>)/sqrt(2)⊗|0>/sqrt(2) + (|0>-|1>)/sqrt(2)⊗|1>/sqrt(2). Simplify: -(|00>+|10>)/2 + (|01>-|11>)/2. CNOT(q[0],q[1]): -(|00>+|11>)/2 + (|01>-|10>)/2.

Expected: each of |00>, |01>, |10>, |11> has probability 0.25.

### Chain-of-thought reasoning

## Reasoning
Goal: Layered circuit with for loop — 2 layers of H+CNOT on |10>.

Start: |10>

Layer 0:
  H(q[0]): |10> -> H|1>⊗|0> = (-|0>+|1>)/sqrt(2)⊗|0> = (-|00>+|10>)/sqrt(2)
  CNOT(q[0],q[1]): (-|00>+|11>)/sqrt(2)

Layer 1:
  H(q[0]) on (-|00>+|11>)/sqrt(2):
    -H|0>⊗|0>/sqrt(2) + H|1>⊗|1>/sqrt(2)
    = -(|0>+|1>)|0>/2 + (-|0>+|1>)|1>/2
    = (-|00>-|10>-|01>+|11>)/2
  CNOT(q[0],q[1]):
    |00>->|00>, |10>->|11>, |01>->|01>, |11>->|10>
    = (-|00>-|11>-|01>+|10>)/2

Probabilities: |coeff|^2 = 1/4 each.
P = [0.25, 0.25, 0.25, 0.25]

## isqExpand/isqd/29

- task_id: `isqExpand/isqd/29`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `boolean_to_phase`, `phase_kickback`, `ancilla_minus`, `toffoli`
- source: `isq_expansion`
- dataset_index: `160`

### Prompt

实现以下量子计算任务（使用isQ）：converts a Boolean oracle into a phase oracle using the ancilla-in-|-> trick (also known as phase kickback).

The Boolean oracle computes f(x0,x1) = x0 AND x1 using a Toffoli gate. To convert it into a phase oracle:
1. Prepare the ancilla q[2] in the |-> state by applying X then H
2. Apply the Boolean oracle (Toffoli)
3. The ancilla remains in |-> but the input register gets a (-1)^f(x) phase

To verify the phase kickback, prepare the inputs in superposition:
- H(q[0]), H(q[1]) to create equal superposition over all 2-bit inputs
- Prepare ancilla: X(q[2]), H(q[2]) -> |->
- Apply Toffoli(q[0], q[1], q[2]): this is the Boolean oracle
- Uncompute ancilla: H(q[2]), X(q[2])  (return ancilla to |0>)
- Apply H(q[0]), H(q[1]) to decode phases

After phase kickback, only |11> gets (-1) phase. H⊗H on (|00>+|01>+|10>-|11>)/2:
Following the same analysis as the Deutsch-Jozsa pattern, this produces |00> with probability 1/4, |01> with 1/4, |10> with 1/4, |11> with 1/4.

Actually, a cleaner test: prepare |11> in inputs + ancilla in |->. After Toffoli, ancilla stays |-> but |11> gets -1 phase. Use H on q[1] to detect:

- State: |1>(|0>+|1>)/sqrt(2)|-> after H(q[1])
  = (|10>+|11>)/sqrt(2) tensored with |->
- Toffoli: f(1,0)=0, f(1,1)=1. Phase kickback on |11>:
  (|10>-|11>)/sqrt(2) |-> = |1>(|0>-|1>)/sqrt(2) |->
- H(q[1]): |1>|1>|-> = |11>|->
- Uncompute ancilla (H, X): |11>|0>

Measure q[0], q[1], q[2]: expect |110> with probability 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: Convert Boolean oracle (Toffoli for AND) to phase oracle via ancilla in |-> trick.

1. X(q[0]): q[0]=|1>
2. H(q[1]): q[1]=|+>=(|0>+|1>)/sqrt(2)
3. X(q[2]); H(q[2]): q[2]=|->=(|0>-|1>)/sqrt(2)
4. State: |1> (|0>+|1>)/sqrt(2) |-> = (|10>+|11>)/sqrt(2) ⊗ |->
5. Toffoli(q[0],q[1],q[2]):
   - |10>|->: f(1,0)=0, no flip on ancilla -> |10>|->
   - |11>|->: f(1,1)=1, flip ancilla |-> -> -|-> (phase kickback)
   Result: (|10>-|11>)/sqrt(2) ⊗ |->
6. = |1>(|0>-|1>)/sqrt(2) ⊗ |-> = |1>|-> ⊗ |->
7. H(q[2]): |-> -> |1>. Then X(q[2]): |1> -> |0>. So ancilla returns to |0>.
8. H(q[1]): |-> -> |1>
9. Final: |1>|1>|0> = |110>

Index = 1*4+1*2+0 = 6. P(|110>)=1.0.

## isqExpand/isqd/137

- task_id: `isqExpand/isqd/137`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `procedure_definition_order`, `bell_state`, `compilation_error`
- source: `isq_expansion`
- dataset_index: `36`

### Prompt

The following isQ program is intended to create a Bell state (|00⟩+|11⟩)/√2 by calling a helper procedure 'bellState()' from main. However, it fails because the helper procedure is called before it is defined. In isQ, procedures must be defined before they are used. Fix the ordering so the program compiles and runs correctly.

### Chain-of-thought reasoning

The buggy code defines main() first, which calls bellState(), but bellState() is only defined later in the file. isQ requires that procedures be defined before they are referenced. The fix is to reorder the code so that bellState() is defined before main(). The circuit itself applies H(q[0]) followed by CNOT(q[0], q[1]), producing the Bell state (|00⟩+|11⟩)/√2. The expected measurement probabilities are 0.5 for |00⟩, 0 for |01⟩, 0 for |10⟩, and 0.5 for |11⟩.

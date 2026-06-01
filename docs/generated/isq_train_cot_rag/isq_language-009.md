# ISQ training COT RAG corpus: isq_language shard 9

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/144

- task_id: `isqExpand/isqd/144`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `phase_oracle`, `multi_controlled_gates`, `CZ`, `X_gate`, `phase_kickback`, `grover_primitive`
- source: `isq_expansion`
- dataset_index: `2962`

### Prompt

Write an isQ program that an isQ phase oracle that marks state |10⟩ with a -1 phase using X gates and a multi-controlled Z gate. The program should apply Hadamard gates before and after the oracle on q[0] so that the phase kickback is visible in the measurement probabilities. Use 2 qubits and the --probs check mode.

### Chain-of-thought reasoning

The goal is to mark |10⟩ (q[0]=1, q[1]=0) with a -1 phase using X gates and CZ. The CZ gate applies a -1 phase only when both control qubits are |1⟩ (i.e., |11⟩). To mark |10⟩, we sandwich CZ with X on q[1]: X(q[1]) converts |10⟩→|11⟩, CZ flips the phase of |11⟩, then X(q[1]) uncomputes back to |10⟩. To verify via probabilities, apply H(q[0]) first to create (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2. After the oracle: (|00⟩-|10⟩)/√2. Then H(q[0]) converts the phase difference: H(|0⟩-|1⟩)/√2 = |1⟩. Final state is |10⟩, giving probability 1.0 at index 2 (binary 10).

## isqExpand/isqd/90

- task_id: `isqExpand/isqd/90`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `entanglement`, `superposition`, `modular_circuit`
- source: `isq_expansion`
- dataset_index: `198`

### Prompt

Create an isQ quantum circuit that composes three procedures to implement a GHZ state preparation for 3 qubits.

Define:
1. `procedure create_superposition(qbit a)` that applies H to qubit a
2. `procedure entangle_pair(qbit a, qbit b)` that applies CNOT(a, b)
3. `procedure make_ghz3(qbit a, qbit b, qbit c)` that calls `create_superposition(a)`, then `entangle_pair(a, b)`, then `entangle_pair(a, c)`

In `procedure main()`, call `make_ghz3` on global qubits q[0..2] and measure all three.

Expected output: GHZ state (|000> + |111>)/sqrt(2). P(|000>) = 0.5, P(|111>) = 0.5.

### Chain-of-thought reasoning

## Circuit Analysis
1. create_superposition(q[0]): H(q[0]) -> (|0>+|1>)/sqrt(2)
2. entangle_pair(q[0], q[1]): CNOT(q[0],q[1]) -> (|00>+|11>)/sqrt(2)
3. entangle_pair(q[0], q[2]): CNOT(q[0],q[2]) -> (|000>+|111>)/sqrt(2)
Standard GHZ preparation decomposed into reusable procedures.
P(|000>)=0.5 at index 0, P(|111>)=0.5 at index 7.

## isqExpand/isqd/9

- task_id: `isqExpand/isqd/9`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `deriving_gate`, `ctrl_modifier`, `isq_syntax_procedures`
- source: `isq_expansion`
- dataset_index: `2051`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```isq
import std;
qbit q[2];

procedure double_x(qbit a) {
    X(a);
    X(a);
}

procedure main() {
    X(q[0]);
    ctrl double_x(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
In isQ, user-defined procedures cannot be used with modifiers (ctrl, inv, nctrl) unless they are marked with "deriving gate". This keyword tells the compiler to treat the procedure as a quantum gate.

Fix: Add "deriving gate" after the closing brace of double_x.

After fix: ctrl double_x(q[0], q[1]) with q[0]=|1> executes double_x on q[1]. Since double_x applies X twice (X*X=I), q[1] remains |0>. Final state: q[0]=1, q[1]=0 = |10>. Index = 1*2+0 = 2.

## isqExpand/isqd/80

- task_id: `isqExpand/isqd/80`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nctrl_modifier`, `ctrl_modifier`, `logic_error`
- source: `isq_expansion`
- dataset_index: `195`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    nctrl X(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The buggy code uses `nctrl @[q[0]] X(q[1])` but the intent is to flip q[1] when q[0]=|1>. nctrl fires when control is |0>, so with q[0]=|1>, nctrl does NOT fire, leaving q[1] unchanged.

The buggy behavior: X(q[0]) makes q[0]=|1>. nctrl@[q[0]] X(q[1]) does NOT fire (q[0] is |1>, not |0>). Result: |10>, not |11>.

Fix: Change nctrl to ctrl.

## isqExpand/isqd/104

- task_id: `isqExpand/isqd/104`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `phase_manipulation`, `entanglement`, `s_gate`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `3245`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[2];

procedure apply_phase(qbit a) {
    S(a);
} deriving gate

procedure entangle_and_phase(qbit a, qbit b) {
    H(a);
    CNOT(a, b);
    apply_phase(b);
}

procedure main() {
    entangle_and_phase(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. H(q[0]): (|0>+|1>)/sqrt(2) x |0>
2. CNOT: Bell (|00>+|11>)/sqrt(2)
3. S(q[1]): |00> unchanged, |11>->i|11>
   State: (|00>+i|11>)/sqrt(2)
4. P(|00>)=0.5, P(|11>)=0.5
Distribution: [0.5, 0.0, 0.0, 0.5]

### Reference answer

{'predicted_probs': {'00': 0.5, '01': 0.0, '10': 0.0, '11': 0.5}, 'explanation': 'Step-by-step:\n1. H(q[0]): (|0>+|1>)/sqrt(2)\n2. CNOT(q[0], q[1]): (|00>+|11>)/sqrt(2) -- Bell state\n3. S(q[1]): S=diag(1,i). |00> unchanged. |11> -> i|11>.\n   State: (|00>+i|11>)/sqrt(2)\n4. P(|00>)=0.5. P(|11>)=|i|^2/2=0.5.\nDistribution: [0.5, 0.0, 0.0, 0.5].'}

## isqExpand/isqd/133

- task_id: `isqExpand/isqd/133`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `deriving_gate`, `pauli_x`, `output_prediction`, `single_qubit`
- source: `isq_expansion`
- dataset_index: `2192`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit q[1];

procedure main() {
    X(q[0]);
}
```

### Chain-of-thought reasoning

The program defines a custom gate myX = [[0,1],[1,0]]. This matrix is the standard Pauli X gate. The initial state of q[0] is |0⟩ = [1,0]^T. Applying the X gate: [[0,1],[1,0]] * [1,0]^T = [0,1]^T = |1⟩. Therefore, measuring q[0] yields outcome 1 with certainty (probability 1.0) and outcome 0 with probability 0.0.

### Reference answer

{'predicted_probs': {'0': 0.0, '1': 1.0}, 'explanation': 'The deriving gate myX = [[0,1],[1,0]] is exactly the Pauli X (NOT) gate. Applying X to |0⟩ flips it to |1⟩, so the measurement outcome is always 1 with probability 1.0.'}

## isqExpand/isqd/66

- task_id: `isqExpand/isqd/66`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `deriving_gate`, `custom_unitary`, `matrix_dimension`, `isq_syntax`
- source: `qa_pipeline`
- dataset_index: `44`

### Prompt

isQ中deriving gate语法如何用于定义自定义酉矩阵门？请分别说明：
1. 如何用2×2矩阵定义自定义单量子比特门
2. 如何用4×4矩阵定义自定义双量子比特门（如iSWAP门）
3. 矩阵维度与量子比特数的关系
请给出完整的代码示例。

### Chain-of-thought reasoning

## 推理
目标：解释deriving gate语法，覆盖1-qubit（2×2）和2-qubit（4×4）矩阵。

关键点：
1. 2×2矩阵 -> 1量子比特门
2. 4×4矩阵 -> 2量子比特门
3. 矩阵维度 = 2^N（N=量子比特数）
4. 必须是酉矩阵
5. 支持复数元素（1i）
6. 可与ctrl、inv组合

### Reference answer

## isQ中的deriving gate语法

### 基本语法
`deriving gate` 允许通过酉矩阵直接定义量子门：
```isq
deriving gate myGate = [[a, b], [c, d]];
```
矩阵必须是酉矩阵（U†U = I）。

### 1. 自定义单量子比特门（2×2矩阵）
例如，定义一个sqrt(X)门：
```isq
deriving gate sqrtX = [[0.5+0.5i, 0.5-0.5i], [0.5-0.5i, 0.5+0.5i]];
```
使用：`sqrtX(q[0]);`

### 2. 自定义双量子比特门（4×4矩阵）
例如，iSWAP门交换两个量子比特并附加i相位：
```isq
deriving gate iswap = [
  [1, 0, 0, 0],
  [0, 0, 1i, 0],
  [0, 1i, 0, 0],
  [0, 0, 0, 1]
];
```
使用：`iswap(q[0], q[1]);`

### 3. 维度关系
- 1量子比特门：2×2矩阵
- 2量子比特门：4×4矩阵
- N量子比特门：2^N × 2^N 矩阵
如果矩阵维度不是2的幂次方，编译器会报错。

### 完整示例
```isq
import std;
qbit q[2];

// 自定义X门（等价于Pauli-X）
deriving gate myX = [[0, 1], [1, 0]];

procedure main() {
    myX(q[0]);  // q[0]: |0> -> |1>
    M(q[0]); M(q[1]);
}
```
结果：P(|10>) = 1.0

### 注意事项
- 矩阵元素支持复数：使用`1i`表示虚数单位
- 矩阵必须严格酉（编译器会检查）
- deriving gate定义的门可以与ctrl、inv修饰符组合使用

## isqExpand/isqd/186

- task_id: `isqExpand/isqd/186`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `ancilla_management`, `uncomputation`, `entanglement`, `toffoli`, `quantum_hygiene`
- source: `isq_expansion`
- dataset_index: `2061`

### Prompt

The following isQ program uses an ancilla qubit q[2] to compute the AND of two control qubits in superposition, then applies a CNOT to a target qubit q[3]. However, the ancilla qubit is never uncomputed after use, so it remains entangled with the data register. Fix the code by adding the missing uncomputation step so that the ancilla is returned to |0⟩ and disentangled from the data qubits.

### Chain-of-thought reasoning

Step 1: After H(q[0]) and H(q[1]), the state is (1/2)(|0000> + |0100> + |1000> + |1100>). Step 2: Toffoli(q[0],q[1],q[2]) computes AND into ancilla: (1/2)(|0000> + |0100> + |1000> + |1110>). Step 3: CNOT(q[2],q[3]) flips target when ancilla is |1>: (1/2)(|0000> + |0100> + |1000> + |1111>). Step 4: Without uncomputation, ancilla q[2] remains entangled — the state has |1111> (index 15) with 0.25 probability. Step 5: Adding Toffoli(q[0],q[1],q[2]) uncomputes the ancilla: when q[0]=1,q[1]=1,q[2]=1, the Toffoli flips q[2] back to 0, giving state (1/2)(|0000> + |0100> + |1000> + |1101>). Step 6: The expected probabilities for 4 qubits: indices 0,4,8,13 each have 0.25, rest are 0. The buggy version incorrectly has probability at index 15 instead of 13 because the ancilla was not uncomputed.

## isqExpand/isqd/99

- task_id: `isqExpand/isqd/99`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `ctrl_modifier`, `logic_error`, `ctrl_at_syntax`
- source: `isq_expansion`
- dataset_index: `387`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    ctrl X(q[0], q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
Buggy: ctrl @[q[0]] X(q[0]) -- q[0] is both control and target. Invalid.
Fix: ctrl @[q[0]] X(q[1]).
Result: (|00>+|11>)/sqrt(2). P(|00>)=0.5, P(|11>)=0.5.

## isqExpand/isqd/167

- task_id: `isqExpand/isqd/167`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `import_std`, `compilation_error`, `hadamard_gate`, `superposition`
- source: `isq_expansion`
- dataset_index: `2667`

### Prompt

The following isQ code is missing the required `import std;` statement at the top, which causes a compilation error. Fix the code by adding the missing import so the program compiles and runs correctly. The program should create a single-qubit superposition using a Hadamard gate.

### Chain-of-thought reasoning

The buggy code is missing the `import std;` statement, which is always required as the first line in any isQ program. Without it, the compiler cannot resolve the standard gate definitions like H, X, CNOT, etc., and will produce a compilation error. The fix is straightforward: add `import std;` as the very first line. After fixing, the program declares a single qubit q[0], applies a Hadamard gate to put it into an equal superposition, and when measured should yield probabilities [0.5, 0.5] for outcomes 0 and 1 respectively.

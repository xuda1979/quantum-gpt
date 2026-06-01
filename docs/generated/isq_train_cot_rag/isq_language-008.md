# ISQ training COT RAG corpus: isq_language shard 8

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/44

- task_id: `isqExpand/isqd/44`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `mid_circuit_measurement`, `entanglement`, `isq_syntax_procedures`
- source: `isq_expansion`
- dataset_index: `2435`

### Prompt

I need an isQ program to demonstrates mid-circuit measurement with conditional correction (a simplified teleportation pattern).

Setup:
1. Prepare q[0] in state |1> (apply X).
2. Create a Bell pair between q[1] and q[2]: H(q[1]), CNOT(q[1], q[2]).
3. Apply CNOT(q[0], q[1]) and H(q[0]).
4. Measure q[0] and q[1] into classical variables.
5. Apply conditional corrections on q[2]:
   - If q[1] measured 1, apply X(q[2]).
   - If q[0] measured 1, apply Z(q[2]).
6. Measure q[2] and print the result.

After correction, q[2] should deterministically be in state |1> (the original state of q[0] has been teleported).

Use stdout_match validation since this uses mid-circuit measurement.

### Chain-of-thought reasoning

## Reasoning
Goal: Simplified teleportation with mid-circuit measurement.

1. q[0] = |1> (state to teleport).
2. Bell pair: (|00>+|11>)/sqrt(2) on q[1],q[2].
3. CNOT(q[0],q[1]) + H(q[0]): Bell measurement on q[0],q[1].
4. Four equally likely outcomes for (m0,m1):
   - (0,0): q[2] = |1> (no correction needed)
   - (0,1): q[2] = |0> -> X -> |1>
   - (1,0): q[2] = -|1> -> Z -> |1>
   - (1,1): q[2] = -|0> -> X -> -|1> -> Z -> |1>
5. All paths yield q[2] = |1> (up to global phase).
6. print result outputs 1.

## isqExpand/isqd/2

- task_id: `isqExpand/isqd/2`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `ctrl_modifier`, `toffoli`, `multi_control`
- source: `isq_expansion`
- dataset_index: `3660`

### Prompt

帮我写一个isQ程序：implements a Toffoli gate (doubly-controlled NOT) using the ctrl modifier. Prepare the input state |110> (q[0]=1, q[1]=1, q[2]=0), apply the Toffoli gate using ctrl @[q[0], q[1]] X(q[2]), and measure all three qubits.

The Toffoli gate flips the target qubit only when both control qubits are |1>. Since both controls are |1>, the target q[2] should flip from |0> to |1>, producing the output state |111>.

Note: isQ has no CCX keyword. Use ctrl @[c1, c2] X(target) for a Toffoli gate.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Toffoli gate using ctrl @[q[0], q[1]] X(q[2]).

1. X(q[0]), X(q[1]): Prepare |110> (q[0]=1, q[1]=1, q[2]=0)
2. ctrl @[q[0], q[1]] X(q[2]): Both controls are |1>, so X is applied to q[2]
3. Final state: |111> (q[0]=1, q[1]=1, q[2]=1)
4. Index = q[0]*4 + q[1]*2 + q[2] = 4+2+1 = 7

Expected: P(|111>) = 1.0 at index 7

## isqExpand/isqd/50

- task_id: `isqExpand/isqd/50`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_procedures`, `entanglement`, `superposition`
- source: `isq_expansion`
- dataset_index: `1291`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit grid[4];

procedure entangle_row(qbit a, qbit b) {
    H(a);
    CNOT(a, b);
}

procedure main() {
    entangle_row(grid[0], grid[1]);
    X(grid[2]);
    X(grid[3]);
    M(grid[0]); M(grid[1]);
    M(grid[2]); M(grid[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. entangle_row(grid[0]): Bell pair on row 0.
   grid[0] = (|00>+|11>)/sqrt(2)
2. X(grid[1][0]), X(grid[1][1]): grid[1] = |11>
3. Total state (grid[0][0], grid[0][1], grid[1][0], grid[1][1]):
   Row 0 x Row 1 = (|00>+|11>)/sqrt(2) x |11>
   = (|0011> + |1111>)/sqrt(2)
4. P(|0011>) = 0.5, index = 0+0+2+1 = 3
   P(|1111>) = 0.5, index = 8+4+2+1 = 15
All other indices: 0.

### Reference answer

{'predicted_probs': {'0011': 0.5, '0111': 0.0, '1011': 0.0, '1111': 0.5}, 'explanation': 'Step-by-step:\n1. entangle_row(grid[0]): H(grid[0][0]), CNOT(grid[0][0], grid[0][1])\n   Row 0: (|00>+|11>)/sqrt(2)\n2. X(grid[1][0]), X(grid[1][1]): Row 1 = |11>\n3. Combined state (row-major: grid[0][0], grid[0][1], grid[1][0], grid[1][1]):\n   (|0011> + |1111>)/sqrt(2)\n4. P(|0011>) = 0.5 at index 3 (0*8+0*4+1*2+1 = 3)\n   P(|1111>) = 0.5 at index 15 (1*8+1*4+1*2+1 = 15)\nDistribution: 16 entries, all zero except index 3 = 0.5 and index 15 = 0.5.'}

## isqExpand/isqd/81

- task_id: `isqExpand/isqd/81`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nested_procedures`, `definition_order`, `compile_error`
- source: `isq_expansion`
- dataset_index: `1086`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;
qbit q[2];

procedure make_bell(qbit a, qbit b) {
    make_plus(a);
    CNOT(a, b);
}

procedure make_plus(qbit a) {
    H(a);
}

procedure main() {
    make_bell(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The buggy code defines make_bell before make_plus, but make_bell calls make_plus. In isQ, procedures must be defined before they are called.

The compiler will report an undefined reference error for make_plus inside make_bell.

Fix: Move make_plus definition above make_bell. The corrected program creates a Bell state: H(q[0]) -> CNOT(q[0],q[1]) -> (|00>+|11>)/sqrt(2). P(|00>)=0.5 at index 0, P(|11>)=0.5 at index 3.

## isqExpand/isqd/15

- task_id: `isqExpand/isqd/15`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `procedure`, `bell_state`, `code_reuse`, `isq_syntax_procedures`
- source: `isq_expansion`
- dataset_index: `5166`

### Prompt

Implement the following in isQ: defines a reusable procedure `encode_bell(qbit a, qbit b)` which creates a Bell state |Phi+> on two qubits (H on a, then CNOT(a,b)). Use this procedure twice on two separate pairs of qubits to create two independent Bell states.

Requirements:
- Declare global qbit q[4].
- Define `procedure encode_bell(qbit a, qbit b)` that applies H(a) then CNOT(a,b).
- In main(), call encode_bell(q[0], q[1]) and encode_bell(q[2], q[3]).
- Measure all 4 qubits.

Expected: the two pairs are independently entangled. The 4-qubit state is (|00>+|11>)/sqrt(2) tensor (|00>+|11>)/sqrt(2). The non-zero outcomes are |0000>, |0011>, |1100>, |1111> each with probability 0.25.

### Chain-of-thought reasoning

## Reasoning
Goal: Define a reusable Bell-state procedure and apply it twice.

1. encode_bell(a,b): H(a), CNOT(a,b) -> (|00>+|11>)/sqrt(2)
2. Two independent Bell pairs: q[0,1] and q[2,3]
3. Combined state: (|00>+|11>)/sqrt(2) x (|00>+|11>)/sqrt(2)
4. Expand: (|0000>+|0011>+|1100>+|1111>)/2
5. Non-zero indices:
   |0000> = index 0, P = 0.25
   |0011> = index 3, P = 0.25
   |1100> = index 12, P = 0.25
   |1111> = index 15, P = 0.25

## isqExpand/isqd/161

- task_id: `isqExpand/isqd/161`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `hadamard`, `for_loop`, `measurement`, `superposition`, `equal_distribution`
- source: `isq_expansion`
- dataset_index: `4322`

### Prompt

Implement the following in isQ: declares 2 qubits, applies a Hadamard gate to each qubit using a for loop, then measures all qubits.

### Chain-of-thought reasoning

Step 1: We need 2 qubits declared at global scope: `qbit q[2];`. Step 2: Apply H to each qubit using a for loop `for i in 0:2 { H(q[i]); }`. The range 0:2 means i takes values 0 and 1. Step 3: After applying H to both qubits, the state is (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2, so each of the 4 basis states has equal probability 0.25. Step 4: Measure both qubits with `int r0 = M(q[0]); int r1 = M(q[1]);`. The expected probabilities are [0.25, 0.25, 0.25, 0.25] for states 00, 01, 10, 11 respectively.

## isqExpand/isqd/27

- task_id: `isqExpand/isqd/27`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `boolean_oracle`, `toffoli`, `ancilla`, `and_function`
- source: `isq_expansion`
- dataset_index: `5438`

### Prompt

Help me write isQ code that implements a Boolean oracle computing f(x0, x1) = x0 AND x1 using a Toffoli gate.

The Boolean oracle stores the result of f(x) in an ancilla qubit: |x0, x1, 0> -> |x0, x1, f(x0,x1)>.

Requirements:
- Use 3 qubits: q[0] and q[1] are input qubits, q[2] is the ancilla (output).
- Define a procedure  that applies Toffoli(q[0], q[1], q[2]) to compute q[2] = q[0] AND q[1].
- In main(), prepare input |11> (both inputs are 1), call the oracle, and measure all qubits.
- Since f(1,1) = 1 AND 1 = 1, the ancilla should flip to |1>, producing output |111>.

### Chain-of-thought reasoning

## Reasoning
Goal: Boolean oracle for f(x0,x1)=x0 AND x1 using Toffoli.

1. X(q[0]), X(q[1]): prepare input |11>, ancilla q[2]=|0>. State: |110>
2. Toffoli(q[0], q[1], q[2]): both controls are |1>, flip q[2]: |110> -> |111>
3. f(1,1)=1, ancilla now stores the result

Index = 1*4+1*2+1 = 7. P(|111>)=1.0 at index 7.

## isqExpand/isqd/10

- task_id: `isqExpand/isqd/10`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `ctrl_modifier`, `inv_modifier`, `s_gate`, `phase_analysis`
- source: `isq_expansion`
- dataset_index: `5384`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    H(q[1]);
    inv ctrl S(q[0], q[1]);
    H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[0]): |00> -> q[0]=1, q[1]=0
2. H(q[1]): q[1] -> (|0>+|1>)/sqrt(2)
3. ctrl @[q[0]] inv S(q[1]): q[0]=|1>, so inv S acts on q[1]: (|0>-i|1>)/sqrt(2)
4. H(q[1]): H applied to (|0>-i|1>)/sqrt(2)
   = ((1-i)/2)|0> + ((1+i)/2)|1>
   P(0) = |1-i|^2/4 = 2/4 = 0.5
   P(1) = |1+i|^2/4 = 2/4 = 0.5

q[0] always |1>. q[1] is 50/50.
P(q[0]=1,q[1]=0) = 0.5 -> index = 1*2+0 = 2
P(q[0]=1,q[1]=1) = 0.5 -> index = 1*2+1 = 3
Distribution: [0.0, 0.0, 0.5, 0.5]

### Reference answer

{'predicted_probs': {'00': 0.0, '01': 0.0, '10': 0.5, '11': 0.5}, 'explanation': 'Step-by-step:\n1. X(q[0]): q[0] -> |1>\n2. H(q[1]): q[1] -> |+> = (|0>+|1>)/sqrt(2)\n3. ctrl @[q[0]] inv S(q[1]): q[0]=|1> so inv S is applied to q[1]. inv S adds phase -pi/2 to |1>: (|0>+e^{-i*pi/2}|1>)/sqrt(2) = (|0>-i|1>)/sqrt(2)\n4. H(q[1]): H * (|0>-i|1>)/sqrt(2) = ((1-i)|0>+(1+i)|1>)/2.\n   P(q[1]=0) = |1-i|^2/4 = 2/4 = 0.5\n   P(q[1]=1) = |1+i|^2/4 = 2/4 = 0.5\n\nq[0] is always |1>, q[1] is 50/50.\nIn index notation (q[0]*2+q[1]): |10>=index 2 has P=0.5, |11>=index 3 has P=0.5.\nDistribution: [0.0, 0.0, 0.5, 0.5].'}

## isqExpand/isqd/12

- task_id: `isqExpand/isqd/12`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `for_loop`, `procedure`, `isq_syntax`, `batch_gate_application`
- source: `isq_expansion_qa`
- dataset_index: `3251`

### Prompt

isQ中for循环和procedure的语法是什么？如何用for循环对所有量子比特批量应用门操作，以及如何定义可复用的量子子程序（procedure）？请结合示例说明。

### Chain-of-thought reasoning

## 推理
目标：解释for循环和procedure的基本语法。

关键点：
1. for i in 0:N 是半开区间语法
2. 嵌套for用于分层电路
3. procedure定义可复用子程序
4. deriving gate允许procedure与修饰符组合
5. 常见陷阱：越界、参数类型、全局qbit要求

### Reference answer

## isQ中的for循环和procedure

### for循环语法
isQ的for循环遍历半开区间 `0:N`（即 0, 1, ..., N-1）：
```isq
for i in 0:N {
    H(q[i]);
}
```
等价于对 q[0], q[1], ..., q[N-1] 依次施加 H 门。

### 嵌套for循环
可以嵌套for循环来构建分层电路：
```isq
for layer in 0:3 {
    for i in 0:4 {
        H(q[i]);
    }
}
```

### procedure语法
procedure定义可复用的量子子程序：
```isq
procedure apply_h_layer(qbit reg[4]) {
    for i in 0:4 { H(reg[i]); }
}
```
参数类型为 `qbit` 或 `qbit name[N]`（数组）。

### procedure + deriving gate
如果需要对procedure使用ctrl或inv修饰符，必须加 `deriving gate`：
```isq
procedure my_oracle(qbit a, qbit b) {
    CNOT(a, b);
} deriving gate
```

### 注意事项
1. for循环范围 `0:N` 是半开区间，不包含N
2. 如果写成 `0:N+1` 会遍历 0..N（包含N），容易越界
3. procedure参数中qbit数组大小必须在编译时确定
4. 在--probs模式下，被测量的qbit必须在全局声明

### 完整示例
```isq
import std;
qbit q[4];

procedure hadamard_all(qbit reg[4]) {
    for i in 0:4 { H(reg[i]); }
}

procedure main() {
    hadamard_all(q);
    for i in 0:4 { M(q[i]); }
}
```
结果：4个qubit均处于均匀叠加态，每个基态概率为1/16。

## isqExpand/isqd/41

- task_id: `isqExpand/isqd/41`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `isq_syntax_arrays`, `phase_manipulation`, `superposition`
- source: `isq_expansion`
- dataset_index: `3430`

### Prompt

I need an isQ program to implements a 2-qubit Quantum Fourier Transform (QFT) as a reusable procedure `qft2(qbit reg[2])`.

The 2-qubit QFT circuit is:
1. H(reg[0])
2. ctrl @[reg[1]] S(reg[0])   (controlled-S, adds pi/2 phase)
3. H(reg[1])

In `main()`, prepare the input state |10> (X on q[0]) to represent the computational basis state with value 2 (in big-endian). Call qft2(q) and measure both qubits.

For QFT on |10> (value=2 out of 4): each output basis state should have equal probability 0.25 (the QFT of a computational basis state is a uniform superposition with different phases, all having equal amplitude 1/2).

### Chain-of-thought reasoning

## Reasoning
Goal: Implement 2-qubit QFT as procedure, apply to |10>.

QFT on N=2 qubits with input |x> = |10> (value 2):
QFT|x> = (1/sqrt(N)) * sum_k exp(2*pi*i*x*k/N) |k>
= (1/2) * sum_{k=0}^{3} exp(2*pi*i*2*k/4) |k>
= (1/2) * sum_k exp(i*pi*k) |k>
= (1/2)(|00> - |01> + |10> - |11>)

All amplitudes have magnitude 1/2, so all probabilities = 0.25.
Expected: [0.25, 0.25, 0.25, 0.25].

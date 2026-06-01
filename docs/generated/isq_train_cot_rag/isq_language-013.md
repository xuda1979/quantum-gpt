# ISQ training COT RAG corpus: isq_language shard 13

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/7

- task_id: `isqExpand/isqd/7`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `ctrl_modifier`, `syntax_error`, `toffoli`
- source: `isq_expansion`
- dataset_index: `77`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    ctrl [q[0], q[1]] X(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The buggy code writes ctrl [q[0], q[1]] X(q[2]) but the correct isQ syntax requires the @ symbol before the brackets: ctrl @[q[0], q[1]] X(q[2]).

The @ symbol is mandatory in the explicit control-qubit form of the ctrl modifier. Without it, the compiler cannot parse the control qubit list.

Fix: Change ctrl [q[0], q[1]] to ctrl @[q[0], q[1]].

## isqExpand/isqd/86

- task_id: `isqExpand/isqd/86`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `procedure_with_classical_param`, `rotation_gate`, `for_loop`, `mid_circuit_measurement`
- source: `isq_expansion_qa`
- dataset_index: `4843`

### Prompt

isQ中如何使用double和int类型的经典变量来参数化量子电路？请说明：
1. double变量如何与旋转门（Rx, Ry, Rz）结合使用
2. int变量如何用于控制for循环中的门操作次数
3. int变量如何存储测量结果并用于条件操作
请给出完整的代码示例。

### Chain-of-thought reasoning

## 推理
目标：解释isQ中double和int经典变量的使用方式。

关键点：
1. double -> 旋转门参数（Rx, Ry, Rz的角度）
2. int -> for循环控制、测量结果存储
3. M()返回int（0或1）
4. if条件使用int变量进行经典控制
5. for使用半开区间 0:n 表示 [0, n)

### Reference answer

## isQ中的经典变量与参数化电路

### 1. double变量与旋转门
double类型用于存储连续角度参数，与旋转门结合实现参数化电路：
```isq
import std;
qbit q[1];

procedure main() {
    double theta = 3.14159265358979;  // pi
    Rx(theta, q[0]);  // 绕X轴旋转pi
    M(q[0]);
}
```
执行后q[0]变为|1>（Rx(pi)|0> = -i|1>，测量概率P(|1>)=1.0）。

### 2. int变量控制循环
int变量可以控制for循环中的迭代次数：
```isq
import std;
qbit q[3];

procedure main() {
    int n = 3;
    for i in 0:n {
        H(q[i]);  // 对前n个qubit施加H门
    }
    M(q[0]); M(q[1]); M(q[2]);
}
```
每个qubit都处于叠加态，3个qubit的8种结果等概率。

### 3. int存储测量结果
int变量存储M()的返回值，用于经典条件控制：
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    int r = M(q[0]);
    if (r == 1) {
        X(q[1]);  // 条件翻转
    }
    M(q[1]);
}
```

### 关键规则
- double用于连续参数（角度、相位）
- int用于离散值（循环计数、测量结果、条件判断）
- M()返回int类型（0或1）
- for循环使用半开区间 `0:n` 表示 [0, n)

## isqExpand/isqd/154

- task_id: `isqExpand/isqd/154`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `measurement_loop`, `classical_counter`, `for_loop`, `classical_control_flow`, `variable_assignment`
- source: `isq_expansion`
- dataset_index: `3830`

### Prompt

请用isQ语言编写一个量子电路：demonstrates a classical counter in a measurement loop. Initialize q[0] to |1> using an X gate, then measure q[0] three times in a for loop. Use an integer variable 'count' to track how many times the measurement result is |1>. Use a global qbit array q[2].

### Chain-of-thought reasoning

The program needs to demonstrate classical control flow with a counter in isQ. Step 1: We declare a global qbit array q[2]. Step 2: In main(), we initialize a classical int variable 'count' to 0. Step 3: We apply X(q[0]) to set q[0] to |1>. Step 4: We loop three times using 'for i in 0:3', each time measuring q[0] with int r = M(q[0]). Step 5: If the result r equals 1, we increment count. Step 6: Since q[0] is prepared in |1>, each measurement collapses to |1>, and after measurement the qubit stays in |1>. So count will be 3 after the loop. Step 7: For the probability check, the final state of q[0] is |1> with certainty, giving expected_probs = [0.0, 1.0] for a single measured qubit.

## isqExpand/isqd/31

- task_id: `isqExpand/isqd/31`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `uncomputation`, `ancilla`, `boolean_oracle`, `phase_kickback`, `common_error`
- source: `isq_expansion`
- dataset_index: `25`

### Prompt

The following program intends to use a Boolean oracle with ancilla-in-|-> to implement a phase oracle for f(x0,x1) = x0 AND x1, then verify by checking the output on input |11>. However, the programmer forgot to uncompute (restore) the ancilla after the Toffoli gate. This leaves the ancilla entangled with the input register, corrupting the result.

The ancilla should be returned to |0> after the oracle application by undoing X and H. Fix the bug by adding the uncomputation of the ancilla.

After fix, the ancilla q[2] should be returned to |0> by applying H then X after the Toffoli. The expected output is |110> (input bits unchanged, ancilla back to |0>).

### Chain-of-thought reasoning

## Bug Analysis
The program sets up an ancilla in |-> for the Boolean-to-phase trick, but forgets to uncompute the ancilla.

Buggy behavior:
1. X(q[0]), X(q[1]): input |11>
2. X(q[2]), H(q[2]): ancilla = |-> = (|0>-|1>)/sqrt(2)
3. State: |11>(|0>-|1>)/sqrt(2)
4. Toffoli: f(1,1)=1, flips ancilla: |11>(|1>-|0>)/sqrt(2) = -|11>|->
5. Without uncomputation, ancilla is still in |->
6. Measuring |-> gives |0> or |1> with equal probability -> entangled output

Fix: Add H(q[2]); X(q[2]); after Toffoli to uncompute ancilla back to |0>.
After fix: H|-> = |1>, X|1> = |0>. With the -1 global phase: -|110>.
P(|110>) = 1.0. Index = 6.

## isqExpand/isqd/126

- task_id: `isqExpand/isqd/126`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `deriving_gate`, `custom_gate`, `unitary_matrix`, `isq_syntax`
- source: `qa_pipeline`
- dataset_index: `2156`

### Prompt

isQ中deriving gate的语法是什么？如何用矩阵定义自定义量子门？给出1-qubit和2-qubit的例子。

### Chain-of-thought reasoning

首先分析问题要求：需要解释isQ中deriving gate的语法并给出两个例子。第一步，回顾isQ的自定义门定义语法，其核心格式为 'deriving gate 名称 = 矩阵;'。第二步，确定1-qubit的例子，选择Hadamard门，其矩阵为 (1/√2)[[1,1],[1,-1]]，用小数近似表示为0.7071。第三步，确定2-qubit的例子，选择CNOT门，其矩阵为4×4的标准CNOT矩阵。第四步，补充说明矩阵必须是酉矩阵、维度必须匹配量子比特数量等关键约束。第五步，提及自定义门可与ctrl、inv等修饰符配合使用的高级用法。最终整合为完整的中文回答。

### Reference answer

在isQ中，使用 deriving gate 关键字可以通过酉矩阵（unitary matrix）来定义自定义量子门。

**基本语法：**
```
deriving gate name = [[a,b,...],[c,d,...],...];
```
其中 name 是自定义门的名称，等号右边是一个二维数组，表示酉矩阵的元素，每行用方括号括起，行与行之间用逗号分隔。

**1-qubit 示例 — 自定义Hadamard门：**
```
import std;
deriving gate myH = [[0.7071,0.7071],[0.7071,-0.7071]];
qbit q[1];
procedure main() {
    myH(q[0]);
}
```
这里 0.7071 ≈ 1/√2，矩阵维度为 2×2。

**2-qubit 示例 — 自定义CNOT门：**
```
import std;
deriving gate myCNOT = [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]];
qbit q[2];
procedure main() {
    myCNOT(q[0], q[1]);
}
```
对于 n 个量子比特的门，矩阵维度为 2^n × 2^n，因此2-qubit门使用 4×4 矩阵。调用时传入对应数量的量子比特参数。

**注意事项：**
1. 矩阵必须是酉矩阵（U†U = I），否则行为未定义。
2. 矩阵维度必须为 2^n × 2^n，n为门操作的量子比特数。
3. 自定义门可与 ctrl、inv 等修饰符组合使用，例如 `ctrl @[c] myH(t);` 或 `inv myH(q[0]);`。

## isqExpand/isqd/83

- task_id: `isqExpand/isqd/83`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nctrl_modifier`, `superposition`, `entanglement`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `3080`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    nctrl X(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial: |00>
2. H(q[0]): (|00>+|10>)/sqrt(2)
3. nctrl @[q[0]] X(q[1]): conditionally flip q[1] when q[0]=|0>
   |00> branch: q[0]=0, fires -> |01>
   |10> branch: q[0]=1, no fire -> |10>
   State: (|01>+|10>)/sqrt(2)
4. P(|01>)=0.5 at index 1, P(|10>)=0.5 at index 2
Distribution: [0.0, 0.5, 0.5, 0.0]

### Reference answer

{'predicted_probs': {'00': 0.0, '01': 0.5, '10': 0.5, '11': 0.0}, 'explanation': 'Step-by-step:\n1. H(q[0]): |00> -> (|0>+|1>)/sqrt(2) ⊗ |0> = (|00>+|10>)/sqrt(2)\n2. nctrl @[q[0]] X(q[1]): applies X to q[1] when q[0]=|0>.\n   - |00> component: q[0]=|0>, nctrl fires, X(q[1]): |00> -> |01>\n   - |10> component: q[0]=|1>, nctrl does NOT fire: |10> stays\n   Result: (|01>+|10>)/sqrt(2)\n3. This is a Bell-like state (|Psi+>).\n4. P(|01>) = 0.5 at index 1, P(|10>) = 0.5 at index 2.\nDistribution: [0.0, 0.5, 0.5, 0.0].'}

## isqExpand/isqd/19

- task_id: `isqExpand/isqd/19`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `for_loop`, `off_by_one`, `range_error`, `common_error`
- source: `isq_expansion`
- dataset_index: `3658`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```isq
import std;
qbit q[3];

procedure main() {
    for i in 0:2 {
        H(q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The for loop range `0:2` iterates over i=0,1 only (half-open interval). This misses q[2], which stays in |0>.

Buggy behavior: H applied only to q[0],q[1]. q[2] is always |0>.
Buggy distribution: 4 states with q[2]=0 each have P=0.25.

Fix: Change `0:2` to `0:3` so the loop covers i=0,1,2.
After fix: All 3 qubits in |+>, uniform distribution P=1/8 for all 8 states.

## isqExpand/isqd/169

- task_id: `isqExpand/isqd/169`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `measurement`, `bell_state`, `quantum_collapse`, `classical_control`
- source: `isq_expansion`
- dataset_index: `3224`

### Prompt

The following isQ code creates a Bell pair and then tries to uncompute q[1] by measuring it and conditionally applying X. However, the second measurement accidentally targets q[0] again instead of q[1]. Since measuring the same qubit twice always gives the same result (quantum state collapse), the conditional X does not uncompute correctly. Fix the measurement target so q[1] is measured instead of measuring q[0] a second time.

### Chain-of-thought reasoning

The buggy code creates a Bell state (|00> + |11>)/sqrt(2) with H and CNOT. It measures q[0] (collapsing the state to either |00> or |11>). Then it mistakenly measures q[0] again instead of q[1]. Due to quantum state collapse, the second measurement of q[0] always returns the same value as the first. So when the first measurement yields 1 (state |11>), the second measurement of q[0] also yields 1, and X(q[1]) produces |10>. This gives probabilities [0.5, 0.0, 0.5, 0.0]. The fix changes the second measurement to M(q[1]). In a Bell state, q[0] and q[1] are perfectly correlated: if q[0]=0 then q[1]=0, if q[0]=1 then q[1]=1. So measuring q[1] after q[0] always agrees. When both are 1, X(q[1]) flips it to 0, yielding |00> in all cases. Expected probabilities: [1.0, 0.0, 0.0, 0.0].

## isqExpand/isqd/74

- task_id: `isqExpand/isqd/74`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nested_procedures`, `procedure_call`, `entanglement`
- source: `isq_expansion`
- dataset_index: `1176`

### Prompt

Create an isQ quantum circuit that demonstrating nested procedure calls where procedure A calls procedure B.

Define two procedures:
1. `procedure flip(qbit a)` — applies X gate to qubit a
2. `procedure flip_and_hadamard(qbit a, qbit b)` — calls `flip(a)` and then applies H to b

In `main()`, call `flip_and_hadamard(q[0], q[1])`, then apply CNOT(q[1], q[0]) and measure both qubits.

Trace: flip(q[0]) -> q[0]=|1>. H(q[1]) -> q[1]=(|0>+|1>)/sqrt(2). CNOT(q[1], q[0]) with q[1] in superposition creates entanglement.

Expected: P(|10>) = 0.5, P(|01>) = 0.5.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate nested procedures (flip_and_hadamard calls flip).

1. flip(q[0]): X(q[0]) -> q[0] = |1>
2. H(q[1]): q[1] = (|0>+|1>)/sqrt(2)
3. State after flip_and_hadamard: |1>(|0>+|1>)/sqrt(2) = (|10>+|11>)/sqrt(2)
4. CNOT(q[1], q[0]): control=q[1], target=q[0]
   - |10>: q[1]=0, no flip -> |10>
   - |11>: q[1]=1, flip q[0]: |11> -> |01>
5. Final: (|10>+|01>)/sqrt(2)
6. P(|01>)=0.5 at index 1, P(|10>)=0.5 at index 2

## isqExpand/isqd/147

- task_id: `isqExpand/isqd/147`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `phase_oracle`, `boolean_oracle`, `phase_kickback`, `ancilla`, `cnot`
- source: `isq_expansion`
- dataset_index: `5339`

### Prompt

请用isQ语言编写一个量子电路：an isQ circuit that demonstrates the ancilla-in-|−⟩ trick for converting a Boolean oracle into a phase oracle. Use 2 qubits: q[0] as data and q[1] as ancilla. Steps: (1) Put data qubit in |+⟩ with H. (2) Prepare ancilla in |−⟩ (X then H). (3) Apply CNOT(data, ancilla) as the Boolean oracle f(x)=x. (4) Apply H to data qubit to observe the phase kickback. The circuit should demonstrate that the phase oracle flipped the data qubit from |0⟩ to |1⟩. Measure both qubits.

### Chain-of-thought reasoning

The ancilla-in-|−⟩ trick converts a Boolean oracle U_f into a phase oracle. Starting state |00⟩. After H(q[0]): (|00⟩+|10⟩)/√2. After X(q[1]): (|01⟩+|11⟩)/√2. After H(q[1]): [(|00⟩-|01⟩)+(|10⟩-|11⟩)]/2. After CNOT(q[0],q[1]) (Boolean oracle f(x)=x): [(|00⟩-|01⟩)+(|11⟩-|10⟩)]/2 = (|0⟩-|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2 = |−⟩|−⟩. The phase kickback flipped the data qubit from |+⟩ to |−⟩. After H(q[0]): H|−⟩ = |1⟩, so state = |1⟩|−⟩ = (|10⟩-|11⟩)/√2. Measuring both qubits gives |10⟩ with prob 0.5 and |11⟩ with prob 0.5, confirming the data qubit is |1⟩ — the phase oracle applied (-1)^f(x) correctly.

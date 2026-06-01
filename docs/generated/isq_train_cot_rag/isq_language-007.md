# ISQ training COT RAG corpus: isq_language shard 7

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/24

- task_id: `isqExpand/isqd/24`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `boolean_oracle`, `phase_oracle`, `ancilla`, `oracle_conversion`
- source: `qa_pipeline`
- dataset_index: `3415`

### Prompt

在量子计算中，Boolean oracle和Phase oracle有什么区别？请分别解释它们的数学定义和isQ实现方式，并说明如何通过ancilla技巧将Boolean oracle转换为Phase oracle。

### Chain-of-thought reasoning

## 推理
目标：对比Boolean oracle和Phase oracle的定义与isQ实现。

关键点：
1. Boolean oracle: O_f|x>|y> = |x>|y⊕f(x)>，需要ancilla
2. Phase oracle: O_f|x> = (-1)^f(x)|x>，编码为相位
3. 转换技巧：ancilla准备为|->态，Boolean oracle自动变成Phase oracle
4. 因为|-> = (|0>-|1>)/√2，XOR操作等价于引入(-1)^f(x)全局相位
5. isQ中Boolean用CNOT/Toffoli，Phase用CZ/ctrl Z

### Reference answer

## Boolean Oracle与Phase Oracle

### Boolean Oracle（布尔oracle）
布尔oracle将函数f(x)的结果写入一个辅助比特（ancilla）：
$$O_f|x
angle|y
angle = |x
angle|y \oplus f(x)
angle$$

其中⊕是异或运算。当y=0时，辅助比特直接存储f(x)的值。

isQ实现方式：使用CNOT或Toffoli将f(x)的结果写入ancilla比特。

### Phase Oracle（相位oracle）
相位oracle将f(x)编码为相位因子：
$$O_f|x
angle = (-1)^{f(x)}|x
angle$$

当f(x)=1时，|x>获得负号（-1相位）。这种标记对幅度不可见，但会影响干涉。

isQ实现方式：使用CZ或ctrl @[] Z来对目标态添加相位。

### Boolean → Phase转换（ancilla in |-> trick）
将ancilla准备为|-> = (|0>-|1>)/√2状态，Boolean oracle的作用变成相位翻转：

$$O_f|x
angle|{-}
angle = (-1)^{f(x)}|x
angle|{-}
angle$$

步骤：
1. 对ancilla施加X然后H，得到|->
2. 执行Boolean oracle
3. ancilla保持在|->不变，但输入寄存器获得了(-1)^f(x)相位

### 核心区别总结
| 特性 | Boolean Oracle | Phase Oracle |
|------|---------------|-------------|
| 输出方式 | 写入ancilla比特 | 编码为相位(-1)^f(x) |
| 需要ancilla | 是 | 否（直接版）|
| 典型门 | CNOT, Toffoli | CZ, ctrl Z |
| 典型应用 | Deutsch-Jozsa | Grover搜索 |

## isqExpand/isqd/159

- task_id: `isqExpand/isqd/159`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `GPhase`, `global_phase`, `gate_syntax`
- source: `isq_expansion`
- dataset_index: `2688`

### Prompt

The following isQ program contains a bug: GPhase is called with a qubit argument, but GPhase is a global phase gate that only accepts a double parameter. Fix the code so it compiles and runs correctly.

### Chain-of-thought reasoning

The bug is that GPhase(pi, q[0]) passes a qubit argument to GPhase, but GPhase is a global phase gate that only takes a single double parameter (the angle theta). It applies a global phase e^{i*theta} to the entire quantum state and has no target qubit. The fix is to remove the qubit argument: GPhase(pi). Since GPhase does not change measurement probabilities, the circuit H(q[0]) followed by CNOT(q[0], q[1]) produces a Bell state with 50% probability of |00⟩ and 50% probability of |11⟩. The expected_probs array is [0.5, 0.0, 0.0, 0.5] for the 2-qubit measurement outcomes.

## isqExpand/isqd/60

- task_id: `isqExpand/isqd/60`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `output_prediction`, `bell_state`, `x_gate`, `independent_qubits`, `cnot`, `probability_distribution`
- source: `isq_expansion`
- dataset_index: `2552`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    H(q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
q[0] is acted on only by X, becoming |1>. It is not entangled with q[1],q[2].
q[1] gets H: (|0>+|1>)/sqrt(2). CNOT(q[1],q[2]) creates Bell state on q[1],q[2].

Overall state: |1> tensor (|00>+|11>)/sqrt(2) = (|100>+|111>)/sqrt(2).

3-qubit probs (8 values, indexed by q[0]*4+q[1]*2+q[2]):
P(|100>)=0.5 at index 4, P(|111>)=0.5 at index 7.
All other indices = 0.

### Reference answer

{'predicted_probs': {'000': 0.0, '001': 0.0, '010': 0.0, '011': 0.0, '100': 0.5, '101': 0.0, '110': 0.0, '111': 0.5}, 'explanation': 'Step-by-step:\n1. X(q[0]): q[0] = |1>. This is independent of q[1],q[2].\n2. H(q[1]): q[1] = (|0>+|1>)/sqrt(2)\n3. CNOT(q[1],q[2]): creates Bell state on q[1],q[2]:\n   (|00>+|11>)/sqrt(2)\n4. Combined state: |1> x (|00>+|11>)/sqrt(2) = (|100>+|111>)/sqrt(2)\n\nMeasurement probabilities:\nP(|100>) = 0.5, index = 1*4+0*2+0 = 4\nP(|111>) = 0.5, index = 1*4+1*2+1 = 7\nDistribution: [0, 0, 0, 0, 0.5, 0, 0, 0.5]'}

## isqExpand/isqd/52

- task_id: `isqExpand/isqd/52`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `measurement`, `missing_measurement`, `duplicate_measurement`, `measurement_order`, `probs_mode`, `best_practice`
- source: `qa_pipeline`
- dataset_index: `2417`

### Prompt

isQ中测量（Measurement）有哪些常见错误和最佳实践？包括：遗漏测量、重复测量同一量子比特、以及测量顺序对概率分布索引的影响。请详细说明并给出代码示例。

### Chain-of-thought reasoning

## 推理
目标：总结isQ测量的常见错误和最佳实践。

关键点：
1. 遗漏测量导致输出维度错误
2. 重复测量同一qubit增加维度，概率分布异常
3. 测量顺序影响概率索引（第一个M()=最高位）
4. 最佳实践：每个qubit测量一次，按索引顺序

### Reference answer

## isQ测量的常见错误与最佳实践

### 错误一：遗漏测量
如果某个qubit参与了计算但没有被M()测量，`--probs`输出将只反映被测量qubit的分布，导致结果与预期不符。

**错误示例**：
```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]);
    // 遗漏了M(q[2])！GHZ态变成2-qubit分布
}
```
预期是3-qubit GHZ态（8个概率值），但只测量2个qubit得到4个概率值。

### 错误二：重复测量
对同一qubit调用两次M()不会报编译错误，但第二次测量总是返回第一次坍缩后的结果。在`--probs`模式下，重复测量会增加输出向量的维度，导致概率分布混乱。

**错误示例**：
```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    M(q[0]);
    M(q[0]);  // 重复测量！维度从2变为4
}
```
输出变成4个概率而非2个，结果：[0.5, 0.0, 0.0, 0.5]（只出现00和11）。

### 测量顺序与索引
`--probs`模式下，概率索引按M()调用顺序排列：第一个M()对应最高位bit。
```isq
M(q[0]); M(q[1]);  // 索引 = q[0]*2 + q[1]
M(q[1]); M(q[0]);  // 索引 = q[1]*2 + q[0]，顺序反转！
```

### 最佳实践
1. 对所有相关qubit都调用M()，且每个qubit只测量一次
2. 按qubit索引顺序测量：M(q[0]); M(q[1]); M(q[2]);
3. 测量前确认num_qubits_measured与实际M()调用次数一致
4. 使用for循环批量测量：`for i in 0:N { M(q[i]); }`

## isqExpand/isqd/79

- task_id: `isqExpand/isqd/79`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `ctrl_modifier`, `syntax_error`, `ctrl_at_syntax`
- source: `isq_expansion`
- dataset_index: `540`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    ctrl q[0] Z(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The buggy code writes `ctrl q[0] Z(q[1])` but the correct isQ syntax requires @[] brackets: `ctrl @[q[0]] Z(q[1])`.

Without @[], the compiler cannot parse the control qubit specification. The @ symbol and square brackets are mandatory in the explicit control form.

Fix: Change `ctrl q[0]` to `ctrl @[q[0]]`.

## isqExpand/isqd/134

- task_id: `isqExpand/isqd/134`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `ctrl`, `procedure`, `controlled_operation`, `isq_syntax`
- source: `isq_expansion_qa`
- dataset_index: `1961`

### Prompt

isQ中如何对过程（procedure）施加控制？ctrl @[q[0]] myProc(q[1])的含义和限制是什么？

### Chain-of-thought reasoning

首先分析问题核心：isQ中对procedure施加控制的机制。步骤1：解释ctrl语法的基本结构，即 ctrl @[控制比特] 过程名(目标比特)。步骤2：明确 ctrl @[q[0]] myProc(q[1]) 的具体语义——q[0]为控制，q[1]为目标，myProc仅在控制比特为|1⟩时执行。步骤3：梳理限制条件——被控制的过程必须是纯量子操作，不能含测量、经典条件分支等。步骤4：补充多控制比特的用法。步骤5：说明编译器层面的实现原理。综合以上得出完整答案。

### Reference answer

在isQ中，可以使用 ctrl 关键字对过程（procedure）施加控制。语法格式为：ctrl @[控制比特列表] 过程名(目标比特列表)。

例如 ctrl @[q[0]] myProc(q[1]) 的含义是：以 q[0] 作为控制比特，对 q[1] 施加 myProc 过程定义的量子操作。只有当 q[0] 处于 |1⟩ 状态时，myProc 中定义的操作才会作用于 q[1]；当 q[0] 处于 |0⟩ 状态时，不执行任何操作。

主要限制包括：
1. 被控制的过程内部不能包含测量操作（M），因为测量会破坏量子叠加态，导致控制语义不明确。
2. 被控制的过程不能包含经典条件分支（if语句依赖测量结果），因为控制操作需要在量子层面保持相干性。
3. 被控制的过程只能包含纯量子门操作，如单比特门、多比特门、旋转门等。
4. 可以指定多个控制比特，例如 ctrl @[q[0], q[1]] myProc(q[2]) 表示当 q[0] 和 q[1] 同时为 |1⟩ 时才执行。
5. 对过程施加控制时，编译器会将过程中的每个门操作逐个转换为受控版本，等价于将该过程的矩阵表示作为整体构造受控门。

## isqExpand/isqd/48

- task_id: `isqExpand/isqd/48`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `entanglement`, `measurement_order`
- source: `isq_expansion`
- dataset_index: `2743`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;
qbit grid[2][2];

procedure main() {
    for j in 0:2 {
        H(grid[0][j]);
        CNOT(grid[0][j], grid[1][j]);
    }
    M(grid[0][0]); M(grid[0][1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The program creates column-wise Bell pairs on grid[2][2] but only measures the first row (grid[0][0] and grid[0][1]). The second row qubits are entangled but unmeasured, causing incorrect --probs output.

Fix: Add M(grid[1][0]) and M(grid[1][1]) to measure all 4 qubits.

After fix: column-wise entanglement means grid[0][j]=grid[1][j]. Valid 4-qubit outcomes: 0000, 0101, 1010, 1111, each P=0.25.

## isqExpand/isqd/63

- task_id: `isqExpand/isqd/63`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `for_loop`, `batch_operation`, `x_gate`, `measurement`, `best_practice`, `idiomatic`
- source: `isq_expansion`
- dataset_index: `4913`

### Prompt

Create an isQ quantum circuit that applies X to all qubits in a 5-qubit register using a for loop, then measures all 5 qubits using another for loop. This demonstrates the idiomatic pattern for batch operations in isQ.

### Chain-of-thought reasoning

## Reasoning
Idiomatic for-loop pattern for batch gate application and measurement.

1. Declare qbit q[5] globally.
2. for i in 0:5 { X(q[i]); } — flips all 5 qubits to |1>.
3. for i in 0:5 { M(q[i]); } — measures all 5 qubits.

State: |11111> = all qubits |1>.
In --probs mode: 2^5=32 probabilities. Index 31 (=11111 binary) = 1.0, all others = 0.0.

## isqExpand/isqd/4

- task_id: `isqExpand/isqd/4`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `inv_modifier`, `adjoint`, `s_gate`
- source: `isq_expansion`
- dataset_index: `117`

### Prompt

I need an isQ program to demonstrates the inv modifier by applying S followed by inv S (S-dagger) to a qubit.

Start with q[0] in |0>, apply H to create |+>, then apply S (which adds a pi/2 phase to |1>), then apply inv S (which removes the pi/2 phase). The two operations cancel, restoring |+>. Finally apply H to map back to |0> and measure.

Since S * S-dagger = Identity, the final state should be |0> with probability 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: Show that S followed by inv S (S-dagger) is identity.

1. H(q[0]): |0> -> |+> = (|0>+|1>)/sqrt(2)
2. S(q[0]): adds phase pi/2 to |1> -> (|0>+i|1>)/sqrt(2)
3. inv S(q[0]): removes phase pi/2 -> (|0>+|1>)/sqrt(2) = |+>
4. H(q[0]): |+> -> |0>

S * S_dagger = I, so steps 2+3 cancel.
Final state: |0> with probability 1.0

## isqExpand/isqd/36

- task_id: `isqExpand/isqd/36`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `isq_syntax_arrays`
- source: `isq_expansion_qa`
- dataset_index: `851`

### Prompt

isQ中如何定义接受量子比特数组作为参数的procedure？如何在procedure中对数组参数进行批量门操作？请说明procedure参数的声明语法（qbit reg[N]）以及如何在调用时传入全局量子比特数组。请结合具体示例进行说明。

### Chain-of-thought reasoning

## 推理
目标：解释procedure接受qbit数组参数的语法。

关键点：
1. qbit reg[N]声明固定长度的数组参数
2. 调用时传入匹配大小的全局数组
3. 量子比特是引用语义
4. 可以与double等经典参数组合

### Reference answer

## isQ中接受量子比特数组参数的procedure

### 基本语法
isQ允许procedure接收固定长度的量子比特数组：
```isq
procedure apply_h_layer(qbit reg[4]) {
    for i in 0:4 {
        H(reg[i]);
    }
}
```
参数声明 `qbit reg[4]` 表示该过程接收一个长度为4的量子比特数组。函数体内通过 `reg[i]` 访问各量子比特。

### 调用方式
在 `main()` 中用全局量子比特数组调用：
```isq
import std;
qbit q[4];

procedure apply_h_layer(qbit reg[4]) {
    for i in 0:4 { H(reg[i]); }
}

procedure main() {
    apply_h_layer(q);
    for i in 0:4 { M(q[i]); }
}
```
调用 `apply_h_layer(q)` 将整个全局数组 `q` 传入。

### 注意事项
1. 数组大小必须在编译期确定，不支持变长数组参数。
2. 过程参数中的 `qbit reg[N]` 中 N 必须是字面量常数。
3. 传入的数组大小必须匹配声明的大小。
4. procedure内部对 `reg[i]` 的门操作直接作用在实际量子比特上（量子比特是引用语义，不是值拷贝）。

### 组合示例：数组参数 + 旋转角度参数
```isq
procedure rotate_all(qbit reg[3], double angle) {
    for i in 0:3 {
        Ry(angle, reg[i]);
    }
}
```
这展示了procedure同时接受量子比特数组和经典参数的能力。

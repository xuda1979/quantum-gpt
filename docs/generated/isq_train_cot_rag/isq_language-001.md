# ISQ training COT RAG corpus: isq_language shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/67

- task_id: `isqExpand/isqd/67`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nctrl_modifier`, `negative_control`, `fredkin_variant`, `isq_syntax`
- source: `isq_expansion_qa`
- dataset_index: `3820`

### Prompt

isQ中nctrl修饰符的语法和语义是什么？它和ctrl有什么区别？请解释nctrl @[...]的含义，给出具体示例，并说明nctrl在量子电路中的典型应用场景（如条件翻转、Fredkin门变体等）。

### Chain-of-thought reasoning

## 推理
目标：解释nctrl修饰符的语法和语义。

关键点：
1. nctrl = negative control，控制比特为|0>时执行
2. 语法：nctrl @[control] Gate(target)
3. 与ctrl对比：ctrl在|1>时执行，nctrl在|0>时执行
4. 应用：条件翻转、混合控制模式、Fredkin门变体
5. 限制：只能修饰单量子比特门

### Reference answer

## isQ中的nctrl修饰符

### 基本概念
nctrl（negative control）是ctrl的补充。当控制比特处于|0>状态时，目标门才会执行。

### 语法
```isq
nctrl @[q[0]] X(q[1]);  // 当q[0]=|0>时，对q[1]施加X门
```

### 与ctrl的对比
| 修饰符 | 控制条件 | 等效操作 |
|--------|----------|----------|
| ctrl @[c] G(t) | c=|1>时执行G | 标准控制门 |
| nctrl @[c] G(t) | c=|0>时执行G | 负控制门 |

### 典型应用

**1. 条件翻转**
```isq
// 当q[0]=|0>时翻转q[1]
nctrl @[q[0]] X(q[1]);
```

**2. 混合控制模式**
可以结合使用ctrl和nctrl实现混合控制：
先用X翻转控制比特，再用ctrl，最后再翻转回来。但nctrl更简洁。

**3. Fredkin门变体**
标准Fredkin门在控制比特=|1>时交换两个目标比特。用nctrl可以实现"当控制比特=|0>时交换"的变体。

### 完整示例
```isq
import std;
qbit q[2];

procedure main() {
    // q[0]初始为|0>，nctrl条件满足
    nctrl @[q[0]] X(q[1]);  // q[1]被翻转
    M(q[0]); M(q[1]);
    // 结果：P(|01>) = 1.0
}
```

### 注意事项
- nctrl只能修饰单量子比特门
- 多控制nctrl：`nctrl @[q[0], q[1]] X(q[2])` — 当q[0]=|0>且q[1]=|0>时执行
- nctrl可以与inv组合：`nctrl @[q[0]] inv S(q[1])`

## isqExpand/isqd/68

- task_id: `isqExpand/isqd/68`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nested_procedures`, `procedure_call`, `modular_circuit`, `isq_syntax`
- source: `qa_pipeline`
- dataset_index: `1237`

### Prompt

isQ中如何实现嵌套过程调用（procedure A调用procedure B）？请说明嵌套调用的语法规则、参数传递方式，以及在量子电路设计中的实际用途。给出一个procedure A调用procedure B的完整代码示例，并分析电路执行流程。

### Chain-of-thought reasoning

## 推理
目标：解释isQ中嵌套过程调用的机制。

关键点：
1. 被调用过程必须先定义
2. qbit参数通过引用传递
3. 经典参数通过值传递
4. 不支持递归（procedure不能调用自身）
5. 用途：模块化设计、分层抽象、重复模式

### Reference answer

## isQ中的嵌套过程调用

### 基本规则
isQ支持过程相互调用，只要被调用的过程在调用点之前已经定义：
```isq
procedure B(qbit a) { H(a); }
procedure A(qbit a, qbit b) {
    B(a);    // 调用B
    CNOT(a, b);
}
```

### 参数传递
- 量子比特参数通过引用传递（不是复制）
- 经典参数（int, double）通过值传递
- 可以传递单个qbit或qbit数组

### 实际用途
1. **模块化电路设计**：将复杂电路分解为可复用子模块
2. **分层抽象**：底层过程实现基本操作，上层过程组合底层过程
3. **重复模式**：在for循环中调用子过程实现分层电路

### 完整示例：Bell态制备器
```isq
import std;
qbit q[2];

// 底层过程：创建叠加态
procedure make_superposition(qbit a) {
    H(a);
}

// 上层过程：创建Bell态，调用make_superposition
procedure make_bell(qbit a, qbit b) {
    make_superposition(a);  // 嵌套调用
    CNOT(a, b);
}

procedure main() {
    make_bell(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```
执行流程：main -> make_bell -> make_superposition(q[0]) -> H(q[0])，然后CNOT(q[0], q[1])。结果：P(|00>)=0.5, P(|11>)=0.5。

### 注意事项
- 被调用过程必须先定义
- isQ不支持递归调用（procedure不能调用自身）
- 嵌套深度没有显式限制，但过深的嵌套会降低可读性

## isqExpand/isqd/184

- task_id: `isqExpand/isqd/184`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `ancilla_management`, `toffoli_gate`, `uncomputation`, `cnot_gate`, `superposition`
- source: `isq_expansion`
- dataset_index: `4725`

### Prompt

Create an isQ quantum circuit that an isQ circuit that demonstrates proper ancilla management. The circuit should: (1) use 2 data qubits in superposition as controls, (2) use 1 ancilla qubit as the target of a Toffoli gate, (3) use the ancilla to apply a CNOT to a 3rd data qubit, (4) uncompute the ancilla by applying the same Toffoli again, and (5) measure all qubits. The ancilla must return to |0⟩ after uncomputation. Declare q[0], q[1] as control data qubits, q[2] as the target data qubit, and q[3] as the ancilla. Use H gates on q[0] and q[1] to create superposition.

### Chain-of-thought reasoning

Step 1: Start with all qubits in |0000⟩ (q[0..3]).
Step 2: Apply H(q[0]) → (|0⟩+|1⟩)/√2 ⊗ |000⟩ = (|0000⟩+|1000⟩)/√2.
Step 3: Apply H(q[1]) → (|0000⟩+|0100⟩+|1000⟩+|1100⟩)/2.
Step 4: Toffoli(q[0],q[1],q[3]) flips q[3] when q[0]=q[1]=1. Only |1100⟩→|1101⟩.
State: (|0000⟩+|0100⟩+|1000⟩+|1101⟩)/2.
Step 5: CNOT(q[3],q[2]) flips q[2] when q[3]=1. Only |1101⟩→|1111⟩.
State: (|0000⟩+|0100⟩+|1000⟩+|1111⟩)/2.
Step 6: Toffoli(q[0],q[1],q[3]) uncomputes. Only |1111⟩ has q[0]=q[1]=1 and q[3]=1, so q[3] flips to 0: |1111⟩→|1110⟩.
State: (|0000⟩+|0100⟩+|1000⟩+|1110⟩)/2.
Step 7: Probabilities for 4 qubits (indices: 0,4,8,14 each = 0.25):
Index 0 (0000): 0.25, Index 4 (0100): 0.25, Index 8 (1000): 0.25, Index 14 (1110): 0.25.
All other indices: 0. Sum = 1.0. Ancilla q[3] is always |0⟩, confirming proper uncomputation.

## isqExpand/isqd/140

- task_id: `isqExpand/isqd/140`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `comparator`, `toffoli`, `negative_control_via_X`, `multi_qubit_logic`, `superposition_testing`
- source: `isq_expansion`
- dataset_index: `5768`

### Prompt

Help me write isQ code that a 3-qubit comparator in isQ: q[0] and q[1] are single-bit inputs, q[2] is an ancilla output. Set q[2] to |1> if and only if q[0] > q[1] (strictly greater). Prepare q[0] and q[1] in equal superposition with Hadamard gates so all four input combinations are tested simultaneously.

### Chain-of-thought reasoning

We need a 3-qubit circuit comparing two single-bit inputs q[0] and q[1], storing the result on ancilla q[2]. The condition q[0] > q[1] for 1-bit values is true only when q[0]=1 and q[1]=0 (the single case 1>0). This is the AND of q[0] and NOT(q[1]). We implement NOT(q[1]) by applying X before and after a Toffoli gate. Step 1: Apply H to q[0] and q[1] creating equal superposition over |00>, |01>, |10>, |11>. Step 2: Flip q[1] with X. Step 3: Toffoli(q[0],q[1],q[2]) sets q[2]=1 only when both controls are 1, meaning original q[0]=1 AND original q[1]=0. Step 4: Restore q[1] with X. Final state mapping: |000>->|000>, |010>->|010>, |100>->|101>, |110>->|110>. Each has probability 1/4=0.25. The 8-element probability array for 3 qubits is [0.25,0.0,0.25,0.0,0.0,0.25,0.25,0.0].

## isqExpand/isqd/23

- task_id: `isqExpand/isqd/23`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `mid_circuit_measurement`, `feedforward`, `classical_control`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `4560`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    int r = M(q[0]);
    if (r == 1) {
        X(q[1]);
    }
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[0]): q[0] = |1>
2. int r = M(q[0]): deterministic measurement, r = 1
3. if (r == 1): TRUE -> enters block
4. X(q[1]): q[1] = |1>
5. M(q[1]): q[1] measured as 1

q[0] was measured mid-circuit (still |1>), q[1] measured at end (|1>).
Final: |11>, index = 3, P = 1.0
Distribution: [0.0, 0.0, 0.0, 1.0]

### Reference answer

{'predicted_probs': {'00': 0.0, '01': 0.0, '10': 0.0, '11': 1.0}, 'explanation': 'Step-by-step:\n1. X(q[0]): q[0] -> |1>\n2. int r = M(q[0]): q[0]=|1>, so r=1 deterministically. q[0] remains |1> after measurement.\n3. if (r == 1): condition is true\n4. X(q[1]): q[1] flips from |0> to |1>\n5. M(q[1]): measures q[1] = |1>\n\nFinal state: q[0]=|1>, q[1]=|1> = |11>\nIndex = 1*2 + 1 = 3\nP(|11>) = 1.0 at index 3.\nDistribution: [0.0, 0.0, 0.0, 1.0].\n\nNote: The mid-circuit measurement on q[0] collapses it to |1> (deterministic since it was already in |1>). The classical variable r=1 then triggers the feedforward X(q[1]).'}

## isqExpand/isqd/96

- task_id: `isqExpand/isqd/96`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `global_phase`, `phase_manipulation`, `deriving_gate`, `ctrl_modifier`
- source: `isq_expansion`
- dataset_index: `1432`

### Prompt

实现以下量子计算任务（使用isQ）：uses GPhase inside a `deriving gate` procedure to implement a controlled phase rotation.

Define:
```
procedure Rphase(qbit q) {
    ctrl GPhase(1.5707963267949, q);
} deriving gate
```
This creates a gate equivalent to diag(1, i) (S gate up to global phase).

In `procedure main()`:
1. Apply X(q[0]) to set q[0] = |1>
2. Apply Rphase(q[0]) -- adds phase i to |1> component
3. Apply H(q[0]) -- converts phase difference into measurable probabilities
4. Measure q[0]

Expected: P(|0>) = 0.5, P(|1>) = 0.5.

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[0]): |0> -> |1>
2. Rphase(q[0]): ctrl GPhase(pi/2, q[0]). When q[0]=|1>, applies e^{i*pi/2}=i. |1> -> i|1>.
3. H(q[0]): H(i|1>) = i*(|0>-|1>)/sqrt(2)
4. P(|0>) = |i/sqrt(2)|^2 = 0.5. P(|1>) = |-i/sqrt(2)|^2 = 0.5.
Distribution: [0.5, 0.5].

## isqExpand/isqd/13

- task_id: `isqExpand/isqd/13`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `mid_circuit_measurement`, `feedforward`, `classical_control`, `print_debug`, `isq_syntax`
- source: `isq_expansion_qa`
- dataset_index: `3049`

### Prompt

isQ中如何实现中间测量（mid-circuit measurement）和经典前馈控制（feedforward）？什么是print调试？请解释mid-circuit measurement的语法，以及如何根据测量结果用if语句控制后续量子操作。

### Chain-of-thought reasoning

## 推理
目标：解释中间测量、经典前馈控制和print调试。

关键点：
1. int r = M(q[0]) 将测量结果存储为经典变量
2. if (r == 1) { ... } 实现经典控制前馈
3. 与ctrl的区别：经典控制 vs 量子控制
4. print r 在--debug模式下输出
5. 应用场景：隐形传态、纠错、RUS

### Reference answer

## 中间测量与经典前馈控制

### 中间测量（Mid-Circuit Measurement）
isQ允许在电路中间测量量子比特，并将结果存储在经典变量中：
```isq
int r = M(q[0]);  // 测量q[0]，结果存入r（0或1）
```
这与电路末尾的测量不同——中间测量后，量子态坍缩，但程序继续执行。

### 经典前馈控制（Feedforward）
根据测量结果条件性地执行后续操作：
```isq
int r = M(q[0]);
if (r == 1) {
    X(q[1]);  // 只在r=1时翻转q[1]
}
```
这实现了经典-量子混合控制：测量结果（经典信息）决定后续量子门操作。

### 典型应用
1. **量子隐形传态**：Alice测量后，Bob根据结果做修正
2. **量子纠错**：测量综合征（syndrome），根据结果施加修正操作
3. **Repeat-Until-Success**：测量判断是否成功，失败则重试

### print调试
isQ支持print语句输出经典变量值，在 `--debug` 模式下可见：
```isq
int r = M(q[0]);
print r;  // 输出测量结果
```
注意：print只在 `isqc run --debug` 时显示输出，在 `--probs` 模式下不可见。

### 与ctrl修饰符的区别
| 方式 | 机制 | 适用场景 |
|------|------|----------|
| ctrl @[q] Gate(t) | 量子控制（相干） | 不需要坍缩 |
| int r = M(q); if(r==1) Gate(t) | 经典控制（测量） | 需要中间决策 |

### 完整示例：量子纠错风格
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    int r = M(q[0]);
    if (r == 1) {
        X(q[1]);  // 修正
    }
    M(q[1]);
}
```

### 注意事项
- 中间测量的qubit可以在全局或局部声明
- 使用 `stdout_match` 检查模式验证含print的程序
- `--probs` 模式下中间测量行为取决于模拟器实现

## isqExpand/isqd/136

- task_id: `isqExpand/isqd/136`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `procedures`, `nested_procedures`, `Ry_rotation`, `CNOT`, `bell_state`
- source: `isq_expansion`
- dataset_index: `621`

### Prompt

Implement a quantum circuit in isQ: Define two nested procedures in isQ: an inner procedure called inner_proc that takes two integer parameters (qubit indices) and applies an Ry rotation with angle pi/2 to the first qubit. Then define an outer procedure called outer_proc that takes the same two integer parameters, calls inner_proc with those parameters, and then applies a CNOT gate with the first qubit as control and the second as target. In main(), call outer_proc(0, 1) to operate on qubits q[0] and q[1]. Declare a global array of 2 qubits.

### Chain-of-thought reasoning

Step 1: We start with 2 qubits in state |00⟩. Step 2: inner_proc applies Ry(π/2) to q[0]. Ry(π/2)|0⟩ = cos(π/4)|0⟩ + sin(π/4)|1⟩ = (1/√2)|0⟩ + (1/√2)|1⟩. So the state becomes (1/√2)|00⟩ + (1/√2)|10⟩. Step 3: outer_proc then applies CNOT(q[0], q[1]). CNOT maps |00⟩→|00⟩ and |10⟩→|11⟩. State becomes (1/√2)|00⟩ + (1/√2)|11⟩, which is the Bell state |Φ+⟩. Step 4: Measurement probabilities are P(00)=0.5, P(01)=0.0, P(10)=0.0, P(11)=0.5. The 4-element probability vector is [0.5, 0.0, 0.0, 0.5].

## isqExpand/isqd/69

- task_id: `isqExpand/isqd/69`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `gate_decomposition`, `cz_gate`, `toffoli_cascade`, `phase_oracle`, `isq_syntax`
- source: `isq_expansion_qa`
- dataset_index: `2368`

### Prompt

isQ中如何将高层量子门分解为基本门的组合？请详细说明以下分解模式：
1. 用H+CNOT+H实现CZ门
2. 用Toffoli级联实现量子递增电路
3. 用ctrl @[...] Z(target)实现相位Oracle
给出每种分解的等价性证明思路和isQ代码示例。

### Chain-of-thought reasoning

## 推理
目标：解释三种高级门分解模式。

关键点：
1. CZ = H·CNOT·H（H在目标比特上）
2. 量子递增 = Toffoli级联（从高位到低位）
3. 相位Oracle = ctrl @[controls] Z(target)
4. CZ是对称的
5. 相位Oracle只改变相位，不改变概率

### Reference answer

## isQ中的门分解模式

### 1. CZ门分解：H + CNOT + H
CZ门的作用：当两个比特都为|1>时添加-1相位。
分解原理：`CZ(a,b) = H(b); CNOT(a,b); H(b);`

等价性证明思路：
- H将Z基转换为X基：HXH = Z, HZH = X
- CNOT = |0><0|⊗I + |1><1|⊗X
- H·CNOT·H = |0><0|⊗I + |1><1|⊗HXH = |0><0|⊗I + |1><1|⊗Z = CZ

```isq
import std;
qbit q[2];
procedure my_cz(qbit a, qbit b) {
    H(b); CNOT(a, b); H(b);
}
procedure main() {
    X(q[0]); X(q[1]);
    my_cz(q[0], q[1]);  // |11> -> -|11>（全局相位）
    M(q[0]); M(q[1]);
}
```

### 2. 量子递增电路（Toffoli级联）
对N比特寄存器实现+1操作（模2^N）：
从最高位向最低位，使用递增控制的Toffoli级联。

```isq
// 3比特递增：|abc> -> |abc+1 mod 8>
procedure increment3(qbit a, qbit b, qbit c) {
    ctrl @[a, b] X(c);  // Toffoli
    CNOT(a, b);
    X(a);
}
```

### 3. 相位Oracle：ctrl @[...] Z(target)
在特定计算基态上添加-1相位标记：
```isq
// 标记|111>态
ctrl @[q[0], q[1]] Z(q[2]);
```
等价于对角矩阵 diag(1,1,1,1,1,1,1,-1)。

### 注意事项
- CZ是对称的：CZ(a,b) = CZ(b,a)
- 递增电路的门操作顺序很重要
- 相位Oracle不改变概率分布，只改变相位

## isqExpand/isqd/185

- task_id: `isqExpand/isqd/185`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `ancilla_management`, `uncomputation`, `qbit_allocation`, `controlled_operations`, `isq_syntax`
- source: `qa_pipeline`
- dataset_index: `3248`

### Prompt

isQ中如何正确管理辅助量子比特（ancilla）？解释分配、使用、反计算、测量的模式。

### Chain-of-thought reasoning

该问题涉及isQ中辅助量子比特的完整生命周期管理。我需要从四个维度来组织答案：首先是分配方式，isQ通过全局qbit数组声明辅助比特，没有专门的ancilla关键字。其次是使用场景，主要是多控门分解和中间结果存储。第三是反计算（uncomputation），这是量子计算特有的概念，因为量子比特不能简单覆盖写入，必须通过逆运算恢复到初始状态，否则会引入纠缠。第四是测量与重置模式，包括不测量的干净复用、测量后经典反馈、测量后重置三种。isQ的特殊语法点包括：inv关键字用于取逆运算、Toffoli自逆特性、M()测量返回int值、if条件语句支持经典反馈。整体结构按生命周期顺序展开，每个部分配合代码示例说明。

### Reference answer

在isQ中，辅助量子比特（ancilla）的管理遵循以下四个关键模式：

## 1. 分配（Allocation）

isQ没有专门的ancilla关键字，辅助比特通过全局qbit数组分配。通常将工作比特和辅助比特声明在同一个数组中，用索引区分：

```isq
import std;
qbit q[5]; // q[0..2]为工作比特，q[3..4]为辅助比特
```

也可以分开声明多个数组：

```isq
import std;
qbit data[3];
qbit anc[2];
```

## 2. 使用（Usage）

辅助比特通常用于：
- **多比特控制的分解**：利用Toffoli门将多控门分解为双控门
- **临时存储计算结果**：存储中间布尔函数值

示例——用ancilla实现4比特受控门：

```isq
// 将CC..C(U)分解：先计算控制条件到ancilla，再单控U
Toffoli(q[0], q[1], anc[0]);
Toffoli(q[2], anc[0], anc[1]);
// 现在用anc[1]单控执行目标门
ctrl @[anc[1]] X(q[3]);
```

## 3. 反计算（Uncomputation）

这是最关键的步骤。使用完ancilla后，必须将其恢复到|0⟩状态，否则会引入额外的纠缠和错误。方法是对之前的计算电路取逆：

```isq
// 正向计算
Toffoli(q[0], q[1], anc[0]);
Toffoli(q[2], anc[0], anc[1]);

// 使用ancilla执行操作
ctrl @[anc[1]] X(q[3]);

// 反计算：逆序执行逆门
Toffoli(q[2], anc[0], anc[1]); // Toffoli自逆
Toffoli(q[0], q[1], anc[0]);   // ancilla回到|0⟩
```

也可以利用isQ的`inv`关键字简化反计算（对自定义门有效）：

```isq
inv myComputeGate(q[0], q[1], anc[0]);
```

## 4. 测量与重置模式

模式A：反计算后不测量（干净的ancilla）
- 反计算后ancilla已回到|0⟩，可直接复用
- 适用于级联的量子子程序

模式B：测量辅助比特用于经典反馈

```isq
int r = M(anc[0]);
if (r == 1) {
    X(q[0]); // 基于测量结果的条件操作
}
```

模式C：测量后条件重置

```isq
int r = M(anc[0]);
if (r == 1) {
    X(anc[0]); // 重置ancilla为|0⟩以便复用
}
```

## 关键原则总结

1. **初始化为|0⟩**：辅助比特使用前必须处于|0⟩状态
2. **用完必反计算**：不反计算会导致后续操作中残余纠缠
3. **反计算顺序**：与计算顺序相反（后进先出）
4. **复用节省资源**：反计算干净的ancilla可以被后续操作重复使用
5. **不可测量不可反计算的ancilla**会累积相位错误，影响最终计算结果

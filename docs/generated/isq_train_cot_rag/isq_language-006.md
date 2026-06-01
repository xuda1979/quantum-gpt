# ISQ training COT RAG corpus: isq_language shard 6

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/93

- task_id: `isqExpand/isqd/93`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`, `ctrl_modifier`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `4245`

### Prompt

Write isQ code for the following quantum task: implements a 2-bit quantum decrement circuit. The circuit subtracts 1 from a 2-bit register (q[1] is MSB, q[0] is LSB).

Initialize the register to |10> (decimal 2) by applying X(q[1]).
After decrement, the result should be |01> (decimal 1).

Decrement logic for 2 bits:
- Flip the LSB (q[0]): X(q[0])
- Propagate borrow: flip MSB (q[1]) if q[0] is now 1 (was 0, meaning borrow). Use: `ctrl @[q[0]] X(q[1])` AFTER flipping.

Measure both qubits. Expected: P(|01>) = 1.0.

### Chain-of-thought reasoning

## Circuit Analysis
Initial: q[1]=1, q[0]=0 -> |10> = decimal 2
Decrement:
1. X(q[0]): q[0]: 0->1. State: |11>
2. ctrl @[q[0]] X(q[1]): q[0]=1, fires. q[1]: 1->0. State: |01>
Result: |01> = decimal 1. Correct: 2-1=1.
Measurement: q[0]=1, q[1]=0. Index = 1. P(1) = 1.0.

## isqExpand/isqd/94

- task_id: `isqExpand/isqd/94`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `expert`
- concept_tags: `toffoli_cascade`, `multi_controlled_logic`, `ancilla_usage`, `uncomputation`
- source: `isq_expansion`
- dataset_index: `4389`

### Prompt

Implement the following in isQ: implements a 4-controlled NOT gate (C4NOT) using a Toffoli cascade with ancilla qubits.

Use 4 control qubits q[0..3], 1 target qubit q[4], and 2 ancilla qubits q[5..6].

Initialize all controls to |1> (so the target should flip).

Toffoli cascade:
1. Toffoli(q[0], q[1], q[5]) -- combine first two controls
2. Toffoli(q[2], q[5], q[6]) -- combine q[2] and q[5]
3. Toffoli(q[3], q[6], q[4]) -- final controlled NOT on target
4. Uncompute ancillas in reverse:
   Toffoli(q[2], q[5], q[6])
   Toffoli(q[0], q[1], q[5])

Measure all 7 qubits. Expected: controls=|1111>, target=|1>, ancillas=|00>. P(|1111100>) = 1.0 at index 31.

### Chain-of-thought reasoning

## Circuit Analysis
C4NOT via Toffoli cascade:
1. Toffoli(q[0],q[1],q[5]): both 1 -> q[5] flips to 1
2. Toffoli(q[2],q[5],q[6]): both 1 -> q[6] flips to 1
3. Toffoli(q[3],q[6],q[4]): both 1 -> q[4] flips to 1
4. Uncompute q[6]: flips back to 0
5. Uncompute q[5]: flips back to 0
Final: q[0..3]=1111, q[4]=1, q[5]=0, q[6]=0
Index = 1+2+4+8+16 = 31. P(31) = 1.0.

## isqExpand/isqd/38

- task_id: `isqExpand/isqd/38`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `mid_circuit_measurement`, `isq_syntax_procedures`
- source: `isq_expansion_qa`
- dataset_index: `3657`

### Prompt

isQ中如何实现经典-量子混合模式？具体包括：
1. 如何使用int r = M(q[0])将测量结果保存到经典变量？
2. 如何根据测量结果进行条件操作（if判断）？
3. 如何使用经典计数器（int count）在循环中累加测量结果？
4. print语句的使用场景是什么？
请结合mid-circuit measurement和经典反馈的具体示例说明。

### Chain-of-thought reasoning

## 推理
目标：解释经典-量子混合编程模式。

关键点：
1. int r = M(q)将测量结果赋给经典变量
2. if(r==1)实现条件操作
3. 循环+计数器累加测量结果
4. print用于输出经典值
5. mid-circuit measurement后的量子态已坍缩

### Reference answer

## isQ中的经典-量子混合模式

### 1. 测量结果保存到经典变量
isQ的M()函数返回int类型的测量结果（0或1）：
```isq
int r = M(q[0]);  // r为0或1
```

### 2. 条件操作（经典控制量子门）
```isq
int r = M(q[0]);
if (r == 1) {
    X(q[1]);  // 仅当q[0]测量为1时翻转q[1]
}
```
这是隐形传态协议的核心模式：先测量，再根据结果修正。

### 3. 经典计数器
```isq
int count = 0;
for i in 0:4 {
    int r = M(q[i]);
    if (r == 1) {
        count = count + 1;
    }
}
print count;  // 输出测量到|1>的次数
```

### 4. print语句
- `print r;` 输出经典整数变量
- `print count;` 输出计数结果
- 仅用于调试/输出模式，不影响量子态
- 使用print的任务通常用 `stdout_match` 验证模式

### 完整示例：简单错误检测
```isq
import std;
qbit q[3];

procedure main() {
    // 编码：创建|000>+|111>（GHZ态）
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    // 注入错误
    X(q[1]);
    // 综合征提取
    int s1 = M(q[0]);
    int s2 = M(q[1]);
    // 经典反馈：打印综合征
    print s1;
    print s2;
}
```

### 注意事项
- mid-circuit measurement会坍缩量子态
- 使用print输出的任务需要 `stdout_match` 或 `compile_only` 验证模式
- 含mid-circuit measurement的任务中，被测量的qbit可在局部声明

## isqExpand/isqd/175

- task_id: `isqExpand/isqd/175`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nctrl`, `negative_control`, `X_gate`, `conditional_operations`
- source: `isq_expansion`
- dataset_index: `5531`

### Prompt

I need an isQ program to uses negative control (nctrl) to apply an X gate to q[1] only when q[0] is in state |0>. Use 2 qubits. Since q[0] starts in |0>, the X gate should fire on q[1], producing the state |01>.

### Chain-of-thought reasoning

The task requires using negative control (nctrl) in isQ. The nctrl @[q[0]] X(q[1]) statement applies the X gate to q[1] only when the control qubit q[0] is in state |0>. Both qubits start in |0⟩. Since q[0] is in |0⟩, the negative control condition is satisfied, so X is applied to q[1], flipping it to |1⟩. The final state is |01⟩ (q[0]=0, q[1]=1). The probability distribution over 2 qubits is: P(|00⟩)=0.0, P(|01⟩)=1.0, P(|10⟩)=0.0, P(|11⟩)=0.0.

## isqExpand/isqd/87

- task_id: `isqExpand/isqd/87`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `classical_control`, `mid_circuit_measurement`, `ctrl_modifier`, `feedforward`
- source: `isq_expansion_qa`
- dataset_index: `173`

### Prompt

isQ程序中如何使用布尔条件来控制量子操作？请说明：
1. if语句如何根据测量结果决定后续门操作
2. 复合条件表达式（如 r1 == 1 && r2 == 0）是否被支持
3. 经典条件控制与量子受控门（ctrl）的本质区别
请给出示例代码说明每种用法。

### Chain-of-thought reasoning

## 推理
目标：解释isQ中布尔条件与量子受控门的区别和用法。

关键点：
1. if语句使用int类型测量结果
2. 复合条件通过嵌套if实现
3. 经典条件 = 先测量再决策（坍缩）
4. ctrl = 量子层面条件执行（保持相干性）
5. 应用场景：经典if用于纠错反馈/传态校正，ctrl用于算法逻辑/纠缠

### Reference answer

## isQ中的布尔条件控制

### 1. if语句与测量结果
isQ支持用测量结果作为条件来控制后续操作（feed-forward）：
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    int r = M(q[0]);
    if (r == 1) {
        X(q[1]);
    }
    M(q[1]);
}
```
这里的if是经典条件分支，在测量坍缩后执行。

### 2. 复合条件
isQ支持标准的比较和逻辑运算符：
```isq
int r1 = M(q[0]);
int r2 = M(q[1]);
if (r1 == 1) {
    if (r2 == 0) {
        Z(q[2]);  // 当r1=1且r2=0时执行
    }
}
```
注意：isQ的条件表达式使用嵌套if来实现复合条件判断。

### 3. 经典条件 vs 量子受控门
| 特性 | if (经典条件) | ctrl (量子受控) |
|------|---------------|------------------|
| 触发时机 | 测量后（坍缩） | 未测量（叠加态中） |
| 保持叠加 | 否（坍缩为确定值） | 是（量子并行） |
| 应用场景 | 纠错反馈、隐形传态校正 | 纠缠创建、算法逻辑 |

```isq
// 量子受控：保持叠加
ctrl @[q[0]] X(q[1]);  // 不破坏q[0]的叠加

// 经典条件：坍缩后决策
int r = M(q[0]);  // q[0]坍缩
if (r == 1) { X(q[1]); }  // 基于确定值操作
```

### 关键区别
- 经典if：先测量，再决策。破坏量子叠加。
- ctrl：在量子态上条件执行，保持相干性。
- 选择哪种取决于是否需要保持量子信息。

## isqExpand/isqd/141

- task_id: `isqExpand/isqd/141`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `increment_circuit`, `carry_propagation`, `gate_ordering`, `Toffoli`, `CNOT`
- source: `isq_expansion`
- dataset_index: `1730`

### Prompt

The following isQ code implements a 3-qubit increment circuit (adds 1 to a quantum register). The initial state is an equal superposition of |000⟩, |001⟩, |010⟩, and |011⟩ (decimal 0–3). After incrementing, the expected states are |001⟩, |010⟩, |011⟩, and |100⟩ (decimal 1–4). However, the carry-propagation gates are applied in the wrong order, causing incorrect results. Fix the gate ordering so the circuit performs a correct increment.

### Chain-of-thought reasoning

An increment circuit adds 1 to a multi-qubit register. The key principle is that carry propagation must be evaluated BEFORE flipping lower bits. The correct order is: (1) Toffoli(q[0],q[1],q[2]) to propagate carry to the MSB when both lower bits are 1, (2) CNOT(q[0],q[1]) to propagate carry to bit 1 when bit 0 is 1, (3) X(q[0]) to flip the LSB. The buggy code flips q[0] first with X, which changes its value before the CNOT and Toffoli gates can read the original state. This causes every carry decision to be based on the POST-flip value of q[0], producing wrong results. For example, on |000⟩ the buggy circuit produces |111⟩ instead of |001⟩. With the equal superposition of |000⟩ through |011⟩ (from H on q[0] and q[1]), the correct increment maps each to the next integer: |000⟩→|001⟩, |001⟩→|010⟩, |010⟩→|011⟩, |011⟩→|100⟩, giving equal 0.25 probability at indices 1, 2, 3, and 4.

## isqExpand/isqd/92

- task_id: `isqExpand/isqd/92`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `mid_circuit_measurement`, `classical_control`, `for_loop`, `feedforward`
- source: `isq_expansion`
- dataset_index: `135`

### Prompt

帮我写一个isQ程序：implements a repeat-until-success pattern.

The program should use a for loop with a maximum of 10 iterations. In each iteration:
1. If a flag variable `done` is still 0:
   a. Allocate a local qubit `anc`
   b. Apply H to `anc`
   c. Measure `anc` into `int r`
   d. Print r
   e. If r == 1, set `done = 1`

This demonstrates mid-circuit measurement with classical feedback in a loop. Use local qubits (compile_only validation).

### Chain-of-thought reasoning

## Design
Repeat-until-success: for loop (max 10 iterations) as bounded retry. Each iteration: allocate local qubit, H, measure. If result=1, set done flag. Classical variable `done` guards iterations (no break in isQ). Output is nondeterministic, compile_only is appropriate.

## isqExpand/isqd/88

- task_id: `isqExpand/isqd/88`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `global_phase`, `phase_manipulation`, `isq_syntax`, `deriving_gate`
- source: `isq_expansion_qa`
- dataset_index: `5528`

### Prompt

isQ中的GPhase门是什么？请说明：
1. GPhase(theta)的数学定义和物理意义
2. GPhase门与普通量子门的区别（它没有qbit参数）
3. GPhase在deriving gate过程中的典型用法（如将Z门转换为controlled-Z的等价形式）
4. 全局相位对测量结果的影响
请给出代码示例。

### Chain-of-thought reasoning

## 推理
目标：解释GPhase门的定义、语法特殊性和应用。

关键点：
1. GPhase(theta) = e^{i*theta}，全局相位因子
2. 唯一没有qbit参数的门
3. 全局相位不影响单系统测量概率
4. 在ctrl上下文中，全局相位变为相对相位（可观测）
5. 典型用法：QFT中的R门，ctrl GPhase(phase, q)
6. deriving gate中用于补偿相位

### Reference answer

## isQ中的GPhase门

### 1. 数学定义
GPhase(theta) = e^{i*theta}，即全局相位因子。它对整个量子态乘以一个复数相位：
|psi> -> e^{i*theta} |psi>

### 2. 与普通门的区别
GPhase是isQ中唯一没有qbit参数的门：
```isq
GPhase(3.14159265358979);  // 直接调用，无qbit参数
```
普通门需要作用在具体的qbit上：`H(q[0]);`

### 3. 在deriving gate中的用法
GPhase常用于补偿全局相位，使过程定义的门具有正确的酋矩阵：
```isq
import std;

// U1 = Z门 + 全局相位pi
// Z = diag(1, -1), GPhase(pi) = e^{i*pi} = -1
// U1 = -1 * diag(1, -1) = diag(-1, 1)
procedure U1(qbit q) {
    Z(q);
    GPhase(3.14159265358979);
} deriving gate
```
当对U1使用ctrl修饰符时，全局相位会转化为相对相位，产生可观测的效果。

### 4. 全局相位与测量
全局相位不影响单独量子系统的测量概率：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    GPhase(1.5707963267949);  // pi/2相位
    M(q[0]);
    // 测量结果不受影响：P(|0>)=0.5, P(|1>)=0.5
}
```
但是，当GPhase出现在受控过程中时，全局相位会变成相对相位，影响干涉和测量结果。

### 关键应用
- QFT中的controlled-R门：`ctrl GPhase(phase, q)` 实现受控相位旋转
- 量子相位估计中的受控酋算子构造
- 精确匹配数学定义中的全局相位

## isqExpand/isqd/65

- task_id: `isqExpand/isqd/65`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `output_prediction`, `duplicate_measurement`, `measurement_order`, `probs_mode`, `common_error`
- source: `isq_expansion`
- dataset_index: `2063`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    M(q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
X(q[0]): q[0]=|1>, q[1]=|0>.

Three M() calls -> 2^3=8 probability values.
M1: q[0] -> always 1
M2: q[0] again -> always 1 (same qubit, already collapsed)
M3: q[1] -> always 0

Bitstring (M1=MSB): 110 = index 6.
All probability at index 6: [0,0,0,0,0,0,1.0,0].

### Reference answer

{'predicted_probs': {'000': 0.0, '001': 0.0, '010': 0.0, '011': 0.0, '100': 0.0, '101': 0.0, '110': 1.0, '111': 0.0}, 'explanation': "Step-by-step:\n1. X(q[0]): q[0] = |1>, q[1] = |0>\n2. First M(q[0]): measures q[0], always gets 1 (bit 0 in output = 1)\n3. Second M(q[0]): measures q[0] again, always gets 1 (bit 1 in output = 1)\n4. M(q[1]): measures q[1], always gets 0 (bit 2 in output = 0)\n\n--probs outputs 2^3=8 values (3 measurement calls).\nOutput bit order: first-M is highest bit.\nBitstring: M1=1, M2=1, M3=0 -> '110' = index 6.\nDistribution: [0,0,0,0,0,0,1.0,0]\n\nThis demonstrates why duplicate measurement is a bug: it inflates the output dimension and creates misleading probability distributions."}

## isqExpand/isqd/57

- task_id: `isqExpand/isqd/57`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `rotation_gate`, `radians_degrees`, `rz_gate`, `wrong_parameter`, `numerical_error`
- source: `isq_expansion`
- dataset_index: `5111`

### Prompt

Fix the bug in this quantum program:

```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    Rz(90, q[0]);  // Bug: should be pi/2 radians, not 90 degrees
    X(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
isQ rotation gates (Rx, Ry, Rz) take angles in radians.
Buggy: Rz(90, q[0]) uses 90 (degrees). The correct value is pi/2 ~ 1.5708.

Circuit trace (with correct angle):
1. X(q[0]): |0> -> |1>
2. Rz(pi/2, q[0]): |1> -> e^{i*pi/4}|1> (global phase on |1>)
3. X(q[0]): |1> -> |0> (with global phase)
Measurement: P(|0>)=1.0 regardless of Rz angle (Rz only adds phase).

Note: The measurement result is the same for any Rz angle in this circuit, but using the correct radian value is essential for circuits where the phase matters (e.g., before interference).

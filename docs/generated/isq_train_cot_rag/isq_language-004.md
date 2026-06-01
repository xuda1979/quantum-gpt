# ISQ training COT RAG corpus: isq_language shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/6

- task_id: `isqExpand/isqd/6`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `defgate`, `custom_gate`, `swap_matrix`, `unitary_definition`
- source: `isq_expansion`
- dataset_index: `202`

### Prompt

Help me write isQ code that uses defgate to define a custom SWAP gate from its unitary matrix, then applies it.

isQ has no native SWAP gate, but you can define one using defgate with the SWAP matrix:
  [[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]]

Note: In isQ defgate syntax, matrix rows are separated by semicolons and elements by commas.

In main(), prepare |01> (apply X to q[1]), apply the custom SWAP gate, and measure. After swapping, the state should be |10> with probability 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: Define a SWAP gate via defgate and apply it.

1. defgate mySWAP with the standard 4x4 SWAP matrix
2. X(q[1]): prepare |01> (q[0]=0, q[1]=1)
3. mySWAP(q[0], q[1]): swaps states -> q[0]=1, q[1]=0
4. Final state: |10>
5. Index = q[0]*2 + q[1] = 1*2 + 0 = 2

Expected: P(|10>) = 1.0 at index 2

## isqExpand/isqd/139

- task_id: `isqExpand/isqd/139`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `decrement_circuit`, `inverse_operations`, `cnot_gate`, `circuit_reversal`, `arithmetic_circuits`
- source: `isq_expansion`
- dataset_index: `2480`

### Prompt

Write an isQ program that a quantum decrement circuit for 2 qubits (the inverse of a 2-qubit increment). The 2-qubit increment circuit is: CNOT(q[0], q[1]) followed by X(q[0]). The decrement reverses this. Prepare the initial state |10⟩ (decimal 2) and apply the decrement to verify it produces |01⟩ (decimal 1). Output the probabilities of all computational basis states.

### Chain-of-thought reasoning

A 2-qubit increment circuit increments a binary counter stored in q[0] (LSB) and q[1] (MSB). The increment maps |00⟩→|01⟩, |01⟩→|10⟩, |10⟩→|11⟩, |11⟩→|00⟩. The standard increment is: CNOT(q[0],q[1]) then X(q[0]). To verify: |00⟩: CNOT→|00⟩, X(q0)→|01⟩ ✓. |01⟩: CNOT→|11⟩, X(q0)→|10⟩ ✓. |10⟩: CNOT→|10⟩, X(q0)→|11⟩ ✓. |11⟩: CNOT→|01⟩, X(q0)→|00⟩ ✓. The decrement is the inverse. Since both CNOT and X are self-inverse (they equal their own inverse), the inverse circuit simply reverses the gate order: X(q[0]) then CNOT(q[0],q[1]). Verification of decrement: |11⟩(3): X(q0)→|01⟩, CNOT→|11⟩... wait, let me recheck. |11⟩: q[1]=1,q[0]=1. X(q[0]): q[0]=1→0, state|10⟩. CNOT(q[0],q[1]): q[0]=0 so no change, |10⟩(2). Correct, 3-1=2. |10⟩(2): X(q[0]): 0→1, |11⟩. CNOT: q[0]=1 so flip q[1]: 1→0, |01⟩(1). Correct, 2-1=1. |01⟩(1): X(q0):1→0, |00⟩. CNOT: q[0]=0 no change, |00⟩(0). Correct. |00⟩(0): X(q0):0→1, |01⟩. CNOT: q[0]=1 flip q[1]:0→1, |11⟩(3). Correct, 0-1 wraps to 3. Starting from |10⟩(2), after decrement we get |01⟩(1). Expected probabilities: [0.0, 1.0, 0.0, 0.0].

## isqExpand/isqd/34

- task_id: `isqExpand/isqd/34`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nctrl_modifier`, `phase_oracle`, `output_prediction`, `marking_oracle`
- source: `isq_expansion`
- dataset_index: `2865`

### Prompt

Analyze the following isQ program and predict the probability distribution.

Hint: nctrl @[q[1]] Z(q[0]) applies Z to q[0] when q[1]=|0>. The Z gate adds a -1 phase when q[0]=|1>. So the combined effect is: add -1 phase when q[0]=|1> AND q[1]=|0>, i.e., mark |10>.

q[1] starts in |0> throughout (never modified).

### Chain-of-thought reasoning

## Circuit Analysis
1. H(q[0]): q[0]=|+>, q[1]=|0>. State: (|00>+|10>)/sqrt(2)
2. nctrl @[q[1]] Z(q[0]): q[1]=|0> always satisfies nctrl
   - On |00>: Z|0>=|0>, no change
   - On |10>: Z|1>=-|1>, adds -1 phase
   - State: (|00>-|10>)/sqrt(2)
3. = (|0>-|1>)/sqrt(2) ⊗ |0> = |->⊗|0>
4. H(q[0]): |-> -> |1>
5. Final: |10>. Index=2. P(|10>)=1.0.

### Reference answer

{'predicted_probs': {'00': 0.0, '01': 0.0, '10': 1.0, '11': 0.0}, 'explanation': 'Step-by-step:\n1. H(q[0]): q[0] = (|0>+|1>)/sqrt(2), q[1] = |0>\n2. State: (|00>+|10>)/sqrt(2)\n3. mark_10(): nctrl @[q[1]] Z(q[0])\n   - q[1]=|0> satisfies nctrl condition on both components\n   - Z(q[0]) on |00>: q[0]=|0>, Z|0>=|0>. No phase change.\n   - Z(q[0]) on |10>: q[0]=|1>, Z|1>=-|1>. Phase -1 added.\n   - State: (|00>-|10>)/sqrt(2) = (|0>-|1>)/sqrt(2) ⊗ |0> = |->|0>\n4. H(q[0]): H|-> = |1>\n5. Final state: |1>|0> = |10>\n6. Index = 1*2 + 0 = 2\n\nResult: P(|10>) = 1.0 at index 2.\nDistribution: [0.0, 0.0, 1.0, 0.0].'}

## isqExpand/isqd/37

- task_id: `isqExpand/isqd/37`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `entanglement`
- source: `isq_expansion_qa`
- dataset_index: `2664`

### Prompt

isQ中如何声明和使用多维量子比特数组（如qbit grid[2][3]）？多维数组在量子算法中有哪些典型用途？请说明多维数组的声明语法、索引访问方式以及与一维数组的区别。请结合量子网格计算的示例进行说明。

### Chain-of-thought reasoning

## 推理
目标：解释isQ多维量子比特数组的声明和使用。

关键点：
1. qbit grid[M][N]声明二维数组
2. 双下标grid[i][j]访问
3. 可以按行切片传入procedure
4. 适合表达2D拓扑结构

### Reference answer

## isQ中的多维量子比特数组

### 声明语法
isQ支持多维量子比特数组，如二维网格：
```isq
qbit grid[2][3];  // 2行3列，共6个量子比特
```

### 索引访问
通过双下标访问具体量子比特：
```isq
H(grid[0][0]);            // 第0行第0列
CNOT(grid[0][1], grid[1][1]);  // 从第0行第1列控制到第1行第1列
```

### 与一维数组的区别
- 一维 `qbit q[6]` 是平坦线性排列
- 二维 `qbit grid[2][3]` 具有行列结构，能直观映射2D量子拓扑
- 多维数组每行可以作为子数组传入procedure

### 典型用途
1. **量子纠错码**：表面码中qubit按2D网格排列
2. **量子图像处理**：像素映射到二维量子寄存器
3. **格子模型模拟**：物理格点映射到量子比特

### 完整示例
```isq
import std;
qbit grid[2][3];

procedure main() {
    // 对第一行所有比特施加H门
    for j in 0:3 {
        H(grid[0][j]);
    }
    // 列方向纠缠：每列的上下比特做CNOT
    for j in 0:3 {
        CNOT(grid[0][j], grid[1][j]);
    }
    // 测量所有
    for i in 0:2 {
        for j in 0:3 {
            M(grid[i][j]);
        }
    }
}
```
此程序在每列创建Bell对，结果中每列的上下比特总是相同（00或11）。

### 注意
- 各维度大小必须是编译期常量
- 传入procedure时需逐行传入（如 `grid[0]` 传入 qbit[3] 参数）

## isqExpand/isqd/172

- task_id: `isqExpand/isqd/172`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `control_modifiers`, `CNOT`, `Bell_state`, `syntax_error`
- source: `isq_expansion`
- dataset_index: `4501`

### Prompt

The following isQ code attempts to create a Bell state by applying H to q[0] then a controlled-X gate, but it crashes with an error because the qubit is controlling itself. Fix the code so that q[0] controls X on a different target qubit to produce a valid Bell state.

### Chain-of-thought reasoning

Step 1: Identify the bug — in the buggy code, `ctrl @[q[0]] X(q[0])` uses q[0] as both the control and the target of the gate, which is physically meaningless and causes an isQ runtime error. Step 2: Determine the intent — the programmer wanted to entangle q[0] and q[1] into a Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2. Step 3: Fix — replace the self-controlling `ctrl @[q[0]] X(q[0])` with `CNOT(q[0], q[1])`, where q[0] is the control and q[1] is the target. Step 4: Verify — after H(q[0]), the state is (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2. After CNOT(q[0],q[1]), the state becomes (|00⟩ + |11⟩)/√2, giving probabilities [0.5, 0.0, 0.0, 0.5] for |00⟩, |01⟩, |10⟩, |11⟩ respectively.

## isqExpand/isqd/77

- task_id: `isqExpand/isqd/77`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `phase_oracle`, `ctrl_z`, `phase_kickback`, `interference`
- source: `isq_expansion`
- dataset_index: `3000`

### Prompt

Code this in isQ: implements a phase oracle using `ctrl @[q[0]] Z(q[1])` and demonstrates the phase kickback effect.

The circuit should:
1. Prepare q[1] in state |1> (apply X)
2. Apply H(q[0]) to create superposition on the control qubit
3. Apply the phase oracle: `ctrl @[q[0]] Z(q[1])`
4. Apply H(q[0]) to convert the phase difference back to a measurable state
5. Measure both qubits

Analysis: When q[1]=|1>, ctrl-Z adds a -1 phase to the |1> component of q[0]. This is phase kickback: H|0> = (|0>+|1>)/sqrt(2), after ctrl-Z with target |1>: (|0>-|1>)/sqrt(2) = |->. H|-> = |1>.

Expected: P(|11>) = 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate phase oracle via ctrl-Z with phase kickback.

1. X(q[1]): q[1] = |1>
2. H(q[0]): q[0] = (|0>+|1>)/sqrt(2). State: (|0>+|1>)/sqrt(2) ⊗ |1>
   = (|01>+|11>)/sqrt(2)
3. ctrl @[q[0]] Z(q[1]): q[0]=|1> branch gets Z on q[1].
   Z|1> = -|1>.
   |01>: q[0]=0, no Z -> |01>
   |11>: q[0]=1, Z applied -> -|11>
   State: (|01>-|11>)/sqrt(2) = ((|0>-|1>)/sqrt(2)) ⊗ |1> = |-> ⊗ |1>
4. H(q[0]): H|-> = |1>. State: |1> ⊗ |1> = |11>
5. P(|11>) = 1.0 at index 3.

## isqExpand/isqd/145

- task_id: `isqExpand/isqd/145`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `phase_oracle`, `multi_controlled_gate`, `controlled_Z`, `X_gate`, `quantum_state_marking`, `hadamard_transform`
- source: `isq_expansion`
- dataset_index: `3857`

### Prompt

用isQ实现implements a phase oracle marking the computational basis state |110⟩ with a -1 phase. Use X gates and a multi-controlled Z gate to achieve this. Then apply Hadamard gates on all qubits before and after the oracle to convert the phase kick into measurable probability differences. Use 3 qubits total. The program should start from |000⟩.

### Chain-of-thought reasoning

To mark |110⟩ with a -1 phase using multi-controlled Z (which naturally marks |111⟩), we use X gates to convert |110⟩ to |111⟩ before and after the controlled-Z. Specifically, |110⟩ means q[2]=1, q[1]=1, q[0]=0. Applying X on q[0] flips it, turning |110⟩ into |111⟩. Then ctrl @[q[0],q[1]] Z(q[2]) applies Z to q[2] when q[0]=q[1]=1, which adds -1 phase only when all three qubits are 1. Finally X(q[0]) restores the labeling. To make this verifiable via measurement, we sandwich the oracle between Hadamard layers (H⊗3 before and after). Starting from |000⟩, H⊗3 creates equal superposition. The oracle marks |110⟩ with -1. A second H⊗3 converts the phase kick into amplitude differences. Computing the amplitudes: after oracle, the state is (1/√8)(Σ|x⟩ - 2|110⟩). After the second H⊗3, |000⟩ gets amplitude 6/8 and all others get ±2/8. Probabilities: |000⟩→36/64=0.5625, all others→4/64=0.0625 each. Sum = 36/64 + 7×4/64 = 64/64 = 1.0.

## isqExpand/isqd/148

- task_id: `isqExpand/isqd/148`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `oracle构造`, `多受控门`, `Grover算法`, `比特串标记`, `ctrl语法`, `X-ctrl-Z-X模式`
- source: `qa_pipeline`
- dataset_index: `3445`

### Prompt

在isQ中如何构造一个标记特定比特串（计算基态）的Oracle？请解释X-ctrl-Z-X模式的原理，并给出isQ代码示例。

### Chain-of-thought reasoning

用户询问的是isQ中构造Oracle的经典模式X-ctrl-Z-X。首先需要解释为什么需要这个模式：因为多受控Z门只能标记|11...1⟩态，而实际目标可能是任意比特串。通过X门将目标态中0的位置翻转成1，就把任意目标态映射到了|11...1⟩，然后多受控Z施加-1相位，最后用X门还原。这是标准的相位Oracle构造方法。在isQ中，多受控门通过ctrl @[]语法实现，Z门是内置门。需要给出清晰的isQ代码示例，展示完整的语法。还需要注意isQ没有原生SWAP，但这与本题无关。代码需要以import std;开头，qbit声明在全局作用域，操作放在main过程中。

### Reference answer

在量子算法（如Grover算法）中，Oracle需要给目标比特串对应的计算基态施加一个-1的相位，即实现：|x⟩ → (-1)^{f(x)}|x⟩，其中f(x)=1当且仅当x等于目标比特串。

**X-ctrl-Z-X模式的原理：**

多受控Z门（multi-controlled Z）只对|11...1⟩态施加-1相位。但我们的目标可能是任意比特串，例如|0101⟩。核心思想是：

1. **第一步（X门翻转）**：对目标比特串中值为0的位施加X门。例如目标为|0101⟩，则对第0、2位施加X门，这样|0101⟩被变换为|1111⟩。

2. **第二步（多受控Z）**：对所有qubit施加多受控Z门，此时只有|1111⟩态获得-1相位，恰好对应原始的目标态。

3. **第三步（X门还原）**：重复第一步的X门操作，将状态翻转回原始基，其他态不受影响地还原。

**isQ代码示例——标记|1010⟩：**

```
import std;

qbit q[4];

procedure main() {
    // 假设qubit已初始化为均匀叠加态
    // 目标比特串: |1010⟩（q[3]=1, q[2]=0, q[1]=1, q[0]=0）

    // 第一步：对目标串中为0的位施加X门
    // q[0]=0, q[2]=0，所以翻转这两个
    X(q[0]);
    X(q[2]);

    // 第二步：多受控Z（ctrl @[c1,c2,...] Z(target)）
    // 使|1111⟩获得-1相位
    ctrl @[q[0], q[1], q[2]] Z(q[3]);

    // 第三步：还原X门
    X(q[0]);
    X(q[2]);
}
```

**更通用的写法（用数组指定目标比特串）：**

```
import std;

qbit q[4];

procedure oracle_mark(int target[4]) {
    // 对target[i]==0的位施加X
    for i in 0:4 {
        if (target[i] == 0) {
            X(q[i]);
        }
    }
    // 多受控Z
    ctrl @[q[0], q[1], q[2]] Z(q[3]);
    // 还原X
    for i in 0:4 {
        if (target[i] == 0) {
            X(q[i]);
        }
    }
}

procedure main() {
    // 标记 |1010⟩
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // 直接手动写oracle
    X(q[0]); X(q[2]);
    ctrl @[q[0], q[1], q[2]] Z(q[3]);
    X(q[0]); X(q[2]);
}
```

**注意事项：**
- isQ中`ctrl @[控制qubit列表] Z(目标qubit)`实现多受控Z门。
- Z门等价于Rz(π)（相差一个全局相位），对|1⟩态施加-1因子。
- 多受控Z门只对全部控制位和目标位均为|1⟩时才施加-1相位，这与我们的需求完全吻合。
- X门是自逆的（X·X=I），所以前后两次X操作完美还原。

## isqExpand/isqd/85

- task_id: `isqExpand/isqd/85`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `for_loop`, `hadamard`, `self_inverse`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `2194`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    for i in 0:4 {
        H(q[0]);
    }
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[0]): |00> -> |10>
2. for i in 0:4: applies H(q[0]) 4 times
   H^1: |1> -> |-> = (|0>-|1>)/sqrt(2)
   H^2: |-> -> |1> (H is self-inverse)
   H^3: |1> -> |->
   H^4: |-> -> |1>
   Even number of H applications: q[0] returns to |1>
3. q[1] untouched: |0>
4. Final: |10>. P(|10>)=1.0 at index 2.
Distribution: [0.0, 0.0, 1.0, 0.0]

### Reference answer

{'predicted_probs': {'00': 0.0, '01': 0.0, '10': 1.0, '11': 0.0}, 'explanation': 'Step-by-step:\n1. X(q[0]): q[0] = |1>, q[1] = |0>. State: |10>\n2. for i in 0:4 applies H(q[0]) four times.\n   H^4 = (H^2)^2 = I^2 = I\n   So 4 applications of H return q[0] to |1>.\n3. Final state: |10>\n4. P(|10>) = 1.0 at index 2.\nDistribution: [0.0, 0.0, 1.0, 0.0].'}

## isqExpand/isqd/22

- task_id: `isqExpand/isqd/22`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `for_loop`, `procedure`, `index_arithmetic`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `233`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[4];

procedure flip_even(qbit reg[4]) {
    for i in 0:2 {
        X(reg[i * 2]);
    }
}

procedure main() {
    flip_even(q);
    for i in 0:4 { M(q[i]); }
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. flip_even(q): for i in 0:2 -> i=0,1
   i=0: X(reg[0*2]) = X(q[0]) -> q[0]=1
   i=1: X(reg[1*2]) = X(q[2]) -> q[2]=1
2. State: q[0]=1, q[1]=0, q[2]=1, q[3]=0 = |1010>
3. Index = 1*8 + 0*4 + 1*2 + 0 = 10
4. Distribution: P(|1010>) = 1.0 at index 10

### Reference answer

{'predicted_probs': {'0000': 0.0, '0001': 0.0, '0010': 0.0, '0011': 0.0, '0100': 0.0, '0101': 0.0, '0110': 0.0, '0111': 0.0, '1000': 0.0, '1001': 0.0, '1010': 1.0, '1011': 0.0, '1100': 0.0, '1101': 0.0, '1110': 0.0, '1111': 0.0}, 'explanation': 'Step-by-step:\n1. flip_even applies X to reg[i*2] for i=0,1 -> X(q[0]) and X(q[2])\n2. After flip_even: q[0]=1, q[1]=0, q[2]=1, q[3]=0\n3. State: |1010>\n4. Index = 1*8 + 0*4 + 1*2 + 0*1 = 10\n\nResult: P(|1010>) = 1.0 at index 10.\nFull distribution: all zeros except index 10 = 1.0.'}

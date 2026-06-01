# ISQ training COT RAG corpus: isq_language shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/170

- task_id: `isqExpand/isqd/170`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `cnot_gate`, `bell_state`, `entanglement`, `gate_arguments`
- source: `isq_expansion`
- dataset_index: `2765`

### Prompt

The following isQ program is intended to create a Bell state (|00⟩ + |11⟩)/√2 by applying a Hadamard gate on q[0] followed by a CNOT with q[0] as control and q[1] as target. However, the CNOT arguments are swapped, producing a different entanglement pattern. Fix the CNOT gate so that q[0] is the control and q[1] is the target.

### Chain-of-thought reasoning

The program aims to create the Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2. Step 1: H(q[0]) transforms |00⟩ to (|00⟩ + |10⟩)/√2. Step 2: A correct CNOT(q[0], q[1]) with q[0] as control and q[1] as target flips q[1] when q[0]=1, yielding (|00⟩ + |11⟩)/√2 with probabilities [0.5, 0.0, 0.0, 0.5]. The buggy code uses CNOT(q[1], q[0]) which makes q[1] the control. Since q[1] is always |0⟩, no flip occurs, leaving the state as (|00⟩ + |10⟩)/√2 — an unentangled product state with probabilities [0.5, 0.0, 0.5, 0.0]. The fix swaps the CNOT arguments to CNOT(q[0], q[1]).

## isqExpand/isqd/165

- task_id: `isqExpand/isqd/165`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `for_loop`, `array_indexing`, `hadamard`, `superposition`
- source: `isq_expansion`
- dataset_index: `137`

### Prompt

The following isQ program is intended to apply a Hadamard gate to all N qubits in a 3-qubit register to create an equal superposition state. However, it contains a bug where the for loop range is set to 0:N+1 instead of 0:N, causing an index out of bounds error. Fix the loop range so the program works correctly.

### Chain-of-thought reasoning

The buggy code declares a 3-qubit array q[3] with valid indices 0, 1, and 2. The for loop 'for i in 0:4' iterates i = 0, 1, 2, 3, which accesses q[3] on the last iteration — an out-of-bounds index since the array size is 3. The fix is to change the loop range to 0:3 so it iterates i = 0, 1, 2, applying H to all three qubits. After applying H to all 3 qubits, the state is an equal superposition of all 8 basis states, each with probability 1/8 = 0.125.

## isqExpand/isqd/51

- task_id: `isqExpand/isqd/51`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `import_std`, `global_qbit`, `scope_rules`, `compilation_error`, `runtime_error`, `best_practice`
- source: `isq_expansion_qa`
- dataset_index: `3250`

### Prompt

isQ程序中`import std;`和全局`qbit`声明为什么是必需的？如果省略`import std;`会发生什么错误？如果在procedure内部声明qbit并使用`--probs`模式运行会怎样？请详细解释这两条规则，并给出正确和错误的示例对比。

### Chain-of-thought reasoning

## 推理
目标：解释isQ的两条基本规则——import std和全局qbit。

关键点：
1. import std;提供所有标准门和M()函数
2. 省略import std导致编译时symbol not found错误
3. --probs模式下qbit必须全局声明
4. 局部qbit在procedure返回时被释放，导致运行时错误
5. stdout_match和compile_only模式不受此限制

### Reference answer

## isQ中的import std和全局qbit规则

### 规则一：import std; 是必需的
isQ的所有标准门（H, X, Y, Z, S, T, CNOT, CZ, Toffoli, Rx, Ry, Rz等）和M()测量函数都定义在标准库std中。如果省略`import std;`，编译器将无法识别这些符号。

**错误示例**（缺少import std）：
```isq
qbit q[2];
procedure main() {
    H(q[0]);  // 编译错误：H未定义
    CNOT(q[0], q[1]);  // 编译错误：CNOT未定义
    M(q[0]); M(q[1]);  // 编译错误：M未定义
}
```
编译时会报 `symbol not found` 或类似错误。

**正确示例**：
```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### 规则二：--probs模式下qbit必须全局声明
`--probs`模拟器要求所有被测量的qbit在全局作用域声明。如果在procedure内部声明qbit，它们在procedure返回时会被释放，导致 `Qubit N freed` 运行时错误。

**错误示例**（局部qbit + --probs）：
```isq
import std;
procedure main() {
    qbit q[2];  // 局部声明
    H(q[0]);
    M(q[0]); M(q[1]);
    // --probs运行时错误：Qubit freed
}
```

**正确示例**：
```isq
import std;
qbit q[2];  // 全局声明
procedure main() {
    H(q[0]);
    M(q[0]); M(q[1]);
}
```

### 总结
1. `import std;` 必须是第一行（在qbit声明之前），否则无法使用任何标准门
2. 使用`--probs`验证时，qbit必须在全局作用域声明
3. `stdout_match`或`compile_only`模式下可以使用局部qbit

## isqExpand/isqd/89

- task_id: `isqExpand/isqd/89`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `isq_syntax_procedures`, `ctrl_modifier`, `deriving_gate`, `controlled_custom_gate`
- source: `isq_expansion_qa`
- dataset_index: `596`

### Prompt

isQ中如何对自定义过程使用ctrl修饰符（受控过程调用）？请说明：
1. `ctrl myProcedure(control_qubit, target_qubit)` 的语法和语义
2. 被控过程必须满足什么条件（deriving gate）
3. ctrl与deriving gate的关系
4. 受控过程调用在量子算法中的典型应用
请给出完整的代码示例。

### Chain-of-thought reasoning

## 推理
目标：解释受控过程调用的语法和约束。

关键点：
1. 语法：ctrl myProc(control, target)
2. 过程必须声明deriving gate
3. deriving gate过程内不能有测量/分支/循环
4. 编译器自动生成受控版本
5. 典型应用：QPE中的ctrl U
6. GPhase在ctrl上下文中从全局相位变为相对相位

### Reference answer

## isQ中的受控过程调用

### 1. 语法
对自定义过程使用ctrl修饰符：
```isq
ctrl myProc(control_qubit, target_qubit);
```
第一个qbit参数为控制比特，后续参数为原过程的参数。当控制比特为|1>时，执行过程内的操作。

### 2. deriving gate要求
被ctrl修饰的过程必须用`deriving gate`声明为门：
```isq
procedure myGate(qbit q) {
    H(q);
    S(q);
} deriving gate  // 必须！否则无法使用ctrl
```
`deriving gate`告诉编译器将该过程视为酋门。过程内不能包含测量、分支、循环等非酋操作。

### 3. ctrl与deriving gate的关系
- `deriving gate`使过程成为可逆（酋）操作
- 只有声明了`deriving gate`的过程才能用ctrl修饰
- 编译器会自动生成受控版本的电路
- 也可以对deriving gate过程使用`inv`（求逆）

### 4. 典型应用：量子相位估计中的受控酋算子
```isq
import std;
qbit q[2];

procedure myX(qbit target) {
    X(target);
} deriving gate

procedure main() {
    H(q[0]);
    ctrl myX(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```
结果：Bell态 (|00>+|11>)/sqrt(2)，P(|00>)=0.5, P(|11>)=0.5。

### 更复杂的示例
```isq
import std;

procedure R(int k, qbit q) {
    double phase = pi / 2 ** (k - 1);
    ctrl GPhase(phase, q);
} deriving gate
```
这是QFT中的受控旋转门，利用ctrl GPhase实现。

## isqExpand/isqd/21

- task_id: `isqExpand/isqd/21`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `procedure`, `parameter_passing`, `qbit_array`, `common_error`
- source: `isq_expansion`
- dataset_index: `955`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;
qbit q[2];

procedure bell_pair(qbit reg[2]) {
    H(reg[0]);
    CNOT(reg[0], reg[1]);
}

procedure main() {
    bell_pair(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The procedure bell_pair expects a single argument of type `qbit reg[2]` (a 2-element array). The buggy call `bell_pair(q[0], q[1])` passes two individual qubits as separate arguments, which is a type mismatch.

Fix: Change `bell_pair(q[0], q[1])` to `bell_pair(q)`. The array `q` has type qbit[2], matching the parameter `qbit reg[2]`.

After fix: Bell state (|00>+|11>)/sqrt(2). P(|00>)=0.5, P(|11>)=0.5.

## isqExpand/isqd/138

- task_id: `isqExpand/isqd/138`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `increment_circuit`, `modular_arithmetic`, `cnot`, `binary_addition`
- source: `isq_expansion`
- dataset_index: `3380`

### Prompt

Write an isQ program that a quantum increment circuit for 2 qubits that adds 1 modulo 4: |00>->|01>, |01>->|10>, |10>->|11>, |11>->|00>. Test it by initializing the register to |10> (by applying X to q[1]), then applying the increment. The final state should be |11>.

### Chain-of-thought reasoning

A 2-qubit increment adds 1 modulo 4. In binary, incrementing means: flip the LSB (q[0]) always, and flip the MSB (q[1]) only when q[0] was 1 (carry propagation). The circuit is: CNOT(q[0], q[1]) first (propagates carry when q[0]=1), then X(q[0]) (flips LSB). Verification: |00> -> CNOT->|00> -> X(0)->|01> ✓; |01> -> CNOT->|11> -> X(0)->|10> ✓; |10> -> CNOT->|10> -> X(0)->|11> ✓; |11> -> CNOT->|01> -> X(0)->|00> ✓. Testing with |10> input: CNOT(0,1) does nothing since q[0]=0, stays |10>. Then X(q[0]) flips q[0] giving |11>. Expected probs: [0,0,0,1] for states |00>,|01>,|10>,|11>.

## isqExpand/isqd/153

- task_id: `isqExpand/isqd/153`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `for_loop`, `measurement`, `classical_feedback`, `hadamard`, `repeat_until_success`
- source: `isq_expansion`
- dataset_index: `1062`

### Prompt

用isQ实现an isQ repeat-until-success circuit: apply H, measure, if 0 then apply H again, using a for loop. Use 1 qubit. The circuit should apply H to q[0], measure it, and if the result is 0, apply H again. Wrap this logic inside a for loop that runs once (for i in 0:1). Print the measurement result.

### Chain-of-thought reasoning

We need a repeat-until-success style circuit using a for loop with mid-circuit measurement and classical feedback. Start with |0⟩. Apply H → |+⟩. Measure: 50% chance of 0, 50% chance of 1. If result is 0 (qubit collapsed to |0⟩), apply H again → |+⟩. If result is 1 (qubit in |1⟩), do nothing. After the conditional: 50% of the time qubit is |+⟩ (from the 0→H path), 50% of the time qubit is |1⟩ (from the 1 path). Final measurement probabilities: P(0) = 0.5 × 0.5 = 0.25 (only from |+⟩ branch measuring 0), P(1) = 0.5 × 0.5 + 0.5 = 0.75 (from |+⟩ branch measuring 1 plus the entire |1⟩ branch). The for loop iterates once (0:1), wrapping the H-measure-conditional-H logic.

## isqExpand/isqd/155

- task_id: `isqExpand/isqd/155`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `mid-circuit measurement`, `classical feedback`, `quantum error correction`, `conditional gate`, `syndrome measurement`
- source: `isq_expansion_qa`
- dataset_index: `352`

### Prompt

isQ中如何实现量子纠错的实时反馈？请解释mid-circuit measurement + if语句的模式，并给出一个具体的代码示例说明其工作原理。

### Chain-of-thought reasoning

首先分析问题核心：量子纠错的实时反馈需要两个能力——(1)在量子线路执行中间进行测量（而非末端测量），(2)根据测量结果条件性地执行量子门。在isQ中，M(q[i])可以赋值给经典int变量，这是mid-circuit measurement的关键。然后if语句可以基于该经典变量控制后续量子操作。这构成了feed-forward机制。接着我设计一个简化的bit-flip code示例，用3个数据qubit和2个ancilla做syndrome测量，然后根据syndrome结果用if嵌套判断哪个比特出错并施加X纠正。这样完整展示了mid-circuit measurement + if反馈的模式。

### Reference answer

在isQ中，量子纠错的实时反馈通过「中途测量（mid-circuit measurement）+ 经典条件判断（if语句）」的模式来实现。核心思想是：在量子线路执行过程中，对辅助量子比特进行测量，根据测量结果（0或1）用经典if语句决定是否对数据量子比特施加纠正操作。

具体语法要素：
1. **中途测量**：使用 `int r = M(q[i]);` 将测量结果存储到经典变量r中。注意这里不会终止线路，而是继续执行后续操作。
2. **经典条件分支**：使用 `if (r == 1) { Gate(q[j]); }` 根据测量结果有条件地施加量子门。
3. **辅助比特重置**（如需要）：可以用X门将测量为1的辅助比特翻转回|0⟩以复用。

代码示例（简化版bit-flip纠错）：
```
import std;
qbit q[3];      // q[0]为数据比特，q[1]、q[2]为辅助比特
qbit anc[2];    // 用于syndrome测量

procedure main() {
    // 假设初始态经过可能翻转，需要纠错
    // 第一步：syndrome测量——将错误信息编码到ancilla
    CNOT(q[0], anc[0]);
    CNOT(q[1], anc[0]);
    CNOT(q[0], anc[1]);
    CNOT(q[2], anc[1]);

    // 第二步：测量ancilla获得错误症状
    int s0 = M(anc[0]);
    int s1 = M(anc[1]);

    // 第三步：根据测量结果实时反馈纠错
    if (s0 == 1) {
        if (s1 == 1) {
            X(q[0]);  // 两个syndrome均为1，说明q[0]翻转
        }
        if (s1 == 0) {
            X(q[1]);  // 仅s0=1，说明q[1]翻转
        }
    }
    if (s0 == 0) {
        if (s1 == 1) {
            X(q[2]);  // 仅s1=1，说明q[2]翻转
        }
        // s0=0, s1=0：无错误，不做操作
    }
}
```

关键要点总结：
- `int r = M(q[i])` 获取经典测量结果而不终止程序
- `if (r == 1) { ... }` 实现经典控制的量子操作反馈
- 这是一种前馈（feed-forward）机制，是表面码、Steane码等量子纠错方案在NISQ设备上的核心实现方式
- 实际应用中，还可以通过for循环遍历多个qubit进行批量纠错操作

## isqExpand/isqd/40

- task_id: `isqExpand/isqd/40`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_procedures`, `entanglement`, `superposition`
- source: `isq_expansion`
- dataset_index: `557`

### Prompt

Write isQ code for the following quantum task: defines a reusable procedure `make_bell(qbit a, qbit b)` which creates a Bell pair (|00>+|11>)/sqrt(2) from two qubits initially in |00>. The procedure should apply H to qubit `a` followed by CNOT(a, b).

In `main()`, use a 4-qubit global array and call `make_bell` twice:
- Once for q[0], q[1] (first Bell pair)
- Once for q[2], q[3] (second Bell pair)

Then measure all 4 qubits. The expected probability distribution should have four non-zero outcomes: |0000>, |0011>, |1100>, |1111>, each with probability 0.25.

### Chain-of-thought reasoning

## Reasoning
Goal: Reusable Bell-pair procedure called twice on independent qubit pairs.

1. make_bell(a,b): H(a), CNOT(a,b) -> (|00>+|11>)/sqrt(2)
2. First pair (q[0],q[1]), second pair (q[2],q[3]).
3. Combined state: 1/2 * (|00>+|11>)(|00>+|11>)
   = 1/2 * (|0000> + |0011> + |1100> + |1111>)
4. Indices: |0000>=0, |0011>=3, |1100>=12, |1111>=15.
5. Each with P=0.25.

## isqExpand/isqd/35

- task_id: `isqExpand/isqd/35`
- task_type: `output_prediction`
- category: `isq_language`
- difficulty: `expert`
- concept_tags: `x_toffoli_x_pattern`, `multi_control`, `phase_oracle`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `4550`

### Prompt

Analyze the following isQ program and predict the probability distribution.

Hint: The oracle uses the X-ctrl-X pattern. q[2] is the bit that equals 0 in the target |110?>, so X is applied before and after the multi-controlled gate. The ctrl gate has 3 controls (q[0], q[1], q[2]) and applies Z to q[3]. The circuit prepares q[0]=|1>, q[1]=|1>, q[2]=|0>, q[3]=|+>.

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[0])=|1>, X(q[1])=|1>, q[2]=|0>
2. H(q[3])=|+>
3. State: |110>(|0>+|1>)/sqrt(2) = (|1100>+|1101>)/sqrt(2)
4. Oracle:
   - X(q[2]): flip to |1>. Now all of q[0..2] are |1>.
   - ctrl @[q[0],q[1],q[2]] Z(q[3]): all controls |1>, Z applied to q[3]
   - Z on |0>=|0> (no change), Z on |1>=-|1> (phase flip)
   - State: (|1110>-|1111>)/sqrt(2)
   - X(q[2]): restore to |0>
   - State: (|1100>-|1101>)/sqrt(2) = |110>|->
5. H(q[3]): |-> -> |1>
6. Final: |1101>. Index = 8+4+0+1 = 13. P=1.0.

### Reference answer

{'predicted_probs': {'0000': 0.0, '0001': 0.0, '0010': 0.0, '0011': 0.0, '0100': 0.0, '0101': 0.0, '0110': 0.0, '0111': 0.0, '1000': 0.0, '1001': 0.0, '1010': 0.0, '1011': 0.0, '1100': 0.0, '1101': 1.0, '1110': 0.0, '1111': 0.0}, 'explanation': 'Step-by-step:\n1. X(q[0]), X(q[1]): q[0]=|1>, q[1]=|1>, q[2]=|0>, q[3]=|0>\n2. H(q[3]): q[3]=(|0>+|1>)/sqrt(2)\n3. State: |110>(|0>+|1>)/sqrt(2) = (|1100>+|1101>)/sqrt(2)\n4. oracle_mark_110():\n   a. X(q[2]): q[2] flips 0->1. State becomes (|1110>+|1111>)/sqrt(2)\n   b. ctrl @[q[0],q[1],q[2]] Z(q[3]): all 3 controls are |1>\n      - On |1110>: q[3]=|0>, Z|0>=|0>. No change.\n      - On |1111>: q[3]=|1>, Z|1>=-|1>. Phase flip.\n      - State: (|1110>-|1111>)/sqrt(2)\n   c. X(q[2]): q[2] flips back 1->0. State: (|1100>-|1101>)/sqrt(2)\n5. = |110>(|0>-|1>)/sqrt(2) = |110>|->\n6. H(q[3]): |-> -> |1>\n7. Final state: |1101>\n\nIndex = 1*8+1*4+0*2+1 = 13.\nP(|1101>) = 1.0 at index 13.\nDistribution: all zeros except index 13 = 1.0.'}

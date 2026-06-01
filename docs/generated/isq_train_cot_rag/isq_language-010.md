# ISQ training COT RAG corpus: isq_language shard 10

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/isqd/95

- task_id: `isqExpand/isqd/95`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `uncomputation`, `ctrl_modifier`, `reversible_computing`
- source: `isq_expansion`
- dataset_index: `779`

### Prompt

Write an isQ program that demonstrates proper ancilla management: allocate, use, and uncompute.

The program should:
1. Use q[0] as data, q[1] as ancilla, q[2] as target.
2. Apply X(q[0]) to set q[0] = |1>.
3. Ancilla pattern:
   a. CNOT(q[0], q[1]) -- copy q[0] into ancilla
   b. ctrl @[q[1]] X(q[2]) -- use ancilla to control target
   c. CNOT(q[0], q[1]) -- uncompute ancilla back to |0>
4. Measure all three qubits.

Expected: q[0]=|1>, q[1]=|0> (uncomputed), q[2]=|1>. P(|101>) = 1.0 at index 5.

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[0]): q[0]=1
2. CNOT(q[0], q[1]): q[0]=1 -> q[1] flips to 1
3. ctrl @[q[1]] X(q[2]): q[1]=1 -> q[2] flips to 1
4. CNOT(q[0], q[1]): q[0]=1 -> q[1] flips back to 0
Final: q[0]=1, q[1]=0, q[2]=1 = |101>. Index = 1+0+4 = 5. P(5) = 1.0.

## isqExpand/isqd/1

- task_id: `isqExpand/isqd/1`
- task_type: `qa_concept`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nctrl_modifier`, `inv_modifier`, `negative_control`, `adjoint`, `isq_syntax`
- source: `isq_expansion_qa`
- dataset_index: `3793`

### Prompt

isQ中的nctrl和inv修饰符各有什么作用？nctrl与ctrl的区别是什么？inv修饰符在电路设计中有哪些典型应用场景？请结合示例说明。

### Chain-of-thought reasoning

## 推理
目标：解释nctrl（负控制）和inv（逆/伴随）修饰符。

关键点：
1. nctrl在控制比特为|0>时触发，与ctrl相反
2. nctrl可以和ctrl混合使用
3. inv对门取共轭转置
4. inv的应用：相位补偿、uncomputation、QFT逆变换
5. inv可以作用于deriving gate标记的过程

### Reference answer

## nctrl和inv修饰符

### nctrl修饰符
nctrl是"negative control"的缩写，当控制比特为|0>时（而非|1>）才执行目标门操作。

语法：
```isq
nctrl @[q[0]] X(q[1]);  // 当q[0]=|0>时翻转q[1]
```

#### ctrl vs nctrl对比
| 修饰符 | 控制条件 | 示例 |
|--------|----------|------|
| ctrl | 控制比特=|1> | ctrl @[q[0]] X(q[1]) |
| nctrl | 控制比特=|0> | nctrl @[q[0]] X(q[1]) |

#### nctrl示例：当q[0]=|0>时执行
```isq
import std;
qbit q[2];
procedure main() {
    // q[0]初始为|0>，nctrl条件满足
    nctrl @[q[0]] X(q[1]);  // q[1]被翻转为|1>
    M(q[0]); M(q[1]);
    // 结果：|01> 概率1.0
}
```

#### 组合使用：nctrl + ctrl
可以混合正控制和负控制来精确选择计算基态：
```isq
nctrl @[q[0]] ctrl @[q[1]] X(q[2]);
// 当q[0]=|0>且q[1]=|1>时翻转q[2]
```

### inv修饰符
inv对门取共轭转置（伴随/逆），即U -> U†。

常见用法：
```isq
inv S(q[0]);   // S†门
inv T(q[0]);   // T†门
```

#### 典型应用场景
1. **相位补偿**：CY门分解中用inv S
   ```isq
   inv S(t); CNOT(c, t); S(t);  // CY门
   ```
2. **电路反转（uncomputation）**：清理辅助比特
3. **QFT逆变换**：用inv对整个QFT取逆
4. **与ctrl组合**：ctrl @[q[0]] inv S(q[1])

#### inv与deriving gate
对标记为deriving gate的自定义过程也可以使用inv：
```isq
procedure my_op(qbit a) {
    S(a); T(a);
} deriving gate

procedure main() {
    qbit q[1];
    my_op(q[0]);      // 正向
    inv my_op(q[0]);  // 逆向：先inv T再inv S
}
```

## isqExpand/isqd/3

- task_id: `isqExpand/isqd/3`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `nctrl_modifier`, `negative_control`
- source: `isq_expansion`
- dataset_index: `519`

### Prompt

帮我写一个isQ程序：uses nctrl (negative control) to flip q[1] when q[0] is in state |0>.

Start with both qubits in |00> (default). Apply nctrl @[q[0]] X(q[1]), which flips q[1] because q[0] is |0> (the negative control condition is met). Measure both qubits.

The result should be |01> with probability 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate nctrl (negative control).

1. Initial state: |00>
2. nctrl @[q[0]] X(q[1]): q[0] is |0>, satisfies nctrl condition, so X applied to q[1]
3. q[1] flips from |0> to |1>
4. Final state: |01> (q[0]=0, q[1]=1)
5. Index = q[0]*2 + q[1] = 0 + 1 = 1

Expected: P(|01>) = 1.0 at index 1

## isqExpand/isqd/168

- task_id: `isqExpand/isqd/168`
- task_type: `bug_fix`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `qbit_scope`, `global_declaration`, `bell_state`, `probs_mode`
- source: `isq_expansion`
- dataset_index: `3542`

### Prompt

The following isQ program is intended to create a Bell state (|00⟩ + |11⟩)/√2, but it triggers a 'Qubit freed' error when compiled with the --probs flag. Identify the issue and fix the code so it compiles and runs correctly.

### Chain-of-thought reasoning

Step 1: Identify the bug. The isQ language requires qubit arrays to be declared at global scope when using the --probs flag. The buggy code declares 'qbit q[2];' inside the procedure main(), which makes it a local allocation. Local qubit variables are freed when the procedure exits, and the --probs simulation mode cannot track them properly, resulting in a 'Qubit freed' error.

Step 2: Determine the fix. Move the qubit declaration 'qbit q[2];' out of the procedure body to global scope, before the procedure definition.

Step 3: Verify the quantum logic. After applying H(q[0]), qubit 0 is in state (|0⟩ + |1⟩)/√2. Then CNOT(q[0], q[1]) entangles the two qubits, producing the Bell state (|00⟩ + |11⟩)/√2.

Step 4: Compute expected probabilities. For the Bell state (|00⟩ + |11⟩)/√2, the measurement probabilities are: P(|00⟩) = |1/√2|² = 0.5, P(|01⟩) = 0, P(|10⟩) = 0, P(|11⟩) = |1/√2|² = 0.5. The expected_probs array is [0.5, 0.0, 0.0, 0.5], which sums to 1.0 and has exactly 2² = 4 elements.

## isqExpand/isqd/30

- task_id: `isqExpand/isqd/30`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `nctrl_modifier`, `phase_oracle`, `marking_oracle`, `multi_control`
- source: `isq_expansion`
- dataset_index: `3106`

### Prompt

Write isQ code for the following quantum task: implements a multi-controlled phase oracle to mark the state |110> with a (-1) phase, using nctrl for the zero-bit position.

The state |110> has q[0]=1, q[1]=1, q[2]=0. Instead of the X-Toffoli-X pattern, use nctrl on q[2] (which is 0 in the target) combined with ctrl on q[0] and q[1]:

nctrl ctrl Z(q[2], q[0], q[1]);

This applies Z to q[1] only when q[0]=|1>, q[1]=|1> (Z eigenvalue), and q[2]=|0>. The effect is a (-1) phase on |110>.

To verify: prepare (|110>+|111>)/sqrt(2) by setting q[0]=|1>, q[1]=|1>, and H(q[2]).
- Oracle marks |110>: (|110>+|111>)/sqrt(2) -> (-|110>+|111>)/sqrt(2)
  = |11>(−|0>+|1>)/sqrt(2)
- Apply H(q[2]): |11> * H(−|0>+|1>)/sqrt(2) = |11>|1> = |111>
  Wait: H(-|0>+|1>)/sqrt(2) = H * (-(|0>-|1>)/sqrt(2)) = -H|-> = -|1>. So we get -|111>.
  Probability of |111> is still 1.0. Global phase unobservable.
- Measure: |111> with probability 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: Mark |110> using nctrl on the zero-position.

Oracle: nctrl @[q[2]] ctrl @[q[0]] Z(q[1])
- Activates when q[2]=|0> (nctrl), q[0]=|1> (ctrl)
- Applies Z to q[1]: if q[1]=|1>, adds -1 phase
- Net: -1 phase exactly when q[0]=1, q[1]=1, q[2]=0 = |110>

Verification:
1. X(q[0]), X(q[1]): q[0]=|1>, q[1]=|1>
2. H(q[2]): q[2]=(|0>+|1>)/sqrt(2)
3. State: |11>(|0>+|1>)/sqrt(2) = (|110>+|111>)/sqrt(2)
4. Oracle: |110> gets -1 phase -> (-|110>+|111>)/sqrt(2)
   = |11>(-|0>+|1>)/sqrt(2)
5. H(q[2]): H(-|0>+|1>)/sqrt(2) = -H|-> = -|1>
6. Final: -|111>, global phase -1 unobservable
7. P(|111>) = 1.0. Index = 7.

## isqExpand/isqd/128

- task_id: `isqExpand/isqd/128`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `difficult`
- concept_tags: `deriving_gate`, `swap_gate`, `custom_gate_definition`, `unitary_matrix`
- source: `isq_expansion`
- dataset_index: `885`

### Prompt

Code this in isQ: using deriving gate to define a SWAP gate as a 4x4 matrix and apply it to swap |01> to |10>.

### Chain-of-thought reasoning

The SWAP gate swaps two qubits and has the 4x4 unitary matrix: [[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]]. In isQ, we use 'deriving gate' to define a custom gate from its matrix. We declare 2 global qubits q[2]. To prepare |01> (q[0]=0, q[1]=1), we apply X to q[1]. Then we apply myswap(q[0], q[1]). The SWAP gate transforms |01> to |10>, meaning q[0]=1, q[1]=0. For 2 measured qubits, |10> corresponds to index 2 (binary), so expected_probs = [0.0, 0.0, 1.0, 0.0].

## isqExpand/isqd/16

- task_id: `isqExpand/isqd/16`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `mid_circuit_measurement`, `feedforward`, `error_correction`, `classical_control`
- source: `isq_expansion`
- dataset_index: `3060`

### Prompt

用isQ实现demonstrates mid-circuit measurement and classical feedforward.

Implement a simple quantum error correction step:
1. Prepare q[0] in state |1> (apply X).
2. Copy q[0] to q[1] using CNOT(q[0], q[1]) — now both are |1>.
3. Simulate an X error on q[0] by applying X(q[0]) — now q[0]=|0>, q[1]=|1>.
4. Detect the error: CNOT(q[0], q[1]) maps to q[1] the XOR. Then measure q[1] mid-circuit: `int syndrome = M(q[1]);`
5. If syndrome == 1, correct q[0] by applying X(q[0]).
6. Measure q[0].

After correction, q[0] should be restored to |1>.

Note: This task uses mid-circuit measurement and classical if-statement. Use check_mode stdout_match since mid-circuit measurement is involved.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate mid-circuit measurement + feedforward for error correction.

1. X(q[0]): q[0]=|1>, q[1]=|0>
2. CNOT(q[0],q[1]): q[0]=|1>, q[1]=|1> (copied)
3. X(q[0]): simulate error -> q[0]=|0>, q[1]=|1>
4. CNOT(q[0],q[1]): q[1] = q[0] XOR q[1] = 0 XOR 1 = |1>
5. int syndrome = M(q[1]): syndrome = 1 (error detected)
6. if (syndrome == 1) X(q[0]): correct q[0] back to |1>
7. M(q[0]): should give 1

Using compile_only mode due to mid-circuit measurement.

## isqExpand/isqd/26

- task_id: `isqExpand/isqd/26`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `basic`
- concept_tags: `phase_oracle`, `cz_gate`, `phase_kickback`
- source: `isq_expansion`
- dataset_index: `2335`

### Prompt

Code this in isQ: implements a phase oracle marking the state |11> with a (-1) phase using a CZ gate.

Prepare an equal superposition on 2 qubits by applying H to both. Then apply CZ(q[0], q[1]) to add a (-1) phase to the |11> component. Finally apply H to both qubits again to reveal the phase difference as a probability change, and measure.

The state evolution is:
1. |00> -> (|00>+|01>+|10>+|11>)/2 after H on both
2. -> (|00>+|01>+|10>-|11>)/2 after CZ (phase oracle for |11>)
3. -> After H on both: this becomes |10> with probability 1.0

Hint: H*CZ*H on |00> effectively implements a standard Deutsch-Jozsa style analysis where the phase kickback produces |10>.

Actually, let us compute carefully:
After CZ on (|00>+|01>+|10>+|11>)/2: we get (|00>+|01>+|10>-|11>)/2.
Apply H⊗H:
H|0> = (|0>+|1>)/sqrt(2), H|1> = (|0>-|1>)/sqrt(2).

|00> -> (|0>+|1>)(|0>+|1>)/2 = (|00>+|01>+|10>+|11>)/2
|01> -> (|0>+|1>)(|0>-|1>)/2 = (|00>-|01>+|10>-|11>)/2
|10> -> (|0>-|1>)(|0>+|1>)/2 = (|00>+|01>-|10>-|11>)/2
-|11> -> -(|0>-|1>)(|0>-|1>)/2 = -(|00>-|01>-|10>+|11>)/2

Sum: collect |00>: (1+1+1-1)/4 = 2/4 = 1/2
|01>: (1-1+1+1)/4 = 2/4 = 1/2
|10>: (1+1-1+1)/4 = 2/4 = 1/2
|11>: (1-1-1-1)/4 = -2/4 = -1/2

Wait, that gives equal probabilities 1/4 each. Let me reconsider.

Actually the normalization: initial state (|00>+|01>+|10>+|11>)/2, each amplitude = 1/2.

After CZ: (|00>+|01>+|10>-|11>)/2

H⊗H maps:
|00> -> |++> = (|00>+|01>+|10>+|11>)/2
|01> -> |+-> = (|00>-|01>+|10>-|11>)/2
|10> -> |-+> = (|00>+|01>-|10>-|11>)/2
|11> -> |-->  = (|00>-|01>-|10>+|11>)/2

So (|00>+|01>+|10>-|11>)/2 maps to:
(1/2)(|++> + |+-> + |-+> - |-->)
= (1/2) * [ (|00>+|01>+|10>+|11>) + (|00>-|01>+|10>-|11>) + (|00>+|01>-|10>-|11>) - (|00>-|01>-|10>+|11>) ] / 2

|00> coeff: (1+1+1-1)/4 = 2/4 = 1/2
|01> coeff: (1-1+1+1)/4 = 2/4 = 1/2
|10> coeff: (1+1-1+1)/4 = 2/4 = 1/2
|11> coeff: (1-1-1-1)/4 = -2/4 = -1/2

All have probability 1/4. So H-CZ-H on |00> gives uniform distribution. That is not a useful distinguishing test.

Let me redesign this task to be simpler and correct.

Instead: demonstrate CZ as a phase oracle by showing the phase affects interference. Use a single qubit in superposition with the other in |1>.

Setup: prepare |1+> = |1>(|0>+|1>)/sqrt(2). Apply CZ. The |11> component gets -1: |1>(|0>-|1>)/sqrt(2) = |1>|->. Apply H to q[1]: |1>|1>. Measure: |11>.

Compare to no-CZ case: |1+> -> H on q[1] -> |10>.

### Chain-of-thought reasoning

## Reasoning
Goal: Show CZ as a phase oracle marking |11>.

1. X(q[0]): q[0] = |1>
2. H(q[1]): q[1] = |+> = (|0>+|1>)/sqrt(2)
3. State: |1>(|0>+|1>)/sqrt(2) = (|10>+|11>)/sqrt(2)
4. CZ(q[0], q[1]): flips phase of |11> -> (|10>-|11>)/sqrt(2) = |1>(|0>-|1>)/sqrt(2) = |1>|->
5. H(q[1]): |-> -> |1>
6. Final state: |11>

Index = 1*2+1 = 3. P(|11>) = 1.0.

## isqExpand/isqd/143

- task_id: `isqExpand/isqd/143`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `phase_oracle`, `CZ`, `controlled_gates`, `X_gate`, `phase_kickback`, `grover_building_block`
- source: `isq_expansion`
- dataset_index: `2926`

### Prompt

Create an isQ quantum circuit that implements a phase oracle on 2 qubits which marks the computational basis state |01⟩ with a -1 phase. Use X gates and a multi-controlled Z gate (CZ) to achieve this. Apply Hadamard gates to both qubits first to create a uniform superposition, then apply the oracle. Return the complete isQ program.

### Chain-of-thought reasoning

To mark |01⟩ with a -1 phase using X gates and CZ, I need to transform |01⟩ into |11⟩ before applying CZ (since CZ adds a -1 phase only to |11⟩), then undo the transformation. State |01⟩ has q[0]=|0⟩ and q[1]=|1⟩. Applying X to q[0] flips |0⟩→|1⟩, transforming |01⟩→|11⟩. Now CZ(q[0],q[1]) adds -1 phase to |11⟩ (the original |01⟩). Finally X(q[0]) restores q[0]. The net effect: only |01⟩ gets a -1 phase. Starting from |++⟩ superposition (equal amplitudes 0.5 for all 4 states), the oracle changes |01⟩'s amplitude sign but measurement probabilities remain 0.25 each since probabilities are |amplitude|².

## isqExpand/isqd/91

- task_id: `isqExpand/isqd/91`
- task_type: `code_generation`
- category: `isq_language`
- difficulty: `intermediate`
- concept_tags: `ctrl_modifier`, `isq_syntax_procedures`, `deriving_gate`, `controlled_custom_gate`, `entanglement`
- source: `isq_expansion`
- dataset_index: `3372`

### Prompt

用isQ实现demonstrates controlled procedure calls.

Define a procedure `apply_x(qbit target)` with `deriving gate` that applies X to the target qubit.

In `procedure main()`:
1. Apply H to q[0] to create superposition
2. Use `ctrl apply_x(q[0], q[1])` to conditionally apply X to q[1] controlled by q[0]
3. Measure both qubits

This should produce a Bell state. Expected: P(|00>) = 0.5, P(|11>) = 0.5.

### Chain-of-thought reasoning

## Circuit Analysis
1. H(q[0]): (|0>+|1>)/sqrt(2)
2. ctrl apply_x(q[0], q[1]): when q[0]=|1>, apply X to q[1] = CNOT(q[0], q[1])
   State: (|00>+|11>)/sqrt(2)
3. Bell state: P(|00>)=0.5, P(|11>)=0.5
Key: ctrl can be applied to any procedure declared with deriving gate.

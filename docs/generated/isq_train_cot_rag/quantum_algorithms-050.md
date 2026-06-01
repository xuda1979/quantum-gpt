# ISQ training COT RAG corpus: quantum_algorithms shard 50

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2065

- task_id: `isqTrain/2065`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4123`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CZ(q[0], q[1]);
    CZ(q[1], q[2]);
    H(q[0]); H(q[1]); H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

The user wants me to analyze a quantum circuit written in isQ and predict the probability distribution of measurement outcomes.

The circuit is:
1. Initialize 3 qubits q[0], q[1], q[2] in |000>.
2. Apply H to q[0], H to q[1], H to q[2]. The state becomes |+++> = (1/sqrt(8)) * sum_{x,y,z \in {0,1}} |xyz>.
3. Apply CZ(q[0], q[1]). This applies a Z gate to q[1] if q[0] is |1>.
4. Apply CZ(q[1], q[2]). This applies a Z gate to q[2] if q[1] is |1>.
5. Apply H to q[0], H to q[1], H to q[2].
6. Measure all.

Let's trace the state.
Initial state: |000>.
After H on all 3:
1/sqrt(8) * (|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)

After CZ(q[0], q[1]):
CZ flips the phase of |110> and |111>?
Wait, CZ applies Z to q[1] if q[0] is |1>. So it flips the phase of |1_1_> where the first qubit is 1.
So |100> -> |100>, |101> -> |101>, |110> -> -|110>, |111> -> -|111>.
Wait, Z on q[1] means if q[1] is |1> it gets a -1 phase. So |110> gets -1, |111> gets -1.
Wait! Let's re-read CZ definition.
"CZ applies Z to target when control is |1>"
CZ(control, target) = CZ(q[0], q[1])
control is q[0], target is q[1].
So if q[0] is |1>, Z is applied to q[1].
Z on q[1] multiplies by -1 if q[1] is |1>.
So |100> is unaffected. |110> gets multiplied by -1. |101> unaffected. |111> gets multiplied by -1.
Let's check this:
q[0]=1, q[1]=0 => Z(0) = |0>
q[0]=1, q[1]=1 => Z(1) = -|1>
So |10x> -> |10x>, |11x> -> -|11x>.
Yes, the state is:
1/sqrt(8) * (|000> + |001> + |010> + |011> + |100> + |101> - |110> - |111>)

After CZ(q[1], q[2]):
control is q[1], target is q[2].
If q[1] is |1>, Z is applied to q[2].
This means |_1_1> gets multiplied by -1.
So |010> gets -1, |011> unaffected (Z on q[2] does nothing to |011>? Wait, if q[1]=1, then Z applied to q[2].
If q[2]=0, Z(0)=|0>.
If q[2]=1, Z(1)=-|1>.
So |_11> -> -|_11>, |_10> -> |_10>.
Let's check:
q[1]=1, q[2]=0 => unaffected
q[1]=1, q[2]=1 => multiplied by -1.
So |010> is unaffected, |011> becomes -|011>.
|110> is unaffected, |111> becomes -(-|111>) = |111>.
Let's check:
|010> (q[1]=1, q[2]=0) -> |010>
|011> (q[1]=1, q[2]=1) -> -|011>
|110> (q[1]=1, q[2]=0) -> -|110>
|111> (q[1]=1, q[2]=1) -> -(-|111>) = |111>
So the state is:
1/sqrt(8) * (|000> + |001> + |010> - |011> + |100> + |101> - |110> + |111>)

Now apply H to all 3 qubits.
Since H|x> = (|0> + (-1)^x |1>) / sqrt(2) = |+> if x=0, |-> if x=1.
Or we can just look at the coefficients of |

### Reference answer

{'predicted_probs': {'000': 0.25, '010': 0.25, '101': 0.25, '111': 0.25}, 'explanation': 'Linear graph state (3 qubits) in X basis: 4 equiprobable outcomes.'}

## isqExpand/algo/5

- task_id: `isqExpand/algo/5`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `deutsch_jozsa`, `oracle`, `balanced_function`
- source: `isq_expansion`
- dataset_index: `3492`

### Prompt

Write an isQ program that implementing the Deutsch-Jozsa algorithm for a 2-bit balanced function f(x) = x0 XOR x1 (where x0 is the most significant bit). Use an ancilla qubit initialized to |1> via X gate.

### Chain-of-thought reasoning

## Reasoning
Goal: Deutsch-Jozsa for f(x0,x1) = x0 XOR x1 (balanced function).

Setup: q[0],q[1] = input register, q[2] = ancilla.

1. X(q[2]): prepare ancilla in |1>
2. H on all 3: q[0],q[1] -> |++>, q[2] -> |-> = (|0>-|1>)/sqrt(2)
3. Oracle: f(x) = x0 XOR x1, implemented as CNOT(q[0],q[2]) + CNOT(q[1],q[2])
   This computes |x0,x1>|y XOR f(x)>. With ancilla in |->: |x0,x1>((-1)^f(x))|-> = (-1)^(x0 XOR x1)|x0,x1>|->
4. H on q[0],q[1]: for balanced function, interference gives |11> with certainty (non-zero output = balanced)

Expected: {|11>: 1.0} (measuring only q[0],q[1])

## isqExpand/algo/169

- task_id: `isqExpand/algo/169`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `half_adder`, `toffoli`, `cnot`, `classical_arithmetic`, `measurement`
- source: `isq_expansion`
- dataset_index: `3641`

### Prompt

Create an isQ quantum circuit that an isQ quantum half adder circuit that computes the binary addition of 0+1. Use a Toffoli gate to compute the carry (A AND B) and a CNOT gate to compute the sum (A XOR B). Initialize input qubit A=0 and B=1. Use q[0] for A, q[1] for B (which becomes Sum after CNOT), and q[2] for Carry. Measure all qubits.

### Chain-of-thought reasoning

Step 1: A half adder takes two bits A and B and produces Sum=A XOR B and Carry=A AND B.
Step 2: For 0+1, we set A=0 (q[0] stays |0⟩) and B=1 (apply X to q[1]).
Step 3: Use Toffoli(q[0], q[1], q[2]) to compute Carry = A AND B. Since A=0, Carry=q[2]=0.
Step 4: Use CNOT(q[0], q[1]) so q[1] becomes A XOR B = 0 XOR 1 = 1 (Sum).
Step 5: Final state is |q[0], q[1], q[2]⟩ = |0, 1, 0⟩ = |010⟩ which is decimal index 2.
Step 6: expected_probs array for 3 qubits has 2^3=8 entries, with index 2 having probability 1.0 and all others 0.0.
Step 7: Verification: Sum=1 and Carry=0 correctly represents 0+1=1 with no carry.

## isqQA/quantum_algorithms/91_application_scenario

- task_id: `isqQA/quantum_algorithms/91_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `application_scenario`, `algorithm`, `BV算法的不同隐藏字符串实现`
- source: `qa_pipeline`
- dataset_index: `5292`

### Prompt

Bernstein-Vazirani (BV) 算法在学术界常被视为展示量子并行性的教学范例。然而，在实际的量子硬件研发和前沿应用中，BV算法是否具备真实的实际应用场景与前景？如果要在近量子（NISQ）设备上，利用BV算法来验证硬件对包含特定隐藏字符串$s=1011$的量子线路的执行能力，应该如何使用isQ语言编写这段测试代码？

### Reference answer

<思考>
首先分析BV算法的实际应用场景和前景。BV算法的核心在于利用量子叠加态和干涉现象，仅需一次查询就能提取出隐藏的比特串，而经典算法需要N次。这种指数级加速在工业界的直接应用虽然有限，但在以下场景具有重要价值：
1. 硬件基准测试：由于其线路结构相对简单且对量子态干涉要求高，IBM、谷歌等常使用BV算法来评估量子比特的相干时间、保真度以及门操作的准确性。
2. 量子纠错验证：在引入纠错编码后，BV算法常被用作验证纠错逻辑是否正常工作的标准测试用例。
3. 机器学习与特征映射：在某些量子机器学习模型中，内积计算或汉明距离的提取可以转化为类似BV算法的隐函数查询。
4. 密码学警告：BV算法直接警告了密码学界，任何基于线性函数叠加或特定结构的黑盒密码系统在量子计算面前都是脆弱的。
接下来推导并编写isQ代码。隐藏字符串 s = 1011，长度为4。我们需要5个量子比特（4个输入，1个辅助）。辅助比特初始化为|1>并应用H门使其进入|->态。对于s中为'1'的位置（即第0、1、3位，从右往左或从左往右均可，假设按索引0,1,3为'1'），对相应的输入比特和辅助比特执行CNOT操作。
</思考>

尽管Bernstein-Vazirani (BV) 算法经常作为量子计算入门的教学案例，但它在当今的量子硬件研发和前沿探索中具有不可忽视的实际应用场景与广阔前景：

1. **NISQ时代的硬件基准测试**：BV算法是目前评估量子计算机性能最常用的基准测试算法之一。与随机基准测试（RB）不同，BV算法需要量子硬件具备执行多层量子门并维持量子干涉的能力。通过逐渐增加隐藏字符串的长度，研究人员可以有效评估量子比特的相干时间、串扰以及整体保真度。
2. **量子纠错验证**：在构建容错量子计算机的过程中，BV算法常被用来测试逻辑量子比特和量子纠错码的有效性。它可以验证经过复杂编码后的系统是否仍然能够保持量子算法应有的指数级加速特性。
3. **量子密码学分析**：BV算法是对称密码学中线性逼近的量子推广。它展示了量子计算机在破解具有特定内部结构的黑盒函数时的强大能力，促使后量子密码学在设计时更加关注防范此类量子叠加查询攻击。
4. **量子机器学习中的内积计算**：在某些基于哈密顿量模拟的量子机器学习算法中，特征向量的内积或汉明权重提取可以通过类似于BV算法的量子线路来实现，从而实现数据特征的高效提取。

下面是使用isQ语言实现的BV算法代码，用于在量子设备上验证隐藏字符串 $s = 1011$ 的求解能力：

```isq
import std;

// 声明5个量子比特，其中q[0]到q[3]为输入寄存器，q[4]为辅助比特（输出寄存器）
qbit q[5];

procedure main() {
    // 初始化辅助比特为 |1> 状态
    X(q[4]);
    
    // 对所有量子比特应用Hadamard门，进入叠加态
    // 辅助比特变为 |-> 态，用于存储相位信息
    for i in 0:5 {
        H(q[i]);
    }
    
    // 实现隐藏字符串 s=1011 的 Oracle (酉变换 U_f)
    // f(x) = s 
 x (模2)
    // 对于s中为1的位，执行CNOT门。这里s的索引1, 0, 3为'1'（对应串1011，假设高位在前q[3]=1, q[2]=0, q[1]=1, q[0]=1）
    // 因此对 q[0], q[1], q[3] 与辅助比特 q[4] 执行控制非操作
    CNOT(q[0], q[4]);
    CNOT(q[1], q[4]);
    CNOT(q[3], q[4]);
    
    // 对输入寄存器再次应用Hadamard门，利用干涉现象提取隐藏相位
    for i in 0:4 {
        H(q[i]);
    }
    
    // 测量输入寄存器，理论上将以100%的概率测量出隐藏字符串 '1011'
    for i in 0:4 {
        M(q[i]);
    }
}
```

## isqExpand/algo/123

- task_id: `isqExpand/algo/123`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `interference`
- source: `qa_pipeline`
- dataset_index: `2872`

### Prompt

振幅放大（Amplitude Amplification）是如何推广Grover搜索算法的？请解释振幅放大的一般框架，说明它与Grover搜索的关系，以及为什么初始态不必是均匀叠加态。

### Chain-of-thought reasoning

## 推理
目标：解释振幅放大是Grover的推广。

核心概念：
1. Q = -A S_0 A^{-1} O_chi
2. 在好态/坏态的二维子空间中旋转
3. Grover是A=H^n的特例
4. 复杂度O(1/sqrt(a))

### Reference answer

## 振幅放大：Grover搜索的一般化框架

### 核心思想
Grover搜索是振幅放大的一个特例。

### 一般框架
给定：
- 算法 A：将 |0> 映射到 A|0> = sin(theta)|good> + cos(theta)|bad>
- Oracle O_chi：翻转好态的相位
- 反射算子 S_0 = I - 2|0><0|

振幅放大算子 Q = -A S_0 A^{-1} O_chi

经过 k 次迭代：Q^k A|0> = sin((2k+1)theta)|good> + cos((2k+1)theta)|bad>

### 与Grover的关系
Grover搜索是特例：A = H^{\otimes n}，theta = arcsin(sqrt(M/N))。
振幅放大的推广在于：
1. A 可以是任意量子算法
2. 初始态的好/坏分量比例可以任意

### 为什么初始态不必均匀
Q 在 |good> 和 |bad> 的二维子空间中是旋转。只要初始态有非零的 |good> 分量，旋转就能增大它。

### 复杂度
如果初始成功概率为 a = sin^2(theta)，则需要 O(1/sqrt(a)) 次迭代。

## isqTrain/2019

- task_id: `isqTrain/2019`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1936`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[6];
procedure main() {
    X(q[0]);
    X(q[3]);
    CNOT(q[2], q[4]);
    CNOT(q[3], q[5]);
    M(q[4]);
    M(q[5]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The system starts in the initial state |000000>.
2. `X(q[0])` flips q[0] to |1>, changing the state to |100000>.
3. `X(q[3])` flips q[3] to |1>, changing the state to |100100>.
4. `CNOT(q[2], q[4])` applies an X gate to q[4] if q[2] is |1>. Since q[2] is |0>, q[4] remains |0>. The state is still |100100>.
5. `CNOT(q[3], q[5])` applies an X gate to q[5] if q[3] is |1>. Since q[3] is |1>, q[5] flips to |1>. The state becomes |100110>.
6. The measurements `M(q[4])` and `M(q[5])` target q[4

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'GF(3) multiplication 1*2=2: product register encodes 2. Index 1 has P=1.0.'}

## isqTrain/3471

- task_id: `isqTrain/3471`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3901`

### Prompt

请用isQ语言编写一个量子电路：the YY evolution operator exp(-i*theta*Y_0*Y_1) for theta=pi/6 in isQ.

Decomposition:
1. Basis change: Rx(pi/2) on both qubits (Y -> Z)
2. ZZ evolution: CNOT, Rz(2*theta), CNOT
3. Undo basis change: Rx(-pi/2) on both

Apply to |01>. Declare 2 qubits, measure both.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The goal is to implement the YY evolution operator exp(-i*theta*Y_0*Y_1) for theta=pi/6 and apply it to |01>.

Let me trace through the state evolution:

1. Initial state: |01⟩ (after X on q[1])

2. Basis change: Rx(π/2) on both qubits
   - Rx(π/2) maps Y eigenstates to Z eigenstates
   - Rx(θ)|0⟩ = cos(θ/2)|0⟩ - i*sin(θ/2)|1⟩
   - Rx(π/2)|0⟩ = cos(π/4)|0⟩ - i*sin(π/4)|1⟩ = (|0⟩ - i|1⟩)/√2
   - Rx(π/2)|1⟩ = cos(π/4)|1⟩ - i*sin(π/4)|0⟩ = (|1⟩ - i|0⟩)/√2 = -i(|0⟩ + i|1⟩)/√2
   
   Wait, let me recalculate. Rx(θ) = exp(-iθX/2) = cos(θ/2)I - i*sin(θ/2)X
   Rx(θ)|0⟩ = cos(θ/2)|0⟩ - i*sin(θ/2)|1⟩
   Rx(θ)|1⟩ = -i*sin(θ/2)|0⟩ + cos(θ/2)|1⟩

   For θ = π/2:
   Rx(π/2)|0⟩ = cos(π/4)|0⟩ - i*sin(π/4)|1⟩ = (1-i)/2|0⟩ + ... wait let me be more careful
   
   Rx(π/2)|0⟩ = (|0⟩ - i|1⟩)/√2
   Rx(π/2)|1⟩ = (-i|0⟩ + |1⟩)/√2

   So after Rx(π/2) on both:
   |01⟩ → [(|0⟩ - i|1⟩)/√2] ⊗ [(-i|0⟩ + |1⟩)/√2]
   = (1/2)(|0⟩ - i|1⟩)(-i|0⟩ + |1⟩)
   = (1/2)(-i|00⟩ + |01⟩ + i²|10⟩ - i|11⟩)
   = (1/2)(-i|00⟩ + |01⟩ - |10⟩ - i|11⟩)

3. ZZ evolution via CNOT-Rz(2θ)-CNOT where 2θ = π/3

   CNOT(q[0], q[1])|ab⟩ = |a, a⊕b⟩
   
   CNOT(q[0], q[1]) applied:
   - |00⟩ → |00⟩
   - |01⟩ → |01⟩
   - |10⟩ → |11⟩
   - |11⟩ → |10⟩
   
   State becomes:
   (1/2)(-i|00⟩ + |01⟩ - |11⟩ - i|10⟩)
   
   Rz(π/3) on q[1]: Rz(θ)|0⟩ = e^(-iθ/2)|0⟩, Rz(θ)|1⟩ = e^(iθ/2)|1⟩
   Rz(π/3)|0⟩ = e^(-iπ/6)|0⟩, Rz(π/3)|1⟩ = e^(iπ/6)|1⟩
   
   State becomes:
   (1/2)(-i*e^(-iπ/6)|00⟩ + e^(iπ/6)|01⟩ - e^(iπ/6)|11⟩ - i*e^(-iπ/6)|10⟩)
   
   CNOT(q[0], q[1]) again:
   - |00⟩ → |00⟩
   - |01⟩ → |01⟩
   - |10⟩ → |11⟩
   - |11⟩ → |10⟩
   
   State becomes:
   (1/2)(-i*e^(-iπ/6)|00⟩ + e^(iπ/6)|01⟩ - e^(iπ/6)|10⟩ - i*e^(-iπ/6)|11⟩)

4. Undo basis change: Rx(-π/2) on both

This is getting complex. Let me think about this differently using the structure of the YY operator.

Actually, the decomposition is:
exp(-iθY⊗Y) = (Rx(π/2)⊗Rx(π/2)) exp(-iθZ⊗Z) (Rx(-π/2)⊗Rx(-π/2

## isqTrain/3425

- task_id: `isqTrain/3425`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `isq_syntax_ctrl_nctrl`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2089`

### Prompt

Implement a quantum circuit in isQ: a 2-bit quantum ripple-carry adder in isQ using the CDKM construction.

Compute a + b where a = 10 (binary, i.e., 2) and b = 01 (binary, 1).
Expected result: 11 (binary, 3) with carry_out = 0.

Register layout:
- q[0]=a[0] (LSB of a), q[1]=a[1] (MSB of a)
- q[2]=b[0] (LSB of b), q[3]=b[1] (MSB of b)
- q[4]=carry (ancilla, starts at |0>)

The adder computes b[i] = a[i] + b[i] + carry, propagating carry.
Use full adder sub-circuits chained together.

Declare 5 global qubits, measure all.

### Chain-of-thought reasoning

Let me analyze this CDKM ripple-carry adder circuit carefully.

**Goal:** Implement a 2-bit quantum ripple-carry adder computing a + b where a = 10 (binary, 2) and b = 01 (binary, 1), expecting result 11 (binary, 3) with carry_out = 0.

**Qubit layout:**
- q[0]=a[0]=0 (LSB of a)
- q[1]=a[1]=1 (MSB of a)
- q[2]=b[0]=1 (LSB of b)
- q[3]=b[1]=0 (MSB of b)
- q[4]=carry=0 (ancilla)

**Initial state after X gates:**
- X(q[1]): sets a[1]=1
- X(q[2]): sets b[0]=1
- State: |a0, a1, b0, b1, carry⟩ = |0, 1, 1, 0, 0⟩

**Bit 0: Half adder**
1. `ctrl ctrl X(q[0], q[2], q[4])` — Toffoli gate: if q[0]=1 AND q[2]=1, flip q[4]
   - q[0]=0, so carry stays 0
   - State: |0, 1, 1, 0, 0⟩ (unchanged)

2. `CNOT(q[0], q[2])` — if q[0]=1, flip q[2]
   - q[0]=0, so q[2] unchanged
   - State: |0, 1, 1, 0, 0⟩
   - b[0] = 0 XOR 1 = 1 ✓ (sum bit 0 = 1)

**Bit 1: Full adder with carry**
3. `CNOT(q[4], q[3])` — if carry=1, flip b[1]
   - q[4]=0, so q[3] unchanged
   - State: |0, 1, 1, 0, 0⟩

4. `CNOT(q[1], q[3])` — if a[1]=1, flip b[1]
   - q[1]=1, so q[3] flips: 0→1
   - State: |0, 1, 1, 1, 0⟩

**Final state:** |0, 1, 1, 1, 0⟩

**Measurement order:** M(q[0]), M(q[1]), M(q[2]), M(q[3]), M(q[4])

In --probs mode, earlier measured qubit = higher bit:
- q[0] = bit 4 (MSB)
- q[1] = bit 3
- q[2] = bit 2
- q[3] = bit 1
- q[4] = bit 0 (LSB)

Result: q[0]=0, q[1]=1, q[2]=1, q[3]=1, q[4]=0
Binary (MSB to LSB): 01110 = 14 decimal

Wait, Let me verify the output: {|01110>: 1.0}

01110 in binary:
- Bit 4: 0
- Bit 3: 1
- Bit 2: 1
- Bit 1: 1
- Bit 0: 0

So the state is |01110⟩ where:
- q[0]=0 (bit 4)
- q[1]=1 (bit 3)
- q[2]=1 (bit 2)
- q[3]=1 (bit 1)
- q[4]=0 (bit 0)

This matches |0,1,1,1,0⟩ ✓

Let me verify the computation:
- a = 10 (binary) = 2
- b = 01 (binary) = 1
- a + b = 3 = 11 (binary)

Results:
- b[0] = 1 (sum bit 0) ✓
- b[1] = 1 (sum bit 1) ✓
- carry = 0 ✓

But wait, this circuit seems incomplete for a proper full adder. The CDKM construction for a ripple-carry adder is more involved. Let me check if the simplified circuit actually works...

For bit 0 (half adder):
- a[0]=0, b[0]=1
- Sum = 0 XOR 1 = 1 ✓
- Carry = 0 AND 1 = 0 ✓

For bit 1

## isqTrain/1997

- task_id: `isqTrain/1997`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `ancilla_usage`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1313`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[4];
procedure main() {
    X(q[0]);
    X(q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    Toffoli(q[0], q[1], q[3]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The initial 4-qubit state is |0000>.
2. `X` gates on q[0] and q[1] flip them to |1>, changing the state to |1100>.
3. `CNOT(q[0], q[2])` flips q[2] to |1> (control q[0] is |1>), evolving the state to |1110>.
4. `CNOT(q[1], q[2])` flips q[2] back to |0> (control q[1] is |1>), evolving the state to |1100>.
5. `Toffoli(q[0], q[1], q[3])` flips q[3] to |1> (both controls q[0], q[1] are |1>), resulting in the final state |1101>.
6. Measuring q[2] yields 0, and measuring q[3] yields 1. The earlier measured qubit (q[

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'Half adder 1+1: sum=0, carry=1. Index 1 has P=1.0.'}

## isqQA/quantum_algorithms/123_comparison

- task_id: `isqQA/quantum_algorithms/123_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `comparison`, `algorithm`, `连续时间量子行走`
- source: `qa_pipeline`
- dataset_index: `979`

### Prompt

请对比连续时间量子行走（CTQW）与离散时间量子行走（DTQW）及经典随机行走（CRW）在算法原理和适用场景上的优缺点，并说明连续时间量子行走在物理实现上的特殊性。此外，请使用 isQ 语言实现一个在由两个节点构成的图（线图）上执行连续时间量子行走的示例代码，展示其基于哈密顿量演化的特性。

### Reference answer

连续时间量子行走、离散时间量子行走以及经典随机行走是图论和量子计算领域中用于探索图结构、搜索和分析算法基础的三种重要范式。它们在状态演化机制和适用场景上有着本质的区别。

1. 算法原理对比与优缺点：
经典随机行走（CRW）是基于马尔可夫链的概率转移过程。其状态转移由转移概率矩阵决定，演化过程对应于经典概率的混合。优点是经典实现简单、物理直观；缺点是由于扩散速度受限于中心极限定理，其到达目标节点的混合时间通常呈线性增长，搜索复杂度一般为 $O(N)$。
离散时间量子行走（DTQW）是在由位置空间和“硬币”空间组成的复合希尔伯特空间中进行的。每次迭代包含一次硬币算符（如Hadamard门）的作用和条件移位操作。优点是DTQW具有极强的通用性，可以在任意规则的图结构上定义，且能更直接地映射到基于量子门的通用量子计算机上进行编程；缺点是需要引入额外的硬币自由度，使得量子线路设计较为复杂，且在某些特定图上的分析不如连续模型直观。
连续时间量子行走（CTQW）直接在图的顶点空间进行，无需引入硬币系统。其演化完全由薛定谔方程决定：$i \frac{d}{dt}|\psi\rangle = H|\psi\rangle$，其中哈密顿量 $H$ 通常取图的邻接矩阵或拉普拉斯矩阵。演化过程通过算符 $U(t) = e^{-iHt}$ 来实现。优点是CTQW在数学上与自然界中真实的量子系统演化高度一致，它在某些特定图（如Johnson图、树图）上表现出比DTQW更优异的快速命中时间，能够实现指数级的加速；此外，由于无需硬币操作，在实现基于图的特定搜索算法时逻辑更加简洁。缺点是CTQW并非在所有图上都容易定义，且在通用量子计算机上模拟连续演化必须使用Trotter-Suzuki分解等技术进行离散化，可能引入时间切片误差。

2. 物理实现的特殊性：
在适用场景方面，CRW适用于经典网络路由和统计算法；DTQW非常适合基于门级量子计算机开发的通用量子算法（如通用量子计算模型、元素有异性检测）；而CTQW极其适合那些能够自然映射出系统哈密顿量的物理平台（如超导量子电路、囚禁离子、量子点阵列）。在这些模拟量子系统中，哈密顿量是系统固有的，因此CTQW可以直接通过让系统自然演化一定时间 $t$ 来实现，从而避开构建复杂量子线路的开销。

3. isQ 代码实现：
下面我们使用 isQ 语言实现一个由两个节点（节点0和节点1）相连构成的简单线图上的连续时间量子行走。在这个系统中，图的邻接矩阵即为我们所需的哈密顿量 $H$。
数学推导如下：
两个节点的邻接矩阵为 $A = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix} = X$。
我们取跃迁率 $\gamma = 1$，则演化算符 $U(t) = e^{-iAt} = e^{-iXt}$。
利用泡利矩阵的性质，可得 $e^{-iXt} = \cos(t)I - i\sin(t)X$。这恰好对应于量子计算中的 $R_x(2t)$ 门。
我们设定演化时间 $t = \frac{\pi}{4}$，此时行走者将处于节点0和节点1的完全均匀叠加态（等同于经过一个Hadamard门再加一个全局相位）。

```isq
import std;

// 声明全局量子比特用于模拟概率分布
qbit q[1];

procedure main() {
    // 假设行走者初始处于节点0，即量子态 |0>
    
    // 连续时间量子行走的演化由哈密顿量决定 U = exp(-i H t)
    // 这里图的邻接矩阵为泡利X门矩阵，哈密顿量 H = X
    // 根据推导，exp(-i X t) 等价于绕X轴旋转的 Rx 门（角度为 2t）
    // 设定演化时间 t = pi / 4
    Rx(pi/2, q[0]);
    
    // 测量量子比特，以观察行走者在图上的概率分布
    // 此时测量得到 0（节点0）和 1（节点1）的概率均为 50%
    int res = M(q[0]);
    
    // 打印结果
    print res;
}
```

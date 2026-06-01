# ISQ training COT RAG corpus: quantum_algorithms shard 137

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4100

- task_id: `isqTrain/4100`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2373`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[3];

procedure main() {
    X(q[1]);
    X(q[2]);

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has 3 qubits initialized to |000>.

1. X(q[1]) → |010>
2. X(q[2]) → |011>
3. H(q[0]) → (|011> + |111>)/√2

Now let's track the state through the controlled Rz gates.

4. ctrl Rz(π/2, q[1], q[0]): When q[1]=1, apply Rz(π/2) to q[0]. Since q[1] is always 1 in our superposition, this applies Rz(π/2) to q[0] in both terms.
   Rz(π/2)|0> = e^{-iπ/4}|0>, Rz(π/2)|1> = e^{iπ/4}|1>
   → (e^{-iπ/4}|011> + e^{iπ/4}|111>)/√2

5. ctrl Rz(π/4, q[2], q[0]): When q[2]=1, apply Rz(π/4) to q[0]. Since q[2] is always 1, apply Rz(π/4) to q[0] in both terms.
   Rz(π/4)|0> = e^{-iπ/8}|0>, Rz(π/4)|1> = e^{iπ/8}|1>
   → (e^{-iπ/4}e^{-iπ/8}|011> + e^{iπ/4}e^{iπ/8}|111>)/√2
   = (e^{-i3π/8}|011> + e^{i3π/8}|111>)/√2

6. H(q[1]): Apply H to q[1]. q[1] is always 1 in both terms.
   H|1> = (|0> - |1>)/√2
   → (e^{-i3π/8}(|001> - |011>) + e^{i3π/8}(|101> - |111>))/2

7. ctrl Rz(π/2, q[2], q[1]): When q[2]=1, apply Rz(π/2) to q[1]. Since q[2] is always 1, apply Rz(π/2) to q[1] in all terms.
   For each basis state, if q[1]=0, multiply by e^{-iπ/4}; if q[1]=1, multiply by e^{iπ/4}.
   → (e^{-iπ/4}·e^{-i3π/8}|001> - e^{iπ/4}·e^{-i3π/8}|011> + e^{-iπ/4}·e^{i3π/8}|101> - e^{iπ/4}·e^{i3π/8}|111>)/2
   = (e^{-i5π/8}|001> - e^{-iπ/8}|011> + e^{iπ/8}|101> - e^{i5π/8}|111>)/2

8. H(q[2]): Apply H to q[2]. q[2] is always 1 in all terms.
   H|1> = (|0> - |1>)/√2
   For each term |abc⟩ with c=1: |abc⟩ → (|ab0⟩ - |ab1⟩)/√2
   → (e^{-i5π/8}(|000>-|001>) - e^{-iπ/8}(|010>-|011>) + e^{iπ/8}(|100>-|101>) - e^{i5π/8}(|110>-|111>))/(2√2)

Now for the CNOT sequence: CNOT(q[0], q[2]), CNOT(q[2], q[0]), CNOT(q[0], q[2])

This is a swap (three-CNOT decomposition) of q[0] and q[2]. Let me verify:
- CNOT(0,2): If q[0]=1, flip q[2]
- CNOT(2,0): If q[2]=1, flip q[0]
- CNOT(0,2): If q[0]=1, flip q[2]

Actually, three CNOTs in the pattern control-target, target-control, control-target does implement swap (three-CNOT decomposition).

So after the swap (three-CNOT decomposition), q[0] and q[2] are exchanged. Each basis state |q0 q1 q2⟩ becomes |q2 q1 q0⟩.

So:
|000

### Reference answer

Uniform distribution across 8 states

## isqTrain/3541

- task_id: `isqTrain/3541`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1207`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```
import std;

qbit q[1];

procedure main() {
    X(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a 1-qubit register in the state |0>.
2. An X gate is applied to qubit q[0].
3. The X gate flips the state of the qubit from |0> to |1>.
4. The final state before measurement is |1>.
5. Measurement in the computational basis yields the state |1> with certainty.

Predicted probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'The output is |1> with probability 1.0'}

## isqTrain/1085

- task_id: `isqTrain/1085`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3440`

### Prompt

帮我写一个isQ程序：implements the deutsch_jozsa pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a Deutsch-Jozsa circuit in isQ.

Let me analyze the circuit:

1. We have 2 input qubits q[0], q[1] and 1 ancilla qubit anc[0]
2. The oracle is for a balanced function f(x) = x[0] XOR x[1]

Steps:
1. Initialize: |000⟩ (q[0], q[1], anc[0])
2. X(anc[0]): |001⟩
3. H(anc[0]): |00⟩(|0⟩-|1⟩)/√2
4. H(q[0]), H(q[1]): uniform superposition on input × |−⟩ on ancilla
   = 1/2(|00⟩+|01⟩+|10⟩+|11⟩) ⊗ |−⟩

5. Oracle f(q, anc): This applies a phase based on f(x). For the balanced function f(x)=x[0]⊕x[1]:
   - f(00)=0: no phase
   - f(01)=1: phase -1
   - f(10)=1: phase -1
   - f(11)=0: no phase
   
   So: 1/2(|00⟩-|01⟩-|10⟩+|11⟩) ⊗ |−⟩

6. H(q[0]), H(q[1]): Apply H⊗H to input register
   H⊗H on |00⟩ → |++⟩ → 1/2(|00⟩+|01⟩+|10⟩+|11⟩)
   H⊗H on |01⟩ → 1/2(|00⟩-|01⟩+|10⟩-|11⟩)
   H⊗H on |10⟩ → 1/2(|00⟩+|01⟩-|10⟩-|11⟩)
   H⊗H on |11⟩ → 1/2(|00⟩-|01⟩-|10⟩+|11⟩)

   So: 1/4[|00⟩+|01⟩+|10⟩+|11⟩ - |00⟩+|01⟩-|10⟩+|11⟩ - |00⟩+|01⟩+|10⟩-|11⟩ + |00⟩-|01⟩-|10⟩+|11⟩] ⊗ |−⟩

   Let me compute coefficients:
   |00⟩: 1+(-1)+(-1)+1 = 0
   |01⟩: 1+1+1+(-1) = 2
   |10⟩: 1+(-1)+1+(-1) = 0
   |11⟩: 1+1+(-1)+1 = 2

   Wait, let me redo this more carefully.

   State after oracle: 1/2(|00⟩ - |01⟩ - |10⟩ + |11⟩) ⊗ |−⟩

   Apply H⊗H:
   |00⟩ → (|0⟩+|1⟩)(|0⟩+|1⟩)/2 = 1/2(|00⟩+|01⟩+|10⟩+|11⟩)
   |01⟩ → (|0⟩+|1⟩)(|0⟩-|1⟩)/2 = 1/2(|00⟩-|01⟩+|10⟩-|11⟩)
   |10⟩ → (|0⟩-|1⟩)(|0⟩+|1⟩)/2 = 1/2(|00⟩+|01⟩-|10⟩-|11⟩)
   |11⟩ → (|0⟩-|1⟩)(|0⟩-|1⟩)/2 = 1/2(|00⟩-|01⟩-|10⟩+|11⟩)

   So H⊗H [1/2(|00⟩ - |01⟩ - |10⟩ + |11⟩)] = 1/4[...]:
   |00⟩ coeff: 1-1-1+1 = 0
   |01⟩ coeff: 1+1+1-1 = 2 → wait that's wrong

   Let me be more careful:
   = 1/2 * 1/2 [(|00⟩+|01⟩+|10⟩+|11⟩) - (|00⟩-|01⟩+|10⟩-|11⟩) - (|00⟩+|01⟩-|10⟩-|11⟩) + (|00⟩-|01⟩-|10⟩+|11⟩)]

   |00⟩: 1-1-1+1 = 0
   |01⟩: 1+1-1-1 = 0
   
   Hmm, wait. Let me recalculate:

## isqExpand/algo/106

- task_id: `isqExpand/algo/106`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `superposition`, `basis_change`
- source: `isq_expansion`
- dataset_index: `4754`

### Prompt

Implement a quantum circuit in isQ: implements a 3-bit quantum random number generator. Apply Hadamard gates to all 3 qubits, then measure all qubits. The result should be a uniform distribution over all 8 outcomes, each with probability 1/8 = 0.125.

### Chain-of-thought reasoning

## Reasoning
Goal: 3-bit QRNG.

1. H on each qubit: (|0>+|1>)/sqrt(2) independently
2. Combined: uniform superposition of 8 states, amplitude 1/sqrt(8)
3. Probability per outcome: 1/8 = 0.125

Expected: [0.125]*8

## isqExpand/algo/89

- task_id: `isqExpand/algo/89`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `oracle`, `bug_fix`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `3099`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;
qbit q[3];

procedure oracle() {
    X(q[0]); X(q[1]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[0]); X(q[1]);
}

procedure diffusion() {
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
}

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    oracle();
    diffusion();
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug分析

### 问题
Oracle要标记|000>（所有量子位为0），需要在CCZ前后对所有3个量子位施加X门。

CCZ在q[0]=1, q[1]=1, q[2]=1时触发。为了检测q[0]=0, q[1]=0, q[2]=0，需要先用X门翻转所有位。

### Bug定位
Buggy代码只对q[0]和q[1]施加了X，遗漏了q[2]。这意味着CCZ在原始q[0]=0, q[1]=0, q[2]=1时触发，即标记了|001>而非|000>。

### 修复
在oracle()中添加X(q[2])：
X(q[0]); X(q[1]); X(q[2]); CCZ; X(q[0]); X(q[1]); X(q[2]);

修复后：P(|000>) = 0.78125

## isqTrain/3017

- task_id: `isqTrain/3017`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `236`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;
qbit q[3];
// GHZ-like state with X on q[1]
procedure main() {
    H(q[0]);
    CNOT(q[1], q[0]);
    CNOT(q[1], q[2]);
    X(q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug identification:**
The first CNOT gate `CNOT(q[1], q[0])` has swapped control and target arguments. It uses `q[1]` as control and `q[0]` as target, but `q[1]` is still |0⟩ at that point, so the CNOT does nothing — failing to create entanglement.

**2. Fix:**
Change `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])` so that `q[0]` (in superposition) controls the flip of `q[1]`, properly entangling them into a GHZ chain.

**3. State evolution (corrected):**
- |000⟩ → H(q[0]) → (|000⟩ + |100⟩)/√2
- CNOT(q[0], q[1]) → (|000⟩ + |110⟩)/√2
- CNOT(q[1], q[2]) → (|000⟩ + |111⟩)/√2
- X(q[1]) → (|010⟩ + |101⟩)/√2

This yields measurement probabilities {|010⟩: 0.5, |101⟩: 0.5}, matching the predicted output.

## isqTrain/1346

- task_id: `isqTrain/1346`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2690`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[3];

procedure my_cz(qbit a, qbit b) {
    H(b);
    CNOT(a, b);
    H(b);
}

procedure main() {

    H(q[0]); H(q[1]);

    my_cz(q[0], q[1]);

    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    my_cz(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);

    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the program**:
    *   Global qubits: `q[3]`. Initial state: $|000\rangle$ (q[0] is highest bit, q[2] is lowest).
    *   Gates on q[0] and q[1]: `H(q[0]); H(q[1])` -> $|+\rangle|+\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$. Q[2] is $|0\rangle$.
    *   `my_cz(q[0], q[1])` is exactly a Controlled-Z (CZ) gate. (H on target, CNOT, H on target = CZ).
    *   Sequence on q[0], q[1]: H H -> CZ -> H H -> X X -> CZ -> X X -> H H
    *   Let's trace the unitary transformation for `my_cz` sandwiched between H's and X's.
    *   Actually, `H H` on two qubits transforms $Z \otimes Z$ to $X \otimes X$. Let's just trace the basis states or the whole matrix.
    *   Wait, $H \otimes H$ and $CZ$. The sequence is:
        $H_0 H_1$
        $CZ_{01}$
        $H_0 H_1$
        $X_0 X_1$
        $CZ_{01}$
        $X_0 X_1$
        $H_0 H_1$
    *   Let's look at what this does to $|00\rangle$ (since $q[2]$ is untouched).
        $H_0 H_1 |00\rangle = |++\rangle$.
        $CZ_{01} |++\rangle = |++\rangle$. (Wait, $CZ |++\rangle = \frac{1}{2}(|0+\rangle |1-\rangle) \neq |++\rangle$. Wait, no. $CZ = |0\rangle\langle0| \otimes I + |1\rangle\langle1| \otimes Z$. On $|++\rangle$, it's $\frac{1}{2}( |00\rangle + |01\rangle + |10\rangle - |11\rangle ) = \frac{1}{\sqrt{2}}(|0+\rangle + |1-\rangle)$. )
        Let's use the identity: $(H \otimes H) CZ (H \otimes H) = CNOT$. Let's verify:
        $H CZ H = ?$
        No, the standard identity is $CZ = (I \otimes H) CNOT (I \otimes H)$.
        What is $(H \otimes H) CZ (H \otimes H)$?
        $(H \otimes H) |0\rangle = |+\rangle$, $(H \otimes H) |1\rangle = |-\rangle$.
        $CZ |00\rangle = |00\rangle \implies$ Maps $|++\rangle \to |++\rangle$.
        $CZ |01\rangle = |01\rangle \implies$ Maps $|+-\rangle \to |+-\rangle$.
        $CZ |10\rangle = |10\rangle \implies$ Maps $|-+\rangle \to |-+\rangle$.
        $CZ |11\rangle = -|11\rangle \implies$ Maps $|--\rangle \to -|--\rangle$.
        So $(H \otimes H) CZ (H \otimes H)$ is a $CZ$ in the $X$ basis! It's a controlled-Z gate but controlled by $X$, targeting $X$ (i.e., applying $Z$ if control is $|-\rangle$, $Z$ to target if it's $|-\rangle$). Actually it's just $Z \otimes Z$ with some phase? No, it maps $|--\rangle \to -|--\rangle$, so it's exactly a diagonal matrix with -1 on $|--\rangle$.
        Let's re-verify:
        $H_0 H_1 CZ_{01} H_0 H_1$:
        $|00\rangle \xrightarrow{H H} |++\rangle \xrightarrow{CZ} |++\rangle \xrightarrow{H H} |00\rangle$
        $|01\rangle \xrightarrow{H H} |+-\rangle \xrightarrow{CZ} |+-\rangle \xrightarrow{H H} |01\rangle$
        $|10\rangle \xrightarrow{H H} |-+\rangle \x

### Reference answer

{'predicted_probs': {'6': 1.0}, 'explanation': 'Parametric variant of isqEval/492. Dimension: qubit_variant: q[2] -> q[3].'}

## isqTrain/2798

- task_id: `isqTrain/2798`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `177`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;

// g(x) = g(x + 8)
oracle bool[4] g(bool a[4]) {
    bool res[] = [a[0], a[1], a[2], false];
    return res;
}

qbit q[4], res[4];

procedure main(){
    H(q);
    g(q, res);
    // H(q); // BUG: missing Hadamard 
    print M(q);
}
```

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug:** The second Hadamard gate `H(q);` is commented out in the `main` procedure. In algorithms like Simon's or Deutsch-Jozsa, this second Hadamard transform is crucial to interfere the superposition states and extract phase information, collapsing them into a measurable computational basis state.
2. **The Fix:** Uncomment `H(q);` to apply the Hadamard gate to the `q` register after the oracle `g(q, res)` is executed.
3. **State Evolution:** 
   - Initialize 8 qubits to |0>: |0000>_q |0000>_res
   - Apply H to `q`: 1/4 Σ_{x∈{0,1}^4} |x>_q |0000>_res
   - Apply oracle `g`: 1/4 Σ_x |x>_q |g(x)>_res
   - Apply H to `q` again (the fix): 1/4 Σ_x Σ_z (-1)^(x·z) |z>_q |g(x)>_res. Due to the oracle's periodicity (s=1000), destructive interference occurs for any `z` where `s·z = 1`, leaving only states where `z` starts with 0. Measurement yields uniform probabilities across |0000> to |0111>.

## isqQA/quantum_algorithms/120_optimization_variant

- task_id: `isqQA/quantum_algorithms/120_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `optimization_variant`, `algorithm`, `量子计数算法`
- source: `qa_pipeline`
- dataset_index: `4712`

### Prompt

在量子计数算法的发展中，为了降低硬件资源开销并适应含噪声中等规模量子（NISQ）设备，研究者提出了哪些关键的改进变体？请以“迭代量子计数”为例，推导其核心数学原理，并使用 isQ 语言编写一段展示其核心受控 Grover 迭代过程的代码。

### Reference answer

量子计数算法通过结合 Grover 搜索和量子相位估计（QPE）来估计无结构数据库中目标解的数量 $M$。标准的 QPE 需要大量的辅助量子比特和深层的量子电路（包括逆量子傅里叶变换），这在当前的 NISQ 时代极难实现。为此，研究人员提出了两种重要的改进变体：

1. **迭代量子计数**：借鉴了 Kitaev 的迭代相位估计思想，该变体将复杂的并行相位估计转化为串行执行。它只需要一个辅助量子比特，通过不断施加不同幂次的受控 Grover 算子，并在基态上进行测量和经典反馈，逐位估计出相位。这极大地减少了量子比特的需求和电路深度。
2. **基于最大似然估计的变体**：完全摒弃了 QPE 结构，通过在不同迭代次数下运行振幅放大电路，测量目标态出现的概率，并在经典计算机上使用最大似然估计拟合出振幅，从而推算出 $M$。

### 数学推导：迭代量子计数的原理

设搜索空间大小为 $N$，目标解数量为 $M$。Grover 算子 $G$ 在由非目标均匀叠加态 $|\alpha\rangle$ 和目标均匀叠加态 $|\beta\rangle$ 张成的二维子空间中，可以表示为旋转矩阵：
$$G = \begin{pmatrix} \cos(2\theta) & -\sin(2\theta) \\ \sin(2\theta) & \cos(2\theta) \end{pmatrix}$$
其中 $\sin^2(\theta) = \frac{M}{N}$。该算子的本征值为 $e^{\pm i 2\theta}$。量子计数的本质就是估计本征相位 $\phi = 2\theta$。

在迭代量子计数中，我们使用一个辅助比特 $|c\rangle$ 和系统寄存器 $|\psi\rangle$。初始态制备为 $|+\rangle \otimes |\psi\rangle$。对于第 $k$ 轮迭代（旨在确定相位小数点后第 $k$ 位），我们执行 $2^k$ 次受控 $G$ 操作：
$$|+\rangle |\psi\rangle \rightarrow \frac{1}{\sqrt{2}} (|0\rangle |\psi\rangle + |1\rangle G^{2^k} |\psi\rangle)$$
假设我们估计的相位前 $k-1$ 位为 $\tilde{\phi}_{k-1}$，则在辅助比特上施加相位旋转 $R_z(\tilde{\phi}_{k-1})$ 抵消已知相位，最后对辅助比特施加 Hadamard 门并测量。测量结果将以极高的概率直接给出相位的第 $k$ 位二进制表示。由此，仅需 1 个辅助比特即可逐步逼近真实相位，进而求得 $M = N \sin^2(\phi/2)$。

### isQ 代码实现

以下代码展示了如何使用 isQ 语言实现迭代量子计数中所需的受控 Grover 迭代核心逻辑。这里以 3 量子比特的搜索空间为例，标记状态 $|101\rangle$。

```isq
import std;

const n = 3;
const N = 1 << n;
// 数据寄存器和辅助控制比特
qbit q[n];
qbit anc[2]; // anc[0] 用于 Toffoli 门分解, anc[1] 用作受控迭代的控制比特

// 标记目标状态 |101> 的 Oracle
procedure oracle() {
    X(q[1]);
    Toffoli(q[0], q[2], anc[0]);
    X(q[1]);
}

// 扩散算子
procedure diffusion() {
    for i in 0:n {
        H(q[i]);
        X(q[i]);
    }
    H(q[2]);
    Toffoli(q[0], q[1], anc[0]);
    CNOT(anc[0], q[2]);
    Toffoli(q[0], q[1], anc[0]);
    H(q[2]);
    
    for i in 0:n {
        X(q[i]);
        H(q[i]);
    }
}

// Grover 迭代算子
procedure grover_iteration() {
    oracle();
    diffusion();
}

procedure main() {
    // 初始化系统寄存器为均匀叠加态
    for i in 0:n {
        H(q[i]);
    }
    
    // 初始化控制比特为 |+> 态
    H(anc[1]);
    
    // 模拟第 k 轮迭代，假设需要执行 2^2 = 4 次受控 Grover 算子
    // 在 isQ 中，利用 ctrl 关键字实现受控操作
    for i in 0:4 {
        ctrl @[anc[1]] grover_iteration();
    }
    
    // 恢复控制比特的相位信息
    H(anc[1]);
    
    // 测量控制比特，获取相位估计位
    M(anc[1]);
    
    // 测量数据比特
    for i in 0:n {
        M(q[i]);
    }
}
```

通过在经典循环中不断调整受控 Grover 算子的执行次数并结合前期的测量反馈，该变体算法能够在极少量子资源的情况下完成高精度的计数任务。

## isqTrain/2888

- task_id: `isqTrain/2888`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2103`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[1];
procedure main() {
    Rx(1.5707963, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The qubit q[0] starts in the initial state |0>.
2. The `Rx(1.5707963, q[0])` gate applies an $R_x(\pi/2)$ rotation to the qubit.
3. The quantum state evolves to $\frac{1}{\sqrt{2}}|0\rangle - \frac{i}{\sqrt{2}}|1\rangle$.
4. Measuring the qubit collapses the superposition into either |0> or |1>.
5. The probability of each outcome is determined by

### Reference answer

{'predicted_probs': {'0': 0.5000000133974483, '1': 0.4999999866025518}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

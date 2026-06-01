# ISQ training COT RAG corpus: quantum_algorithms shard 107

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/76

- task_id: `isqExpand/algo/76`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `vqe`, `output_prediction`, `ry_cnot`, `entanglement`
- source: `isq_expansion`
- dataset_index: `4265`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];

procedure main() {
    Ry(pi/2.0, q[0]);
    Ry(pi/3.0, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
Starting from |00>:

1. Ry(pi/2) on q[0]: cos(pi/4)|0> + sin(pi/4)|1> = (1/sqrt2)(|0> + |1>)
2. Ry(pi/3) on q[1]: cos(pi/6)|0> + sin(pi/6)|1> = (sqrt3/2)|0> + (1/2)|1>

Tensor product (before CNOT):
- |00>: (1/sqrt2)*(sqrt3/2) = sqrt3/(2*sqrt2)
- |01>: (1/sqrt2)*(1/2) = 1/(2*sqrt2)
- |10>: (1/sqrt2)*(sqrt3/2) = sqrt3/(2*sqrt2)
- |11>: (1/sqrt2)*(1/2) = 1/(2*sqrt2)

After CNOT(q[0],q[1]): |10>->|11>, |11>->|10>
- |00>: sqrt3/(2*sqrt2), P = 3/8 = 0.375
- |01>: 1/(2*sqrt2), P = 1/8 = 0.125
- |10>: 1/(2*sqrt2) [was |11>], P = 1/8 = 0.125
- |11>: sqrt3/(2*sqrt2) [was |10>], P = 3/8 = 0.375

The circuit creates Bell-like correlations: |00> and |11> are equally likely (P=0.375 each), |01> and |10> are equally likely (P=0.125 each).

### Reference answer

{'predicted_probs': {'00': 0.375, '01': 0.125, '10': 0.125, '11': 0.375}, 'explanation': 'Ry(pi/2) on q[0] gives (1/sqrt2)(|0>+|1>). Ry(pi/3) on q[1] gives (sqrt3/2)|0>+(1/2)|1>. After CNOT(q[0],q[1]): amplitudes are |00>: (1/sqrt2)*(sqrt3/2), |01>: (1/sqrt2)*(1/2), |10>: (1/sqrt2)*(1/2) [from |11>->|10>], |11>: (1/sqrt2)*(sqrt3/2) [from |10>->|11>]. Probabilities: P(00)=P(11)=3/8=0.375, P(01)=P(10)=1/8=0.125.'}

## isqTrain/2729

- task_id: `isqTrain/2729`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4869`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit w[5];
procedure main() {
    for i in 0:3{
        X2P(w[i]);
        Y2P(w[i+1]);
        CNOT(w[i], w[i+1]);
    }
    for i in 0:3{
        for j in 0:3{
            for k in 0:3{
                H(w[(i+j+k) % 5]);
            }
        }
    }
    for i in 0:5{
        M(w[i]);
    }
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program.
The program defines a quantum circuit with 5 qubits `w[5]`.
The first loop applies operations for `i` from 0 to 2 (0:3 means 0,1,2):
Wait, in isQ `for i in 0:3` means `i` goes 0, 1, 2. Let me double check. Usually `0:3` might be 0,1,2 or 0,1,2,3. Wait! In Python `range(3)` is 0,1,2. In isQ, `0:3` usually means `0, 1, 2`. Let's see the number of iterations. If it means 0, 1, 2, 3, it's 4 iterations. Wait, `0:3` in some languages like Rust is 0, 1, 2. Let me check the standard isQ docs.
Ah, in isQ `for i in 0:3` means `i` can be 0, 1, 2. Wait. Let me check if it's 0, 1, 2. Wait, wait. If it is 0 to 2, it's 3 iterations. If it's 0 to 3, it's 4 iterations.
Let's look at the problem description:
`for i in 0:3 { X2P(w[i]); Y2P(w[i+1]); CNOT(w[i], w[i+1]); }`
If `i` goes 0, 1, 2, 3, then `i+1` can be 4, which is valid for `w[5]`. So it's likely 0, 1, 2, 3 (4 iterations).
Wait, in isQ, `for i in a:b` iterates over `a, a+1, ..., b-1`. So `0:3` means 0, 1, 2.
Let's see: `i` goes 0, 1, 2. Then `i+1` goes 1, 2, 3. The array is size 5. If it was 4 iterations, `i=3` -> `i+1=4`.
But wait, if `0:3` means `0,1,2`, that's 3 iterations. If it means 0,1,2,3, that's 4.
Wait, in isQ, `for i in 0:3` means `0, 1, 2`. Let's assume it means 0, 1, 2.
Let's consider the predicted output probabilities:
`{'00000': 0.125, '00100': 0.125, '01000': 0.125, '01100': 0.125, '10000': 0.125, '10100': 0.125, '11000': 0.125, '11100': 0.125}`
Notice that qubits 3 and 4 are always `0`. This means they are in the |0> state.
If the first loop was `i` in 0, 1, 2, 3, then qubit 4 would be modified by `Y2P(w[4])` and `CNOT(w[3], w[4])`.
Since qubit 4 is not measured as 0 and 1 with equal probability (it's exactly 0 probability of being 1), qubit 4 must not have been touched!
Wait, if qubit 4 is always 0, then `i+1` never reaches 4.
So `0:3` means 0, 1, 2. (3 iterations).
Wait, let's look at the second loop:
`for i in 0:3 { for j in 0:3 { for k in 0:3 { H(w[(i+j+k) % 5]); } } }`
If `0:3` means 0, 1, 2, then `i+j+k` goes from 0 to 6.
Let's trace the H gates. Each `H` applied twice is identity.
If `0:3` means 0, 1, 2:
Values of `i+j+k` mod 5.
Let `N = 3`.
The number of ways to form `i+j+k = X` for X in 0..6.
Wait, `0:3` could also mean 0,1,2,3 (4 iterations). Let's re-read isQ documentation carefully.
In isQ, `for i in 0:3` means `i=0, 1, 2`. Wait, if it

### Reference answer

{'predicted_probs': {'00000': 0.12500000000000003, '00100': 0.12499999999999986, '01000': 0.1250000000000001, '01100': 0.12500000000000003, '10000': 0.12499999999999997, '10100': 0.12499999999999994, '11000': 0.12500000000000006, '11100': 0.12499999999999994}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1335

- task_id: `isqTrain/1335`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `420`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;

qbit x[1];
qbit y[2];

procedure main() {
    X(y[0]);
    H(x[0]); H(y[0]);

    X(y[0]);

    H(x[0]);
    M(x[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
- The circuit initializes `x[0]` to |0>, while the operations on `y` qubits do not affect `x[0]` due to the absence of entangling gates.
- The first `H(x[0])` transforms the state of `x[0]` from |0> to |+>.
- The subsequent `X(y[0])` only affects the `y` register, leaving `x[0]` in the |+> state.
- The second `H(x[0])` reverses the first Hadamard, changing `x[0]` from |+> back to |0>.
- The final measurement `M(x[0])` is performed on the |0> state.

Predicted probability distribution: {|0>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqEval/483. Dimension: qubit_variant: y[1] -> y[2].'}

## isqTrain/4425

- task_id: `isqTrain/4425`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `992`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];

procedure main() {
    // 1. Initial state
    H(q[0]); H(q[1]);
    
    // 2. Cost Unitary (gamma = pi/4)
    // Rz(2*gamma) = Rz(pi/2)
    CNOT(q[0], q[1]);
    Rz(pi/2.0, q[1]);
    CNOT(q[0], q[1]);
    
    // 3. Mixing Unitary (beta = pi/8)
    // Rx(2*beta) = Rx(pi/4)
    Rx(pi/4.0, q[0]);
    Rx(pi/4.0, q[1]);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, step-by-step quantum circuit analysis of the provided isQ program. It should predict the probability distribution and explain the reasoning using Dirac notation. Output format must strictly follow the rules.

2.  **Analyze the isQ program:**
    *   `qbit q[2];`: 2 qubits, initialized to $|00\rangle$.
    *   `H(q[0]); H(q[1]);`: Apply H to both qubits.
        *   State becomes $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   `CNOT(q[0], q[1]); Rz(pi/2.0, q[1]); CNOT(q[0], q[1]);`: This is a controlled-Rz gate.
        *   Basis states $|00\rangle$ and $|10\rangle$ are unaffected.
        *   $|01\rangle$ gets Rz($\pi/2$) = $e^{-i\pi/4}|01\rangle$.
        *   $|11\rangle$ gets Rz($\pi/2$) = $e^{i\pi/4}|11\rangle$.
        *   Wait, Rz($\theta$) on $|1\rangle$ is $e^{-i\theta/2}|0\rangle$ and $e^{i\theta/2}|1\rangle$. Let's be careful.
        *   Rz($\pi/2$) = $e^{-i\pi/4}|0\rangle\langle0| + e^{i\pi/4}|1\rangle\langle1|$.
        *   Wait, standard isQ Rz gate definition usually implies $|0\rangle \to e^{-i\theta/2}|0\rangle$ and $|1\rangle \to e^{i\theta/2}|1\rangle$.
        *   Since it's applied only when control is 1:
            *   $|00\rangle \to |00\rangle$
            *   $|01\rangle \to |01\rangle$ (target is 0, phase $e^{-i\pi/4}$? Wait, target is q[1]. So if control is 0, target is 1? NO. Control is q[0]. Target is q[1]. If control is 0, target is 1? NO, CNOT only does something when control is 1. Control is q[0], so if q[0] is 1, it applies Rz to q[1].)
            *   Let's trace carefully:
                *   $|00\rangle$: q[0]=0, no Rz. State is $|00\rangle$.
                *   $|01\rangle$: q[0]=0, no Rz. State is $|01\rangle$.
                *   $|10\rangle$: q[0]=1, q[1]=0. Rz($\pi/2$) on $|0\rangle$ gives $e^{-i\pi/4}|0\rangle$. State is $e^{-i\pi/4}|10\rangle$.
                *   $|11\rangle$: q[0]=1, q[1]=1. Rz($\pi/2$) on $|1\rangle$ gives $e^{i\pi/4}|1\rangle$. State is $e^{i\pi/4}|11\rangle$.
        *   State after step 2: $\frac{1}{2}(|00\rangle + |01\rangle + e^{-i\pi/4}|10\rangle + e^{i\pi/4}|11\rangle)$.
    *   `Rx(pi/4.0, q[0]); Rx(pi/4.0, q[1]);`: Apply Rx($\pi/4$) to both.
        *   Rx($\theta$) = $\frac{1}{\sqrt{2}}\begin{pmatrix} 1 & -i \\ -i & 1 \end{pmatrix}$ for $\theta=\pi/4$? No, $R_x(\theta) = e^{-i\theta X/2} = \cos(\theta/2)I - i\sin(\theta/2)X = \begin{pmatrix} \cos(\theta/2) & -i\sin(\theta/2) \\ -i\sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$.
        *   For $\theta = \pi/4$, $\cos(\pi/8) = c$, $\sin

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 0.5000, P(|10>) = 0.5000.'}

## isqTrain/314

- task_id: `isqTrain/314`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1106`

### Prompt

Write an isQ program that implements the oracle_boolean pattern. Include explicit identity operations in the circuit (H-H pair before M(x[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement the Deutsch oracle for the constant function f(x)=1, with explicit H-H identity pairs to demonstrate gate cancellation awareness.

2. **Qubits**: 2 qubits — x[0] (input, measured) and y[0] (ancilla for phase kickback).

3. **State evolution**:
   - Initial: |0⟩|0⟩; X(y[0]) → |0⟩|1⟩
   - H(x[0])H(y[0]) → |+⟩|−⟩ = ½(|00⟩−|01⟩+|10⟩−|11⟩)
   - X(y[0]) oracle (f=1, flips y unconditionally): → −|+⟩|−⟩ (global phase −1)
   - H(x[0]): −|0⟩|−⟩; H(x[0]): −|+⟩|−⟩; H(x[0]): −|0⟩|−⟩ (three H's net to one H since H²=I)

4. **Result**: x[0] is in |0⟩ (ignoring global phase), so measuring x[0] yields P(|0⟩)=1.0, confirming f is constant.

## isqQA/quantum_algorithms/133_comparison

- task_id: `isqQA/quantum_algorithms/133_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `comparison`, `algorithm`, `量子比较器`
- source: `qa_pipeline`
- dataset_index: `2395`

### Prompt

在量子算法设计中，量子比较器是实现条件分支、搜索Oracle和排序等操作的核心组件。请深入对比分析“基于减法器与借位链的经典逻辑映射方法”与“基于量子傅里叶变换（QFT）的比较方法”。详细讨论这两种实现在资源消耗（辅助比特、量子门深度）、抗噪性能，以及在NISQ时代与容错量子计算中的适用场景差异。最后，请用isQ代码实现一个基于基础布尔逻辑的2-qubit可逆量子比较器模块，要求在不破坏原始输入的前提下，将比较结果存储到输出比特中。

### Reference answer

<think 
> 量子比较器的设计直接受到底层物理架构和纠错能力的制约。基于减法器/借位链的方法本质上是经典数字电路中比较逻辑的量子版本，利用受控非门（CNOT）和托弗利门构建。其资源消耗随比特数线性增长，需要O(n)的辅助比特和O(n)的量子线路深度。由于所有门都是离散的Clifford+T门或基础的通用门集，它在容错量子计算（FTQC）中具有极大的优势，且由于没有连续旋转，在NISQ设备上受旋转角度误差影响较小，但过深的线路会引发退相干。相反，基于QFT的比较器将数据转换到频域通过相位旋转进行比较。理论上它结构优雅，但依赖大量受控相位门，这些门的分解会导致极大的T门深度，在FTQC中开销惊人。同时，受控旋转对当前NISQ硬件的噪声极其敏感。因此，当前实际算法开发基本倾向于基础布尔逻辑映射法。
 
对于代码实现，我们利用可逆逻辑比较两个2位量子整数A和B。为了不破坏输入，我们通过受控逻辑计算A>B。高位决定大小，只有高位相等时才看低位。由于isQ不支持SWAP且需要基础门，我们直接使用Toffoli和CNOT。 
</think 
>量子比较器是量子算法中实现条件判断的核心基石。在量子计算领域，实现两个量子寄存器所代表的整数大小比较，主要存在两种截然不同的设计范式：基于减法与布尔逻辑链的经典映射法，以及基于量子傅里叶变换（QFT）的相位比较法。这两种方法在资源消耗和物理可行性上表现出显著的差异。 

首先是**基于布尔逻辑和借位链的比较器**。这种方法本质上是经典数字电路中比较逻辑的量子化延伸。它通过级联半减器或全减器逻辑，提取最高位的借位标志来判断大小。 
- **资源消耗**：通常需要O(n)数量的辅助比特来暂存借位信息，其线路深度也为O(n)。其核心优势在于线路完全由基础的Toffoli门、CNOT门和X门构成。 
- **适用场景与优缺点**：这是目前容错量子计算（FTQC）架构下的首选方案。因为所有操作都可以完美地分解为Clifford+T门集，便于进行量子纠错。在NISQ（含噪声中等规模量子）设备上，虽然它没有连续旋转带来的系统误差，但长线路深度容易导致退相干。它广泛应用于量子排序、数据库查找以及金融定价中的条件触发逻辑。 

其次是**基于量子傅里叶变换（QFT）的比较器**。该方法将两个量子寄存器通过QFT转换到频域，在其中施加条件相位旋转，最后通过逆QFT读出比较结果。 
- **资源消耗**：如果不考虑逆变换，它看似不需要大量的辅助比特，但由于需要执行2n次QFT和逆QFT，且包含大量受控相位门（如CRk），其总体线路复杂度极高。 
- **适用场景与优缺点**：受控相位旋转包含无穷小角度，这在NISQ时代是致命的，因为微小的控制脉冲误差会直接导致计算失败。此外，在FTQC中，这些连续旋转门需要经过繁杂的Solovay-Kitaev分解近似，导致T门数量呈爆炸式增长。因此，除非在极少数本身就高度依赖QFT的特定算法内部，这种方法在独立的比较器设计中基本被现代学术界弃用。 

综上所述，基于布尔逻辑的减法比较器在当前和未来的量子体系结构中占据绝对主导地位。下面是用isQ语言实现的一个基于布尔逻辑的2-qubit可逆量子比较器。该模块比较两个2位整数A(a1a0)和B(b1b0)，利用辅助比特计算“A>B”的状态并存储在result中，计算结束后通过逆操作完全恢复所有输入比特和中间辅助比特的量子态。 

```isq 
import std; 

qbit a[2]; 
qbit b[2]; 
qbit anc[2]; 
qbit result; 

procedure main() { 
    // 目标：比较两个2位量子整数 A (a[1]a[0]) 和 B (b[1]b[0]) 
    // 如果 A > B，则 result 翻转为 1，否则保持 0。此操作不破坏输入。 
    
    // 第一步：处理低位 a[0] > b[0] 
    // 若 a[0]=1, b[0]=0，则 a[0] > b[0] 成立。 
    X(b[0]); 
    Toffoli(a[0], b[0], anc[0]); 
    X(b[0]); 
    
    // 第二步：处理高位 a[1] == b[1] 
    // 若二者相等，则将低位比较结果 anc[0] 传递给 result 
    CNOT(a[1], anc[1]); 
    CNOT(b[1], anc[1]); 
    
    // 当 a[1] == b[1] (即 anc[1] 为 0) 时，传递低位结果 
    // 使用负控制：如果 anc[1] 为 0，则执行 CNOT 
    nctrl @[anc[1]] CNOT(anc[0], result); 
    
    // 第三步：处理高位 a[1] > b[1] 
    // 若 a[1]=1, b[1]=0，则直接决定 A > B，翻转 result 
    X(b[1]); 
    Toffoli(a[1], b[1], result); 
    X(b[1]); 
    
    // 第四步：逆操作 Uncompute，恢复 anc 寄存器，消除量子纠缠垃圾 
    CNOT(b[1], anc[1]); 
    CNOT(a[1], anc[1]); 
    
    X(b[0]); 
    Toffoli(a[0], b[0], anc[0]); 
    X(b[0]); 
} 
```

## isqTrain/3650

- task_id: `isqTrain/3650`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `149`

### Prompt

Create an isQ quantum circuit that the 4-qubit inverse QFT on input |0101>. Apply bit-reversal, then inverse controlled-Rz rotations and Hadamard gates in reverse order. Measure all qubits.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The goal is to implement the 4-qubit inverse QFT on input |0101>.

1. We have 4 qubits q[0], q[1], q[2], q[3].
2. Initial state: |0000>
3. Apply X(q[1]) and X(q[3]) to prepare |0101> = |1>|0>|1>|0> where q[3] is the leftmost bit.

Wait, let me reconsider the bit ordering. In the input |0101>, if we have q[0] as the least significant bit (rightmost), then:
- q[0] = 1 (rightmost)
- q[1] = 0
- q[2] = 1
- q[3] = 0 (leftmost)

So X(q[1]) and X(q[3]) would give us |1010> in the qubit ordering q[3]q[2]q[1]q[0].

Wait, let me re-read. The code applies X(q[1]) and X(q[3]). So:
- q[1] is flipped to |1>
- q[3] is flipped to |1>
- q[0] and q[2] remain |0>

So the state is |q[3]q[2]q[1]q[0]> = |1010>.

But the comment says input is |0101>. There might be some convention difference. Let me just follow the code.

After X(q[1]) and X(q[3]): state is |1>_q3 ⊗ |0>_q2 ⊗ |1>_q1 ⊗ |0>_q0

Then bit-reversal swaps:
- CNOT(q[0], q[3]); CNOT(q[3], q[0]); CNOT(q[0], q[3]) — swaps q[0] and q[3]
- CNOT(q[1], q[2]); CNOT(q[2], q[1]); CNOT(q[1], q[2]) — swaps q[1] and q[2]

After swapping q[0]↔q[3] and q[1]↔q[2]:
State becomes |0>_q3 ⊗ |1>_q2 ⊗ |0>_q1 ⊗ |1>_q0

So after bit-reversal: |0101> in q[3]q[2]q[1]q[0] notation.

Now the inverse QFT operations:

The standard QFT on 4 qubits performs:
- H on q[0], then controlled rotations from q[0] to others
- H on q[1], then controlled rotations from q[1] to q[2], q[3]
- H on q[2], then controlled rotation from q[2] to q[3]
- H on q[3]
Then bit reversal at the end.

The inverse QFT reverses this: first bit reversal, then undo the operations in reverse.

Looking at the code after bit reversal:
1. H(q[3])
2. ctrl Rz(-π/4, q[3], q[2])
3. H(q[2])
4. ctrl Rz(-π/8, q[3], q[1])
5. ctrl Rz(-π/4, q[2], q[1])
6. H(q[1])
7. ctrl Rz(-π/16, q[3], q[0])
8. ctrl Rz(-π/8, q[2], q[0])
9. ctrl Rz(-π/4, q[1], q[0])
10. H(q[0])

This is indeed the inverse QFT. The QFT would use positive rotation angles; the inverse uses negative angles.

Now, the input to the inverse QFT (after bit reversal) is |0101> (in computational basis).

QFT|0101> gives a specific output. So inverse QFT applied to |0101> would give QFT†|0101>.

Actually, let me think about this differently. If QFT|x> = |ψ> where |ψ> is in the Fourier basis, then inverse QFT|ψ> = |x>.

But here we're applying inverse QFT to |0101> which is a computational basis state, not necessarily a Fourier basis state.

The QFT maps: QFT|j> = (1/√N) Σ_k e^{2πijk/N} |k>

So inverse QFT|j> = (1/√N) Σ_k e^{-2πijk/N} |k>

For N=16 (4 qubits), inverse QFT|5> = (1/4) Σ_{k=0}^{

## isqTrain/89

- task_id: `isqTrain/89`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `914`

### Prompt

用isQ实现implements the amplitude_amplification pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this amplitude amplification circuit with reversed measurement order.

1. **Goal**: Implement Grover's amplitude amplification to find |11⟩ with reversed measurement order.

2. **Qubits**: 2 qubits (q[0], q[1]), both measured.

3. **State evolution**:

- Initial state: |00⟩
- After H(q[0]), H(q[1]): (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩) = |+⟩|+⟩
- Oracle for |11⟩: my_cz applies CZ using H-CNOT-H decomposition
  - CZ flips the phase of |11⟩
  - State becomes: (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩)
- Diffuser:
  - H(q[0]), H(q[1]): Returns to computational basis-like superposition, but with sign change
  - After H⊗H: (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩) → the amplitude of |00⟩ becomes -1/2, others become... let me recalculate
  
  Actually, let me be more careful. The diffuser is: H⊗2 → X⊗2 → CZ → X⊗2 → H⊗2
  
  This is the standard Grover diffuser which reflects about the mean.
  
  Starting state after oracle: (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩)
  
  The diffuser inverts about the mean. The mean of amplitudes is (1/2 + 1/2 + 1/2 - 1/2)/4 = 1/4
  
  After diffuser:
  - |00⟩: 2*(1/4) - 1/2 = 0... no wait, the formula is: new_amp = 2*mean - old_amp
  
  Actually, the Grover diffuser applies a reflection about |s⟩ = H⊗2|00⟩.
  
  Let me just compute step by step through the diffuser:
  
  State after oracle: (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩)
  
  After H⊗2: H⊗2 (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩)
  
  H⊗2|00⟩ = (1/2)(|00⟩+|01⟩+|10⟩+|11⟩)
  H⊗2|01⟩ = (1/2)(|00⟩-|01⟩+|10⟩-|11⟩)
  H⊗2|10⟩ = (1/2)(|00⟩+|01⟩-|10⟩-|11⟩)
  H⊗2|11⟩ = (1/2)(|00⟩-|01⟩-|10⟩+|11⟩)
  
  So H⊗2 of our state:
  (1/2)[(1/2)(|00⟩+|01⟩+|10⟩+|11⟩) + (1/2)(|00⟩-|01⟩+|10⟩-|11⟩) + (1/2)(|00⟩+|01⟩-|10⟩-|11⟩) - (1/2)(|00⟩-|01⟩-|10⟩+|11⟩)]
  
  = (1/4)[(|00⟩+|01⟩+|10⟩+|11⟩) + (|00⟩-|01⟩+|10⟩-|11⟩) + (|00⟩+|01⟩-|10⟩-|11⟩) - (|00⟩-|01⟩-|10⟩+|11⟩)]
  
  Coefficient of |00⟩: 1+1+1-1 = 2
  Coefficient of |01⟩: 1-1+1+1 = 2
  Coefficient of |10⟩: 1+1-1+1 = 2
  Coefficient of |11⟩: 1-1-1-1 = -2
  
  So after H⊗2: (1/4)(2|00⟩ + 2|01⟩ + 2|10⟩ - 2|11⟩) = (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩)
  
  Hmm, that's the same state. That doesn't seem right... let me reconsider.
  
  Wait, I need to redo this. After the oracle, the state is:
  |ψ⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩)
  
  The diffuser is: D = 2|s⟩⟨s

## isqTrain/4078

- task_id: `isqTrain/4078`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3414`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[3];

unit grover_oracle(qbit q[3]) {
    X(q[0]);
    X(q[1]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[1]);
    X(q[0]);
} deriving gate

unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    grover_oracle(q);
    grover_diffusion(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants an explanation of the provided isQ code (a 3-qubit Grover's algorithm) and the most likely measurement outcome. I need to output the analysis in the specified format, using Dirac notation, and predict the probability distribution.

2.  **Analyze the isQ Code**:
    *   **Initialization**: `qbit q[3]`
    *   **Main program**:
        *   `H(q[0]); H(q[1]); H(q[2]);` -> Initializes the state to $|+\rangle^{\otimes 3} = \frac{1}{\sqrt{8}}\sum_{x=0}^{7} |x\rangle$.
        *   `grover_oracle(q);`:
            *   `X(q[0]); X(q[1]);` -> Maps basis states. Specifically, $|000\rangle \leftrightarrow |110\rangle$, etc.
            *   `ctrl CZ(q[0], q[1], q[2]);` -> Multi-controlled Z (Toffoli-like phase shift). In the computational basis, it applies a Z gate (phase -1) to the state where all three are |1>. So, it applies -1 to $|110\rangle$ (because X on 0,1 made 1,1).
            *   `X(q[0]); X(q[1]);` -> Uncompute.
            *   *Oracle effect*: The state $|110\rangle$ gets a phase of -1. So the target state is $|110\rangle$.
        *   `grover_diffusion(q);`:
            *   Standard diffusion operator: $H^{\otimes 3} (2|0\rangle\langle 0| - I) H^{\otimes 3}$.
            *   Implementation: `H` -> `X` -> `ctrl CZ` -> `X` -> `H`.
            *   This reflects the state about the mean.
        *   `M(q[0]); M(q[1]); M(q[2]);` -> Measurement.

3.  **Trace the Quantum State**:
    *   Initial state: $|000\rangle$
    *   After H gates: $|\psi_0\rangle = \frac{1}{\sqrt{8}} \sum_{x=0}^7 |x\rangle = \frac{1}{2\sqrt{2}} (|000\rangle + |001\rangle + |010\rangle + |011\rangle + |100\rangle + |101\rangle + |110\rangle + |111\rangle)$
    *   After Oracle: The state $|110\rangle$ gets a -1 phase.
        $|\psi_1\rangle = \frac{1}{2\sqrt{2}} (|000\rangle + |001\rangle + |010\rangle + |011\rangle + |100\rangle + |101\rangle - |110\rangle + |111\rangle)$
    *   After Diffusion: The diffusion operator $D = 2|\psi_0\rangle\langle\psi_0| - I$.
        Let's calculate $D |\psi_1\rangle$.
        $|\psi_1\rangle = |\psi_0\rangle - \frac{2}{2\sqrt{2}} |110\rangle = |\psi_0\rangle - \frac{1}{\sqrt{2}} |110\rangle$.
        $D |\psi_1\rangle = (2|\psi_0\rangle\langle\psi_0| - I)(|\psi_0\rangle - \frac{1}{\sqrt{2}} |110\rangle)$.
        $\langle\psi_0|\psi_0\rangle = 1$.
        $\langle\psi_0|110\rangle = \frac{1}{2\sqrt{2}}$.
        $D |\psi_1\rangle = 2|\psi_0\rangle(1 - \frac{1}{4}) - |\psi_0\rangle + \frac{1}{\sqrt{2}} |110\rangle$
        $D |\psi_1\rangle = 2|\psi_0\rangle(\frac{3}{4}) - |\psi_0\rangle + \frac{1}{\sqrt{2}} |110\rangle = \frac{1}{2}|\psi_0\rangle + \frac{1}{\sqrt{2}} |110\rangle$.
        Substitute $|\psi_0\rangle = |\psi_1\rangle + \frac{1}{\sqrt{2}} |110\rangle$:
        $D |\psi_1\rangle = \frac{1}{2}(|

### Reference answer

Dominant output states: |001> with probability ~0.78 each

## isqTrain/3043

- task_id: `isqTrain/3043`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2849`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit q[4];
// Bell pair creator as derived gate
procedure bellpair(qbit a, qbit b) {
    // H(a); // BUG: missing Hadamard
    CNOT(a, b);
} deriving gate
procedure main() {
    bellpair(q[0], q[1]);
    bellpair(q[2], q[3]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug identification:** In the `bellpair` procedure, the Hadamard gate `H(a)` is commented out on line 6 (`// H(a);`). Without it, only CNOT(a, b) is applied to |00⟩, which acts as identity (control qubit is |0⟩). This means the circuit produces deterministic |0000⟩ instead of entangled Bell pairs.

**2. Fix:** Uncomment `H(a);` to restore the Hadamard gate. The corrected `bellpair` body should be:

**3. State evolution (corrected circuit):**
- Initial: |0000⟩
- After `bellpair(q[0], q[1])`: H(q[0]) → (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2, then CNOT → (|00⟩+|11⟩)/√2 on q[0],q[1]
- After `bellpair(q[2], q[3])`: Same process yields (|00⟩+|11⟩)/√2 on q[2],q[3]
- Final state: ½(|0000⟩+|0011⟩+|1100⟩+|1111⟩)
- Measurements: 25% probability each for |0000⟩, |0011⟩, |1100⟩, |1111⟩ ✓

# ISQ training COT RAG corpus: quantum_algorithms shard 97

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3794

- task_id: `isqTrain/3794`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4042`

### Prompt

Write isQ code for the following quantum task: Deutsch-Jozsa for a 3-input balanced oracle with truth table [0, 0, 1, 1, 0, 0, 1, 1]. Use for loops for Hadamard application. Measure all 4 qubits.

### Chain-of-thought reasoning

Let me analyze the Deutsch-Jozsa circuit for a 3-input balanced oracle with truth table [0, 0, 1, 1, 0, 0, 1, 1].

1. The goal is to determine whether the oracle f is constant or balanced using the Deutsch-Jozsa algorithm.

2. We need 4 qubits: 3 input qubits (q[0], q[1], q[2]) and 1 output qubit (q[3]).

3. Step-by-step state evolution:

Initial state: |0000>

After X(q[3]): |0001>

After H(q[3]): |000⟩|−⟩

After Hadamard on all 4 qubits (H on q[0], q[1], q[2], q[3]):
- The output qubit q[3] is already in |−⟩, H|−⟩ = |1⟩
- The input qubits get H|0⟩ = |+⟩ each
- State: (1/2√2)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)|1⟩

Wait, let me redo this more carefully.

Initial state: |0000⟩

After X(q[3]): |0001⟩

After H(q[3]): |000⟩(|0⟩-|1⟩)/√2 = |000⟩|−⟩

After H on q[0], q[1], q[2] (the first 3 qubits):
State becomes: (1/2√2) Σ_x |x⟩|−⟩
where x ranges from 000 to 111.

Actually, H is applied to all 4 qubits in the loop:
for i in 0:3 { H(q[i]); }

Wait, 0:3 in isQ means i = 0, 1, 2, 3 (inclusive). So H is applied to all 4 qubits.

After H(q[0]): (|0⟩+|1⟩)/√2 |001⟩... wait, let me be more careful.

After X(q[3]): |0001⟩

After H(q[3]): |000⟩(|0⟩-|1⟩)/√2

After H(q[0]): (|0⟩+|1⟩)/√2 |00⟩(|0⟩-|1⟩)/√2

After H(q[1]): (1/2)(|00⟩+|01⟩+|10⟩+|11⟩)|0⟩(|0⟩-|1⟩)/√2

Wait, I need to track this more carefully with all 4 qubits.

After X(q[3]) and H(q[3]):
State = |000⟩(|0⟩-|1⟩)/√2

Now we apply H to q[0], q[1], q[2] (and also q[3] since the loop is 0:3):

After H on q[0]:
State = (|0⟩+|1⟩)/√2 ⊗ |00⟩ ⊗ (|0⟩-|1⟩)/√2
= (1/√2)(|0⟩+|1⟩)|00⟩(|0⟩-|1⟩)/√2

After H on q[1]:
State = (1/2)(|0⟩+|1⟩)(|0⟩+|1⟩)|0⟩(|0⟩-|1⟩)/√2

After H on q[2]:
State = (1/2√2)(|0⟩+|1⟩)(|0⟩+|1⟩)(|0⟩+|1⟩)(|0⟩-|1⟩)/√2
= (1/4) Σ_x |x⟩ (|0⟩-|1⟩)

where x ranges over 3-bit strings.

After H on q[3]:
H(|0⟩-|1⟩)/√2 = (|0⟩+|1⟩ - |0⟩+|1⟩)/2 = |1⟩

So state becomes: (1/2√2) Σ_x |x⟩|1⟩

Now apply oracle f:
The oracle f maps |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩

With the truth table [0, 0, 1, 1, 0, 0, 1, 1]:
- f(000) = 0
- f(001) = 0
- f(010) = 1
- f(011) = 1
- f(100) = 0
- f(101) = 0
- f(110) = 1
- f(111) = 1

So the oracle applies

## isqQA/quantum_algorithms/118_math_derivation

- task_id: `isqQA/quantum_algorithms/118_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `math_derivation`, `algorithm`, `量子振幅估计`
- source: `qa_pipeline`
- dataset_index: `2956`

### Prompt

请详细推导无相位估计的量子振幅估计算法的核心数学过程。假设我们有一个作用在$n$个量子比特上的量子算子$A$，它能够以如下方式制备叠加态：$A|0\rangle^{\otimes n} = \sqrt{1-a}|\psi_0\rangle + \sqrt{a}|\psi_1\rangle$，其中$a \in (0,1)$是我们希望估计的未知概率，且$|\psi_0\rangle$和$|\psi_1\rangle$是相互正交的量子态。请利用算子代数和几何相位的性质，严密推导系统在应用$m$次量子振幅放大迭代算子$Q = -A S_0 A^{-1} S_{\chi}$（其中$S_0$和$S_{\chi}$分别为关于零态和目标子空间的条件相移）后，量子态的演化过程，并说明如何从中提取出高精度的$a$的估计值。

### Reference answer

<think>
首先，将高维量子态投影到由好态和坏态张成的二维子空间中，引入参数 $\theta = 2\arcsin(\sqrt{a})$，将概率 $a$ 的估计转化为角度 $\theta$ 的估计问题。

其次，利用几何代数解析量子振幅放大算子 $Q = -AS_0A^{-1}S_{\chi}$。分析其组成部分：$S_{\chi}$ 相当于关于好态基矢的反射，而 $-AS_0A^{-1}$ 等效于关于初始态 $A|0\rangle$ 的反射。根据几何性质，两次反射的复合等效于一次旋转，且旋转角度为两基矢夹角的两倍，即 $\theta$。

接着，推导多次迭代的演化。应用 $m$ 次 $Q$ 算子相当于将系统的态矢量在二维空间中连续旋转 $m$ 次，总旋转角为 $m\theta$。由此可写出演化后的态，并得出测量得到好态的概率为 $\sin^2((2m+1)\theta/2)$。

最后，说明无相位估计的提取思路。通过设置一系列不同的迭代次数 $m$（如 $2^0, 2^1, ..., 2^k$），多次运行量子电路并统计好态的出现频率，得到不同深度下的概率分布。利用经典的最大似然估计（MLE）或其他统计算法，拟合这些带有正弦周期性的测量结果，即可高精度地求解出 $\theta$，进而计算出目标概率 $a$。
</think>

无相位估计的量子振幅估计是量子机器学习和金融衍生品定价中的核心算法。为了严密推导其数学过程，我们首先需要将目标态和好态的叠加转化为一个等效的二态系统，并分析格罗弗迭代算子的几何意义。

设算子$A$作用在初始态$|0\rangle^{\otimes n}$上，制备出包含目标子空间叠加的态：
$$ A|0\rangle = \sqrt{1-a}|\psi_0\rangle + \sqrt{a}|\psi_1\rangle $$
这里我们定义两个正交基构成的二维子空间，令角度$\theta$满足$\sin(\theta/2) = \sqrt{a}$，即$\theta = 2\arcsin(\sqrt{a})$。我们可以将初始态重写为：
$$ |\Psi\rangle = A|0\rangle = \cos\frac{\theta}{2}|\psi_0\rangle + \sin\frac{\theta}{2}|\psi_1\rangle $$

量子振幅放大算子定义为 $Q = -A S_0 A^{-1} S_{\chi}$。
1. **$S_{\chi}$ 的作用**：这是关于“好态”的条件相移算子，定义为$S_{\chi} = I - 2|\psi_1\rangle\langle\psi_1|$。作用在态上时，它保持$|\psi_0\rangle$不变，而对$|\psi_1\rangle$引入$-1$的相位，等效于在二维空间中关于态$|\psi_0\rangle$所在的轴进行反射。
2. **$-A S_0 A^{-1}$ 的作用**：$S_0 = I - 2|0\rangle\langle 0|$ 是关于全零态的反射算子。因此，$-A S_0 A^{-1}$ 作用在由$\{|\psi_0\rangle, |\psi_1\rangle\}$张成的子空间中，等效于关于初始叠加态 $|\Psi\rangle$ 的反射。

根据反射与旋转的几何关系，两次连续的反射等效于一次旋转。算子 $Q$ 在该二维子空间中，相当于将系统的状态矢量朝着$|\psi_1\rangle$的方向旋转角度 $\theta$。在矩阵表示下：
$$ Q = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix} $$
经过 $m$ 次 $Q$ 算子的迭代后，系统的量子态演化为：
$$ |\Psi_m\rangle = Q^m |\Psi\rangle = \cos\left(\frac{2m+1}{2}\theta\right)|\psi_0\rangle + \sin\left(\frac{2m+1}{2}\theta\right)|\psi_1\rangle $$

随后，我们在该态上进行计算基的测量。测得“好态”（对应于成功概率 $a$）的概率 $p_m$ 严格等于：
$$ p_m = \sin^2\left(\frac{2m+1}{2}\theta\right) $$
在无相位估计的变体中，为了避免使用昂贵的量子傅里叶变换和额外的计数寄存器，我们通过非等距地增加 $m$ 的值（例如呈指数级增长序列 $m \in \{0, 1, 2, 4, 8, \dots, 2^J\}$），并多次测量以获取对应深度下的成功频率 $\hat{p}_m$。利用最大似然估计（MLE），结合不同深度 $m$ 下观测到的概率分布，我们构建似然函数并拟合出最可能的相位参数 $\theta^*$。由于 $a = \sin^2(\theta/2)$，高精度的 $\theta^*$ 直接给出高精度的估计值 $a^*$。这种变体算法在降低量子线路深度的同时，依然能够在总查询复杂度为 $M$ 的情况下达到 $O(1/M)$ 的估计误差，实现了对经典蒙特卡洛采样的二次量子加速。

## isqTrain/704

- task_id: `isqTrain/704`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2819`

### Prompt

Create an isQ quantum circuit that implements the integer_comparator pattern but with a different initial state preparation (flip q[[0, 1]] -> q[2]).

### Chain-of-thought reasoning

The user wants me to explain a quantum circuit that implements an integer comparator pattern.

Let me analyze the circuit:
1. We have 3 qubits: q[0], q[1], q[2]
2. Initial state preparation: X(q[2]) flips q[2] to |1>
3. Then CNOT(q[1], q[2]) - if q[1] is |1>, flip q[2]

Wait, the prompt says "flip q[[0, 1]] -> q[2]" which means we should flip q[0] and q[1] instead of q[2] as In the implementation.

So the circuit should:
1. X(q[0]) - flip q[0] to |1>
2. X(q[1]) - flip q[1] to |1>
3. CNOT(q[1], q[2]) - if q[1] is |1>, flip q[2]

Let me trace through:
- Initial: |000>
- After X(q[0]): |100>
- After X(q[1]): |110>
- After CNOT(q[1], q[2]): |111> (q[2] flips because q[1] is |1>)

Wait, but The circuit should X(q[2]) only, not flipping q[0] and q[1].

Let me re-read the prompt: "flip q[[0, 1]] -> q[2]" means the initial state preparation should flip q[0] and q[1] (encoding a=3 in binary), then use CNOT to compare.

Actually, Analyzing the circuit requirements more carefully:
- It only does X(q[2]) - this sets q[2] to |1>
- Then CNOT(q[1], q[2]) - this flips q[2] if q[1] is |1>

Since q[1] starts as |0>, CNOT doesn't change q[2], so q[2] remains |1>.

The measurement is on q[2], which gives |1> with probability 1.0.

But the prompt says "with a different initial state preparation (flip q[[0, 1]] -> q[2])". This is a bit confusing.

I think "flip q[[0, 1]] -> q[2]" means:
- Instead of flipping q[2], flip q[0] and q[1]
- So we encode a = 3 (binary 11) in q[0] and q[1]
- Then use CNOT to compare

Let me trace this new circuit:
1. X(q[0]): |100> (flipping q[0])
2. X(q[1]): |110> (flipping q[1])
3. CNOT(q[1], q[2]): |111> (q[2] flips because q[1] is |1>)

But wait, The implementation seems to measure q[2] and expects |1> with probability 1.0. If we flip q[0] and q[1] instead of q[2], the result should still be |1> on q[2] after the CNOT.

Actually, let me re-read The implementation again:

This is:
- Start with |000>
- X(q[2]): |001>
- CNOT(q[1], q[2]): |001> (q[1] is 0, so no flip)
- Measure q[2]: get 1 with probability 1.0

But the prompt says to do "flip q[[0, 1]] -> q[2]" which I interpret as:
- Flip q[0] and q[1] to encode the integer
- Then use CNOT to propagate to q[2]

So the new circuit would be:

Let me trace:
- Start: |000>
- X(q[0]): |100>
- X(q[1]): |110>
- CNOT(q[1], q[2]): |111>
- Measure q[2]: get 1 with probability 1.0

This makes sense! The comparator checks if the encoded integer (3 in binary = 11) is >= 2 (has MSB set), and the result flag is stored in q[2].

Now let me write the reasoning:

## Reasoning
1. The goal is to implement an integer comparator that encodes a=3 (binary 11) in q[0] and q[1], then checks if a >= 2 via CNOT.
2. We need

## isqTrain/726

- task_id: `isqTrain/726`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2861`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the ripple_carry_adder pattern using q[6] -> q[8]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this ripple-carry adder circuit carefully.

The circuit uses 8 qubits:
- q[0], q[1]: input a (2-bit number)
- q[2], q[3]: input b (2-bit number)
- q[4], q[5]: carry/ancilla bits
- q[6], q[7]: additional qubits (ground state)

The inputs are:
- a = 3 (binary 11): q[0]=1, q[1]=1
- b = 1 (binary 01): q[2]=1, q[3]=0

Let me trace through the state evolution:

Initial state: |00000000⟩

After X(q[0]), X(q[1]), X(q[2]):
|11100000⟩

Now let me label the qubits: |a1, a0, b1, b0, c0, c1, q6, q7⟩

So the state is: a1=1, a0=1, b1=0, b0=1, c0=0, c1=0, q6=0, q7=0
= |11010000⟩

Wait, let me re-read. q[0]=a0, q[1]=a1, q[2]=b0, q[3]=b1

After X on q[0], q[1], q[2]:
|a1=1, a0=1, b1=0, b0=1, ...⟩
= |1,1,0,1,0,0,0,0⟩

Bit 0 computation:
- Toffoli(q[0], q[2], q[4]): c0 = a0 AND b0 = 1 AND 1 = 1
  State: |1,1,0,1,1,0,0,0⟩

- CNOT(q[0], q[2]): b0 = a0 XOR b0 = 1 XOR 1 = 0
  State: |1,1,0,0,1,0,0,0⟩

Bit 1 computation:
- Toffoli(q[1], q[3], q[5]): c1 += a1 AND b1 = 1 AND 0 = 0
  State: |1,1,0,0,1,0,0,0⟩ (unchanged)

- Toffoli(q[1], q[4], q[5]): c1 += a1 AND c0 = 1 AND 1 = 1
  State: |1,1,0,0,1,1,0,0⟩

- Toffoli(q[3], q[4], q[5]): c1 += b1 AND c0 = 0 AND 1 = 0
  State: |1,1,0,0,1,1,0,0⟩ (unchanged)

- CNOT(q[1], q[3]): b1 = a1 XOR b1 = 1 XOR 0 = 1
  State: |1,1,1,0,1,1,0,0⟩

- CNOT(q[4], q[3]): b1 = b1 XOR c0 = 1 XOR 1 = 0
  State: |1,1,0,0,1,1,0,0⟩

Wait, that gives sum = 00 with carry = 1, which would be 3 + 1 = 4? No wait, sum0 is in q[2], sum1 is in q[3], and carry_out is in q[5].

After all operations:
q[2] = 0 (sum0)
q[3] = 0 (sum1)  
q[5] = 1 (carry_out)
q[6] = 0
q[7] = 0

So the measured bits are: q[2]=0, q[3]=0, q[5]=1, q[6]=0, q[7]=0

The predicted output {|00100>: 1.0}. With 5 qubits measured, the bitstring ordering has earlier measured qubit = higher bit.

So q[2] is the highest bit (bit 4), q[3] is bit 3, q[5] is bit 2, q[6] is bit 1, q[7] is bit 0.

|00100⟩ means: q[2]=0, q[3]=0, q[5]=1, q[6]=0, q[7]=0

So 3 + 1 = 4, which in binary (3 bits for result) is 100. The sum bits

## isqTrain/3805

- task_id: `isqTrain/3805`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1385`

### Prompt

用isQ实现4-bit Bernstein-Vazirani to find secret s=1011. Use oracle keyword, for loops for Hadamard. Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement the 4-bit Bernstein-Vazirani algorithm to find the secret string s=1011.
Qubits: 5 total (q[0]-q[3] for input, q[4] for oracle output). All 5 are measured.
1. Initialize |00000>, apply X to q[4] -> |00001>.
2. Apply H to q[4] -> |0000->.
3. Apply H to q[0]-q[3] -> (1/4) Σ|x>|->.
4. Oracle f computes s·x mod 2, kicking the phase to the top register -> (1/4) Σ(-1)^(s·x)|x>|->.
5. Apply H to q[0]-q[3], which reveals s -> |1011>|->.
Expected measurements: The input qubits deterministically read 1011 (s). The ancilla qubit is in |->, yielding a 50% chance for |0> and 50% for |1>, giving final states |10110> and |10111> with 0.5 probability each.

## isqTrain/4062

- task_id: `isqTrain/4062`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1122`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// Bernstein-Vazirani: find secret string s = 000
oracle f(3, 1) = [0, 0, 0, 0, 0, 0, 0, 0];
qbit q[4];  // 3 input + 1 output

procedure main() {
    // Prepare |->  on output qubit
    X(q[3]);
    H(q[3]);
    // Hadamard on input qubits
    for i in 0:3 {
        H(q[i]);
    }
    // Apply BV oracle
    f(q[0], q[1], q[2], q[3]);
    // Final Hadamard on inputs
    for i in 0:3 {
    // BUG: missing gate here
    }
    // Measure inputs to reveal secret string
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Bug fixing in isQ quantum code (Bernstein-Vazirani algorithm).
    *   **Input:** Buggy code, Corrected code, predicted output.
    *   **Format requirement:** "## Bug Analysis" followed by 1. Bug description, 2. Fix description, 3. Brief state evolution.
    *   **Constraints:** Concise (3-15 lines), no code blocks, precise step-by-step reasoning using Dirac notation.

2.  **Analyze the Bug:**
    *   **Buggy code snippet:**
        
    *   **Corrected code snippet:**
        
    *   **Bug:** The final Hadamard gates on all qubits are missing in the loop body.
    *   **Why it's a bug:** Bernstein-Vazirani requires a final Hadamard transform on the input qubits (and sometimes output depending on specific formulation, but here it's applied to all qubits) to map the phase-encoded secret string back into the computational basis.

3.  **Analyze State Evolution (Corrected):**
    *   Initial: $|0000\rangle$
    *   After X and H on q[3]: $|000\rangle \otimes |-\rangle$
    *   After H on q[0:3]: $|+++\rangle \otimes |-\rangle$
    *   Oracle $f$ (constant 0, secret $s=000$): $|+++\rangle \otimes |-\rangle$ (phase kickback is trivial since $s=000$, so $(-1)^{x \cdot s} = 1$).
    *   Final H on q[0:3]: H applied to $|+\rangle$ gives $|0\rangle$. So we get $|0000\rangle \otimes |-\rangle$.
    *   The predicted measurement probabilities are $\{|0000\rangle: 0.5, |0001\rangle: 0.5\}$. Let's trace carefully.
    *   Ah, $|-\rangle$ measured is 50% 0, 50% 1. So if the first 3 qubits are $|000\rangle$ and the 4th is $|-\rangle$, the measurement results are $|0000\rangle$ and $|0001\rangle$ with equal probability! This perfectly matches the predicted output.

4.  **Draft the Bug Analysis:**
    *   *What the bug is:* The final `for` loop is missing the Hadamard gate (`H(q[i])`) in its body.
    *   *What the fix is:* Add `H(q[i]);` inside the final `for i in 0:3` loop to apply the inverse Hadamard transform.
    *   *State evolution:*
        *   Start: $|0000\rangle$.
        *   Prepare output: $|000\rangle|-\rangle$.
        *   Initial Hadamards: $|+++\rangle|-\rangle$.
        *   Oracle (s=000): State remains $|+++\rangle|-\rangle$.
        *   Final Hadamards: $|000\rangle|-\rangle$.
        *   Measure: Collapses to $|0000\rangle$ or $|0001\rangle$ (50% each) because q[3] is in $|-\rangle$, yielding the predicted output.

5.  **Refine and Format:** Ensure no markdown code blocks for isQ are used. Keep it under 15 lines. Use precise language.

    *Drafting text:*
    ## Bug Analysis
    1. **What the bug is**: The final `for i in 0:3` loop is missing the Hadamard gate (`H(q[i])`) in its body, preventing the transformation of the phase-encoded secret string back into the computational basis.
    2. **What the fix is**: Add `H(q[i]);` inside the final loop body to apply the final Hadamard transform to all qubits.
    3. **State evolution of the corrected circuit**:
       - Initial state: $|0000\rangle$.
       - Prepare output qubit and apply initial Hadamards: Transforms inputs to $|+\rangle$ and output to $|-\rangle$, yielding $|+++\rangle|-\rangle$.
       - Apply oracle ($s=000$): The state remains $|+++\rangle

## isqTrain/793

- task_id: `isqTrain/793`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `227`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[5];

procedure main() {
    // Set polynomial a(x) = 1+x: a0=1, a1=1
    X(q[0]);
    X(q[1]);
    // Set polynomial b(x) = 1: b0=1
    X(q[2]);
    // Multiply: p0 = a0 AND b0 (GF(2) product constant term)
    Toffoli(q[0], q[2], q[3]);
    // p1 = a1 AND b0 (GF(2) product x-coefficient)
    Toffoli(q[1], q[2], q[4]);
    // Measure product coefficients
    M(q[3]);
    M(q[4]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit starts with 5 qubits in $|0\rangle$. It applies X gates to q[0], q[1], and q[2]. It then applies a Toffoli gate with controls q[0], q[2] and target q[3], followed by a Toffoli gate with controls q[1], q[2] and target q[4]. Finally, it measures q[3] and q[4].
2. **Evolution:** 
   - Initial state: $|00000\rangle$
   - After X gates on q[0,1,2]: $|11100\rangle$
   - After Toffoli(0,2,3): Since q[0] and q[2] are $|1\rangle$, q[3] flips to $|1\rangle$. State becomes $|111

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqEval/285. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1291

- task_id: `isqTrain/1291`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `225`

### Prompt

I need an isQ program to implements a variant of the fourier_checking pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this circuit carefully.

The circuit is a Fourier checking (Forrelation) variant on 5 qubits, but only qubits 0, 1, 2 are actively used. Qubits 3 and 4 remain in |0⟩ throughout.

Let me trace through the state evolution for the active qubits (q[0], q[1], q[2]):

**Step 1: Initial state**
|000⟩

**Step 2: First H layer**
H⊗3 |000⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

**Step 3: T gates on all three qubits**
T applies phase e^(iπ/4) to |1⟩ state. So T⊗3 applies:
- |000⟩: phase 1
- |001⟩, |010⟩, |100⟩: phase e^(iπ/4)
- |011⟩, |101⟩, |110⟩: phase e^(iπ/2) = i
- |111⟩: phase e^(i3π/4)

State: (1/√8)(|000⟩ + e^(iπ/4)(|001⟩ + |010⟩ + |100⟩) + i(|011⟩ + |101⟩ + |110⟩) + e^(i3π/4)|111⟩)

**Step 4: CZ(q[0], q[1]) and CZ(q[1], q[2])**
CZ applies a -1 phase when both qubits are |1⟩.

CZ(q[0], q[1]) flips sign when q[0]=1 AND q[1]=1: affects |110⟩, |111⟩
CZ(q[1], q[2]) flips sign when q[1]=1 AND q[2]=1: affects |011⟩, |111⟩

After both CZ gates:
- |011⟩: i → -i
- |110⟩: i → -i
- |111⟩: e^(i3π/4) → gets -1 from CZ(0,1) and -1 from CZ(1,2), so +e^(i3π/4)

State: (1/√8)(|000⟩ + e^(iπ/4)(|001⟩ + |010⟩ + |100⟩) - i(|011⟩ + |110⟩) + i|101⟩ + e^(i3π/4)|111⟩)

Wait, let me be more careful. Let me track each basis state:

|000⟩: +1 (no change)
|001⟩: +e^(iπ/4) (T on q2 only)
|010⟩: +e^(iπ/4) (T on q1 only)
|011⟩: +ie^(-1 from CZ(1,2)) = -i
|100⟩: +e^(iπ/4) (T on q0 only)
|101⟩: +i (T on q0 and q2, no CZ affects this)
|110⟩: +ie^(-1 from CZ(0,1)) = -i
|111⟩: +e^(i3π/4)e^(-1 from CZ(0,1))e^(-1 from CZ(1,2)) = e^(i3π/4)·(+1) = e^(i3π/4)

Wait, e^(-1) means multiplying by -1. So:

|111⟩: e^(i3π/4) × (-1) × (-1) = e^(i3π/4)

So state after oracle f:
(1/√8)(|000⟩ + e^(iπ/4)|001⟩ + e^(iπ/4)|010⟩ - i|011⟩ + e^(iπ/4)|100⟩ + i|101⟩ - i|110⟩ + e^(i3π/4)|111⟩)

**Step 5: Middle H layer**
H⊗3 on this state. This is getting complex. Let me compute numerically.

Let me define the state as a vector indexed by (q0, q1, q2):

amp[000] = 1
amp[001] = e^(iπ/4)
amp[010] = e^(iπ/4)
amp[011] = -i
amp[100] = e^(iπ/4)
amp[101] = i
amp[110] = -i
amp[111] = e^(i3π/4)

Now H⊗3 = H⊗H⊗H. Each H maps:
H|0⟩ = (|0⟩+|1⟩)/√2

## isqExpand/algo/52

- task_id: `isqExpand/algo/52`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `mid_circuit_measurement`, `basis_change`
- source: `isq_expansion`
- dataset_index: `3604`

### Prompt

实现以下量子计算任务（使用isQ）：implements quantum teleportation to teleport the state |0> from Alice's qubit (q[0]) to Bob's qubit (q[2]). Use q[1] and q[2] as a shared Bell pair. Perform mid-circuit measurement on q[0] and q[1], then apply classical corrections (X and Z) on q[2] conditioned on the measurement results. Finally measure q[2]. After teleportation, Bob's qubit should be in state |0>, so q[2] always measures 0.

### Chain-of-thought reasoning

## Reasoning
Goal: Teleport |0> from q[0] to q[2].

1. q[0] starts in |0> (default). No preparation needed.
2. Create Bell pair |Phi+> = (|00>+|11>)/sqrt(2) on q[1],q[2]: H(q[1]), CNOT(q[1],q[2]).
3. Full 3-qubit state: |0> (x) (|00>+|11>)/sqrt(2) = (|000>+|011>)/sqrt(2).
4. CNOT(q[0],q[1]): no change since q[0]=0.
5. H(q[0]): q[0] -> (|0>+|1>)/sqrt(2).
   State: ((|0>+|1>)|00> + (|0>+|1>)|11>)/2 = (|000>+|100>+|011>+|111>)/2.
6. Regroup by m0,m1:
   - m0=0,m1=0: q[2]=|0>. Correction: none -> |0>
   - m0=1,m1=0: q[2]=|0>. Correction: Z -> Z|0>=|0>
   - m0=0,m1=1: q[2]=|1>. Correction: X -> X|1>=|0>
   - m0=1,m1=1: q[2]=|1>. Correction: XZ -> ZX|1>=Z|0>=|0>
7. All cases yield q[2]=|0>. Measurement always gives 0.

stdout_match mode because mid-circuit measurement makes --probs unreliable.

## isqTrain/1938

- task_id: `isqTrain/1938`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_procedures`, `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5016`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[2];
procedure my_oracle() {
    X(q[1]);
    CZ(q[0], q[1]);
    X(q[1]);
}
procedure diffuser() {
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
}
procedure main() {
    H(q[0]); H(q[1]);
    my_oracle();
    diffuser();
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Predict the probability distribution of the isQ program's measurement outcomes.
    *   **Format:** "## Circuit Analysis" followed by step-by-step reasoning, ending with the probability distribution. 3-8 lines for simple, up to 15 lines for complex.
    *   **Notation:** Dirac notation.
    *   **Input Program:** A standard Grover's algorithm for 2 qubits.

2.  **Analyze the isQ Program:**
    *   `qbit q[2];` initializes qubits to |00>.
    *   `main()`:
        *   `H(q[0]); H(q[1]);` -> Creates superposition: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        *   `my_oracle();`:
            *   `X(q[1]);` -> Flips q[1].
            *   `CZ(q[0], q[1]);` -> Controlled-Z.
            *   `X(q[1]);` -> Flips q[1] back.
            *   This sequence implements a controlled-Z sandwiched by X gates on q[1]. This flips the sign of the amplitude for the state where q[0] is in |0> (because CZ applies -1 if both are |1>, but X on q[1] makes |0> look like |1> to the CZ). Specifically, `X(CZ)X` applies Z to q[0] controlled by q[1] being |0>. Wait, let's trace exactly.
            *   Initial state for oracle: $|\psi\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
            *   Apply X on q[1]: $\frac{1}{2}(|01\rangle + |00\rangle + |11\rangle + |10\rangle)$
            *   Apply CZ(q[0], q[1]): $\frac{1}{2}(|01\rangle + |00\rangle + |11\rangle - |10\rangle)$. (CZ applies -1 to |11>). Wait, CZ(q[0], q[1]) applies -1 when *both* are |1>. So |11> gets -1.
            *   Apply X on q[1]: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
            *   Wait, the prompt says {'10': 1.0} is expected! Let me re-evaluate the oracle.
            *   Let's trace the oracle state again.
            *   State before oracle: $0.5 |00\rangle + 0.5 |01\rangle + 0.5 |10\rangle + 0.5 |11\rangle$
            *   Apply X to q[1]: $0.5 |01\rangle + 0.5 |00\rangle + 0.5 |11\rangle + 0.5 |10\rangle$
            *   Apply CZ: $0.5 |01\rangle + 0.5 |00\rangle - 0.5 |11\rangle + 0.5 |10\rangle$
            *   Apply X to q[1]: $0.5 |00\rangle + 0.5 |01\rangle - 0.5 |10\rangle + 0.5 |11\rangle$
            *   So the marked state is $|10\rangle$. State is $|\psi'\rangle = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle + |11\rangle)$.
        *   `diffuser();`:
            *   Apply H to both: $H^{\otimes 2} |\psi'\rangle$.
            *   Let's calculate $H^{\otimes 2} \frac{1}{2}(1, 1, -1, 1)^T$.
            *   $H^{\otimes 2} = \frac{1}{2} \begin{pmatrix} 1 & 1 & 1 & 1 \\ 1 & -1 & 1 & -1 \\ 1 & 1 & -1 & -1 \\ 1 & -1 & -1 & 1 \end{pmatrix}$.
            *   Row 1 (|00>): 0.25 * (1+1-1+1) = 0.5
            *   Row 2 (|01>): 0.25 * (1-1-1-1) = -0.5

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'Grover search |10>'}

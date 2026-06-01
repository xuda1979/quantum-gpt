# ISQ training COT RAG corpus: quantum_algorithms shard 158

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/59

- task_id: `isqExpand/algo/59`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `mid_circuit_measurement`, `basis_change`
- source: `isq_expansion`
- dataset_index: `5332`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);

    H(q[1]);
    CNOT(q[2], q[1]);

    CNOT(q[0], q[1]);
    H(q[0]);

    int m0 = M(q[0]);
    int m1 = M(q[1]);

    if (m1 == 1) {
        X(q[2]);
    }
    if (m0 == 1) {
        Z(q[2]);
    }

    M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

The bug is in Bell pair creation: CNOT(q[2], q[1]) has the wrong direction.

Correct: H(q[1]) puts q[1] in |+>, then CNOT(q[1], q[2]) creates |Phi+> = (|00>+|11>)/sqrt(2) on q[1],q[2]. Control must be q[1].

With the bug (CNOT(q[2], q[1])), q[2] is the control and q[1] is the target. Since q[2] starts in |0>, CNOT does nothing, leaving q[1] in |+> and q[2] in |0> -- no entanglement is created.

Fix: Change CNOT(q[2], q[1]) to CNOT(q[1], q[2]).

After fix, standard teleportation of |1> works correctly.

## isqTrain/2692

- task_id: `isqTrain/2692`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `435`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
oracle bool[1] constant(bool a[4]) {
    bool res[] = [true];
    return res;
}
qbit q[4], anc[1];

procedure main()
{
    X(anc[0]);
    H(q);
    H(anc[0]);
    constant(q, anc);
    H(q);
    print M(q);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1.  **Initial state**: The 4 main qubits `q` and 1 ancilla `anc` start in $|0000\rangle|0\rangle$.
2.  **X(anc[0])**: Flips the ancilla to $|1\rangle$. The state is $|0000\rangle|1\rangle$.
3.  **H(q) and H(anc)**: Hadamard gates put all qubits in superposition. The state becomes $\frac{1}{4} \sum_{x=0}^{15} |x\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
4.  **constant oracle**: This oracle calculates $f(x) = 1$ for all $x$. It flips the ancilla state. Since the ancilla is in $|-\rangle$, the phase flips by -1. The state becomes $-\frac{1}{4} \sum_{x=0}^{15} |x\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
5.  **H(q)**: Applying Hadamard gates to `q` again performs an inverse quantum Fourier transform. For a constant oracle, all amplitudes constructively interfere into the $|0000\rangle$ state.
6.  **Final state**: The main qubits `q` collapse exactly to $|0000\rangle$.

Predicted probabilities: {'0000': 1.0}

### Reference answer

{'predicted_probs': {'0000': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/755

- task_id: `isqTrain/755`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2673`

### Prompt

Implement the following in isQ: implements the modular_adder pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

The user wants to write an isQ program implementing a modular_adder pattern with a different initial state preparation.
Wait, the prompt says "flip q[[0]] -> q[1]".
The circuit should:
`X(q[1]);` to encode a = 1.
Wait, `flip q[[0]] -> q[1]` might mean "flip q[0] instead of q[1]".
Let me look at the expected measurement probabilities: `{|00>: 1.0}`.
Wait, if I start with |000>, flip q[0] -> |100> (assuming q[0] is MSB) or |001> (assuming q[0] is LSB).
In the implementation:
`Toffoli(q[0], q[1], q[2]);` (so q[0], q[1] are the register, q[2] is ancilla).
If a=1, X(q[1]) -> |01>.
Wait, if q[0] is MSB, then X(q[1]) means |10>? No, standard notation is q[0] is MSB. Let's assume q[0] is LSB.
If q[0] is LSB, X(q[1]) -> |010>.
Wait, let's trace the reference:
Start: |000>.
X(q[1]): |010> (value = 2)
Wait, The implementation says:
X(q[1]); -> value = 1. If q[1] is MSB, then it's |010>.
Then "First flip LSB": Wait, reference has no X gate?
Ah, reference:
`X(q[1]);`
`nctrl X(q[0], q[1]);` -> Toffoli with negated control? Wait, `nctrl X(q[0], q[1])` in standard isQ is `inv ctrl X(q[0], q[1])`? No, it means control is negated?
Actually, the reference code has:
`nctrl X(q[0], q[1]);`
Wait, what is `nctrl X`? Is it negative controlled X? So if q[0] is 0, flip q[1].
Wait, if initial is |010>.
Then `nctrl X(q[0], q[1])` -> q[0] is 0, so it flips q[1].
|010> -> |000>.
Then Toffoli(q[0], q[1], q[2]) -> |000>.
CNOT(q[2], q[0]) -> |000>.
CNOT(q[2], q[1]) -> |000>.
Outcome is |00>.
Wait, if the prompt asks to "flip q[[0]] -> q[1]", does it mean the user prompt for generating this task was "Write an isQ program that implements the modular_adder pattern but with a different initial state preparation (flip q[0] instead of q[1])." ?
Wait, if I change the initial state to flip q[0] instead of q[1]:
Initial state: |001>.
Then `nctrl X(q[0], q[1])` -> q[0] is 1, so nctrl does NOT flip q[1].
Toffoli(q[0], q[1], q[2]) -> q[0]=1, q[1]=0 -> does nothing.
CNOT(q[2], q[0]) -> does nothing.
CNOT(q[2], q[1]) -> does nothing.
Final state: |001>. Outcome: |01> if q[0] and q[1] are measured? Wait, The resulting probabilities should be {|00>: 1.0}.
Let me re-evaluate circuit implementation.
If circuit implementation has X(q[1]):
Initial: |000>.
X(q[1]) -> |010>.
nctrl X(q[0], q[1]) -> wait, what if `nctrl` means something else? No, negative control. If q[0] == 0, flip q[1].
So |010> -> |000>.
Then Toffoli(q[0], q[1], q[2]) -> |000>.
CNOT(q[2], q[0]) -> |000>.
CNOT(q[2], q[1]) -> |000>.
Measured q[0], q[1] -> 0, 0. So outcome is |00>.

What if I flip q[0] instead of q[1]?
Start |000>. X(q[0]) -> |001>.
nctrl X(q[0], q[1]) -> q[0] is 1, so no flip. State remains |001>.
Toffoli(q[0], q[1], q[2]) -> |001>.
CNOT(q[2], q[0]) -> |

## isqTrain/4644

- task_id: `isqTrain/4644`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2054`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];

procedure main() {
    
    X(q[1]);  // target different qubit

    
    
    
    

    
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(0.785398163397448, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);

    
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(0.785398163397448, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);

    
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a step-by-step reasoning for an isQ program predicting the probability distribution of measurement outcomes.
    *   Format: "## Circuit Analysis" followed by 1-4 sections (Operations, Step-by-step, Final state, Probabilities).
    *   Constraint: 3-8 lines for simple circuits, up to 15 for complex ones. Use Dirac notation. Output ONLY the analysis. End with the predicted probability distribution.
    *   Input program: An X gate on q[1], followed by a sequence of CNOT-Rz-CNOT gates and H-CNOT-Rz-CNOT-H blocks, repeated. Wait, let's look at the blocks. It looks like a Trotterized Ising model or a repetition of $e^{-i Z Z \theta}$ and $e^{-i X X \phi}$ interactions. Let's calculate exactly.
    *   Initial state: $|00\rangle$. X on q[1] makes it $|01\rangle$.
    *   Angles: 0.392699081698724 = $\pi/8$, 0.785398163397448 = $\pi/4$.

2.  **Analyze the Circuit Step-by-Step:**
    *   **Initial state:** $|00\rangle$
    *   `X(q[1])`: $|01\rangle$
    *   **Block 1:**
        *   `CNOT(q[0], q[1]); Rz(pi/8, q[1]); CNOT(q[0], q[1]);` -> This is equivalent to $e^{-i Z_0 Z_1 \pi/16}$ or something?
            Wait, $CNOT_{01} Rz(\theta)_1 CNOT_{01} = \exp(-i Z_0 Z_1 \theta / 2)$.
            Let's verify: $CNOT \cdot (I \otimes Rz(\theta)) \cdot CNOT$.
            $|00\rangle \to |00\rangle$, $|01\rangle \to |01\rangle$, $|10\rangle \to |11\rangle$, $|11\rangle \to |10\rangle$.
            So $Z_0 Z_1$ is mapped to $I \otimes Z$.
            Applying $I \otimes Rz(\theta)$ in the $Z \otimes Z$ basis applies a phase to $|10\rangle$ and $|11\rangle$.
            Wait, $Rz(\theta) = e^{-i Z \theta / 2}$.
            So it applies $e^{-i Z_1 \theta/2}$.
            Let's trace the state $|01\rangle$.
            $CNOT(|01\rangle) = |01\rangle$.
            $Rz(\pi/8)|01\rangle = e^{i \pi/16} |01\rangle$.
            $CNOT(|01\rangle) = |01\rangle$.
            So this block just applies a global phase to $|01\rangle$? Wait, $Rz(\theta) |1\rangle = e^{-i\theta/2} (-|1\rangle)$? No, $Rz(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$. So $Rz(\theta)|0\rangle = e^{-i\theta/2}|0\rangle$ and $Rz(\theta)|1\rangle = e^{i\theta/2}|1\rangle$.
            Wait, $CNOT_{01} Rz(\theta)_1 CNOT_{01} |01\rangle = CNOT Rz(\theta) |01\rangle = CNOT(e^{i\theta/2} |01\rangle) = e^{i\theta/2} |01\rangle$.
            Since we only have $|01\rangle$, and it doesn't mix with other states? Wait! Does $|01\rangle$ mix?
            Let's look at the **Block 2:**
            `H(q[0]); H(q[1]); CNOT(q[0], q[1]); Rz(pi/4, q[1]); CNOT(q[0], q[1]); H(q[0]); H(q[1]);`
            This is $H_0 H_1 \cdot ZZ(\pi/4) \cdot H_0 H_1 = XX(\pi/4)$.
            Let's trace $|01\rangle$:
            $H_0 H_1 |01\rangle = H_0 |0\rangle \ot

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 0.5000, P(|10>) = 0.5000.'}

## isqQA/quantum_algorithms/92_comparison

- task_id: `isqQA/quantum_algorithms/92_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `comparison`, `algorithm`, `Simon算法原理`
- source: `qa_pipeline`
- dataset_index: `2935`

### Prompt

在探讨隐含子群问题的量子解决方案时，Simon算法与Bernstein-Vazirani (BV) 算法常常被放在一起讨论。请从数学原理、布尔函数类型、查询复杂度对比以及适用场景等角度，深入分析Simon算法与Bernstein-Vazirani算法的区别与联系。同时，请提供一段使用isQ语言实现特定Simon问题实例的代码示例，并简要解释其中关键的量子干涉过程。

### Reference answer

Simon算法与Bernstein-Vazirani (BV) 算法都是求解隐藏结构问题的早期量子算法，它们在数学原理上同属于阿贝尔群上的隐含子群问题（HSP）的特例，且都利用了量子并行性和相位干涉来实现相对经典算法的指数级或线性加速。然而，两者在处理的具体布尔函数类型和目标上存在显著差异。

首先，从布尔函数类型和数学原理来看，BV算法针对的是一个线性布尔函数 $f(x) = a \cdot x \pmod 2$，其中 $a$ 是一个未知的秘密比特串。经典算法确定 $a$ 需要 $O(n)$ 次查询，而BV量子算法仅需 $1$ 次查询即可提取出 $a$。BV算法本质上是在寻找函数的“核”相关的特征向量。相反，Simon算法针对的是满足特定周期性的二对一函数，即存在一个非零秘密字符串 $s$，使得对于所有 $x$ 都有 $f(x) = f(x \oplus s)$。Simon算法的目标是找到这个周期 $s$。数学上，Simon算法是通过寻找与隐藏子群 $H = \{0, s\}$ 相互正交的向量来重建 $s$ 的。

其次，在查询复杂度和优缺点方面，BV算法实现了从经典 $O(n)$ 到量子 $O(1)$ 的加速，但适用条件苛刻（必须是精确的线性函数），在实际复杂问题中应用场景有限。Simon算法则实现了从经典 $O(2^{n/2})$ 到量子 $O(n)$ 的真正指数级加速。Simon算法的主要缺点是其依赖于黑盒函数必须严格满足二对一映射的承诺，且在量子线路测量后需要借助经典的高斯消元法来求解包含 $n-1$ 个独立方程的线性方程组。

最后，在适用场景上，BV算法更多作为展示量子干涉威力的教学工具；而Simon算法不仅适用于寻找函数周期，其核心思想更是直接启发了Shor算法的诞生——Shor算法中的质因数分解本质上就是将求阶问题转化为有限阿贝尔群上的周期寻找问题。

以下是使用isQ语言实现的Simon算法示例。假设输入为2个量子比特，隐藏周期 $s=11$。此时函数 $f(x)$ 实现的逻辑可以简化为 $f(x) = x_0 \oplus x_1$（当 $x=00, 11$ 时 $f=0$；当 $x=01, 10$ 时 $f=1$），满足 $f(x) = f(x \oplus 11)$。目标寄存器设为1个量子比特。

```isq
import std;

qbit q[2];
qbit out[1];

procedure main() {
    // 步骤1：对输入寄存器施加Hadamard门，创建均匀叠加态
    H(q[0]);
    H(q[1]);
    
    // 步骤2：施加Oracle U_f，计算 f(x) = x_0 XOR x_1
    // 这里的Oracle实现了满足周期 s=11 的二对一映射
    CNOT(q[0], out[0]);
    CNOT(q[1], out[0]);
    
    // 在标准Simon算法中，通常在此处不对out进行测量，而是直接对输入寄存器进行干涉
    // 步骤3：再次对输入寄存器施加Hadamard门，产生干涉
    H(q[0]);
    H(q[1]);
    
    // 步骤4：测量输入寄存器
    // 结果将必定满足 y · s = 0 (mod 2)，即测量结果只可能是 00 或 11
    M(q[0]);
    M(q[1]);
}
```

关键的量子干涉过程解释：在经过第一个Hadamard门和Oracle之后，输入寄存器和目标寄存器处于纠缠态。在标准Simon算法流程中，由于我们只关心输入寄存器，此时相当于输入寄存器的密度矩阵混合了各个计算基态。当我们在输入寄存器上施加第二个Hadamard门时，这相当于在计算基下进行了一次逆傅里叶变换。因为 $f(x) = f(x \oplus s)$，不同基态 $|x\rangle$ 和 $|x \oplus s\rangle$ 的概率幅会根据其与隐藏串 $s$ 的内积进行相位重组。具体而言，如果对于测量结果 $y$ 有 $y \cdot s = 1$，则相关概率幅会发生相消干涉（抵消为零）；而满足 $y \cdot s = 0$ 的概率幅则会相长干涉（叠加增强）。因此，最终的测量结果 $y$ 必定与 $s$ 正交，通过多次运行获取足够多的正交向量 $y$ 后，即可在经典计算机上通过高斯消元法唯一确定周期 $s$。

## isqTrain/762

- task_id: `isqTrain/762`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4999`

### Prompt

Implement a quantum circuit in isQ: implements the weighted_adder pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a weighted adder where input qubits q[0],q[1] (set to |1⟩) contribute weights 1 and 2 to sum qubits q[2],q[3] respectively, using H-CZ-H instead of CNOT.

2. **Qubits**: 4 total (q[0..3]); q[2] and q[3] are measured (2 output bits).

3. **State evolution**:
   - Start: |0000⟩ → after X(q[0]), X(q[1]): |1100⟩
   - **Weight 1 block** (CNOT equiv on q[2]):
     - H(q[2]): |1100⟩ → |11⟩⊗(|+0⟩) = |11⟩⊗(|00⟩+|10⟩)/√2
     - CZ(q[0],q[2]): flips sign when both |1⟩ → |11⟩⊗(|00⟩−|10⟩)/√2 = |11⟩⊗|−0⟩
     - H(q[2]): |−⟩→|1⟩ → |1110⟩
   - **Weight 2 block** (CNOT equiv on q[3]):
     - H(q[3]): |1110⟩ → |111+⟩ = |111⟩⊗(|0⟩+|1⟩)/√2
     - CZ(q[1],q[3]): → |111⟩⊗(|0⟩−|1⟩)/√2 = |111−⟩
     - H(q[3]): |−⟩→|1⟩ → |1111⟩

4. **Final state**: |1111⟩, so measuring q[2],q[3] yields |11⟩ with probability 1.0 — correctly encoding x₀+x₁

## isqTrain/1108

- task_id: `isqTrain/1108`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2237`

### Prompt

I need an isQ program to implements a compact variant of the simon_algorithm pattern using out[2] -> out[1]. The circuit should use a reduced qubit register.

### Chain-of-thought reasoning

The user wants a reasoning section for the given isQ code implementing Simon's algorithm with a reduced register where `out[2]` -> `out[1]`.
Wait, the prompt says "out[2] -> out[1]", which means 2 output qubits mapped to 1 output qubit. The reference code declares `qbit q[2];` and `qbit out[1];`. The oracle function is `bool[2] f(bool x[2])` returning 2 booleans, but the state is calculated on `out[1]`.

Let's trace the state evolution.
Initial state: |000> (q[0], q[1], out[0])
Hadamards on q[0], q[1]:
1/2 (|00> + |01> + |10> + |11>) |0>_out
Oracle `f(q, out)` is applied.
Wait, isQ `f(q, out)` maps the classical `f` to quantum oracle. The function returns `[false, x0_xor_x1]`.
For `x = 00`, f(x) = 00 (mod 2 = 0). out stays |0>.
For `x = 01`, f(x) = 01 (mod 2 = 1). out flips to |1>.
For `x = 10`, f(x) = 01 (mod 2 = 1). out flips to |1>.
For `x = 11`, f(x) = 00 (mod 2 = 0). out stays |0>.
State after oracle:
1/2 (|00>|0> + |01>|1> + |10>|1> + |11>|0>)
Notice that |00>|0> + |11>|0> = (|00> + |11>)|0>, and |01>|1> + |10>|1> = (|01> + |10>)|1>.
Hadamards on q[0], q[1]:
H|00> = 1/2 (|00>+|01>+|10>+|11>)
H|11> = 1/2 (|00>-|01>-|10>+|11>)
Sum: |00> + |11>.
H|01> = 1/2 (|00>-|01>+|10>-|11>)
H|10> = 1/2 (|00>+|01>-|10>-|11>)
Sum: |00> - |11>.
So the state is 1/2 ( (|00> + |11>)|0> + (|00> - |11>)|1> ) = 1/2 |00>(|0>+|1>) + 1/2 |11>(|0>-|1>).
We only measure q[0] and q[1].
Wait, if we measure q[0] and q[1], their states are exactly |00> and |11>.
Wait, is it?
Let's re-evaluate.
1/2 (|00> + |11>)|0> -> H tensored H gives 1/2 * 1/2 (|00>+|01>+|10>+|11> + |00>-|01>-|10>+|11>) |0> = 1/2 (|00> + |11>)|0>.
1/2 (|01> + |10>)|1> -> H tensored H gives 1/2 * 1/2 (|00>-|01>+|10>-|11> + |00>+|01>-|10>-|11>) |1> = 1/2 (|00> - |11>)|1>.
So total state is 1/2 |00>|0> + 1/2 |11>|0> + 1/2 |00>|1> - 1/2 |11>|1> = 1/sqrt(2) |00> |+> + 1/sqrt(2) |11> |->.
Measuring q[0] and q[1] yields |00> with 50% probability and |11> with 50% probability.
The reference code measures only q[0] and q[1]. Output is `{|00>: 0.5, |11>: 0.5}`.

Reasoning format:
1. Goal: Implement Simon's algorithm for a 2-bit function with period s=11 using a compact 1-bit output register.
2. Qubits: 3 total (q[0], q[1], out[0]), measuring only the 2 input qubits.
3. Evolution:
   - Initialize |000>.
   - H(q) creates superposition 1/2(|00>+|01>+|10>+|11>)|0>.
   - Oracle f

## isqTrain/2893

- task_id: `isqTrain/2893`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `431`

### Prompt

请用isQ语言编写一个量子电路：applies a Rz(pi/2) after H rotation to a single qubit and measures it.

Requirements:
- Declare `qbit q[1];` at global scope.
- Use `procedure main()` as entry point.
- Measure the qubit.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply H followed by Rz(π/2) to a single qubit, then measure.
2. **Qubits**: 1 qubit (q[0]) is used and measured.
3. **State evolution**:
   - |0⟩ → H → |+⟩ = (1/√2)(|0⟩ + |1⟩)
   - Rz(π/2) applies phase e^(-iπ/4) to |0⟩ and e^(iπ/4) to |1⟩
   - Final state: (e^(-iπ/4)/√2)|0⟩ + (e^(iπ/4)/√2)|1⟩
4. **Probabilities**: Both |0⟩ and |1⟩ have amplitude magnitude 1/√2, so P(|0⟩) = P(|1⟩) = 0.5. The relative phase does not affect measurement probabilities.

## isqTrain/4819

- task_id: `isqTrain/4819`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_import_qft`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `3572`

### Prompt

Help me write isQ code that applies QFT followed by inverse QFT, demonstrating that qft_inv undoes qft. Import std and qft. Declare 3 global qubits. Prepare |101> (X on q[0] and q[2]). Apply qft(q) then qft_inv(q). The state should return to |101>. Measure all 3 qubits. Expected: |101> with probability 1.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Demonstrate that `qft_inv` perfectly reverses `qft`, restoring the original computational basis state.
2. **Qubits**: 3 global qubits `q[0], q[1], q[2]`; all are measured.
3. **State evolution**:
   - Start in |000⟩.
   - `X(q[0])` and `X(q[2])` flip qubits 0 and 2, preparing |101⟩.
   - `qft(q)` transforms |101⟩ into a Fourier basis state: (1/√8) Σ_y exp(2πi·5y/8)|y⟩, a uniform superposition with specific phases.
   - `qft_inv(q)` applies the inverse QFT, which exactly cancels the phase rotations and basis change, returning to |101⟩.
4. **Expected probabilities**: Since the final state is exactly |101⟩, measurement yields outcome |101⟩ with probability 1.0.

## isqTrain/1387

- task_id: `isqTrain/1387`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1923`

### Prompt

实现以下量子计算任务（使用isQ）：the Bernstein-Vazirani algorithm to find the secret string s = 11 (MSB first). Use 2 input qubits and 1 ancilla.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Bernstein-Vazirani algorithm to find secret string $s = 11$ (MSB first).
    *   Configuration: 2 input qubits ($q_0, q_1$), 1 ancilla ($anc_0$).
    *   Output: A "Reasoning" section tracing the state evolution and explaining the probabilities.
    *   Constraints: Concise (3-8 lines for simple, up to 15 for complex), use Dirac notation, strict formatting (start with "## Reasoning", NO code blocks).

2.  **Algorithm Breakdown:**
    *   Goal: Find the 2-bit secret string $s = 11$ using the Bernstein-Vazirani algorithm.
    *   Qubits: $q[2]$ (input, measured), $anc[1]$ (output, phase kickback).
    *   Initialization: $|q_0 q_1 anc_0\rangle = |000\rangle$.
    *   Step 1 (Prepare ancilla): Apply $X$ then $H$ to $anc_0$.
        *   State: $|00\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |00\rangle \otimes |-\rangle$.
    *   Step 2 (Superposition input): Apply $H$ to $q_0$ and $q_1$.
        *   State: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes |-\rangle$.
    *   Step 3 (Oracle): For $s=11$, $U_f$ applies a phase of $(-1)^{s \cdot x}$ to the input qubits. This is achieved by CNOTing both $q_0$ and $q_1$ to $anc_0$. Since $anc_0$ is in $|-\rangle$, this induces phase kickback of $(-1)^{x_0 \oplus x_1}$.
        *   State: $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle) \otimes |-\rangle$.
    *   Step 4 (Final Hadamard): Apply $H$ to $q_0$ and $q_1$.
        *   State: $H^{\otimes 2} \frac{1}{2} \sum (-1)^{x \cdot s}|x\rangle \otimes |-\rangle = |s\rangle \otimes |-\rangle = |11\rangle \otimes |-\rangle$.
    *   Step 5 (Measurement): Measuring $q_0$ and $q_1$ yields the bitstring 11 with 100% probability.

3.  **Drafting the Reasoning Section:**
    *   *Goal:* Find the 2-bit secret string $s = 11$ using the Bernstein-Vazirani algorithm.
    *   *Qubits:* 2 input qubits (measured) and 1 ancilla qubit for phase kickback.
    *   *Evolution:*
        *   Initial: $|000\rangle$.
        *   After $X$ and $H$ on ancilla, and $H^{\otimes 2}$ on inputs: $\frac{1}{2}\sum_{x \in \{0,1\}^2} |x\rangle \otimes |-\rangle$.
        *   Oracle ($CNOT(q_0, anc)$ and $CNOT(q_1, anc)$): Encodes $s=11$ via phase kickback as $\frac{1}{2}\sum_{x} (-1)^{x \cdot s}|x\rangle \otimes |-\rangle$.
        *   Final $H^{\otimes 2}$: Interferes phases to isolate $|s\rangle$, yielding $|11\rangle \otimes |-\rangle$.
    *   *Probabilities:* The final state of the measured qubits is exactly $|11\rangle$, guaranteeing a measurement outcome of '11' with 1.0 probability.

4.  **Refining for Conciseness (Targeting ~5-8 lines):**
    ## Reasoning
    - Goal: Find the 2-bit secret string $s = 11$ using the Bernstein-Vazirani algorithm.
    - Qubits: 2 input qubits $q[0], q[1]$ (measured) and 1 ancilla $anc[0]$ for phase kickback.
    - Initial state $|000\rangle$ transforms to $\frac{1

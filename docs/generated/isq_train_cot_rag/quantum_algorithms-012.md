# ISQ training COT RAG corpus: quantum_algorithms shard 12

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/27

- task_id: `isqExpand/algo/27`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hhl`, `controlled_rotation`, `eigenvalue_inversion`, `ry_gate`
- source: `qa_pipeline`
- dataset_index: `5179`

### Prompt

在HHL算法中，受控旋转步骤（Controlled Rotation）的作用是什么？为什么使用 Ry(2·arcsin(c/λ)) 角度？这一步如何实现特征值的倒数编码？

### Chain-of-thought reasoning

## 推理
目标：解释HHL中受控旋转步骤的数学原理。

推导路线：
1. QPE后状态包含 |λ̃_j> 在时钟寄存器
2. 需要将 1/λ 编码到振幅——这是HHL的核心技巧
3. Ry(θ)|0> = cos(θ/2)|0> + sin(θ/2)|1>
4. 设 θ = 2·arcsin(c/λ)，则 sin(θ/2) = c/λ
5. 后选择测量辅助比特为 |1>，提取 c/λ 分量
6. c 的选择影响成功概率——c = λ_min 最优
7. 实现方式：switch-case 枚举时钟寄存器的值

### Reference answer

## HHL中的受控旋转

### 作用
受控旋转是HHL算法的关键步骤，它将QPE提取的特征值信息转换为振幅信息，实现从 λ 到 1/λ 的映射。

### 数学推导

QPE之后，系统状态为：
Σ_j b_j |u_j> |λ̃_j> |0>_anc

受控旋转执行如下映射：
|λ̃_j> |0> → |λ̃_j> (√(1 - c²/λ̃_j²)|0> + c/λ̃_j |1>)

### 为什么是 Ry(2·arcsin(c/λ))

Ry(θ) 门的矩阵为：
```
[ cos(θ/2)  -sin(θ/2) ]
[ sin(θ/2)   cos(θ/2) ]
```

当 θ = 2·arcsin(c/λ) 时：
- sin(θ/2) = sin(arcsin(c/λ)) = c/λ
- cos(θ/2) = √(1 - c²/λ²)

因此 Ry(θ)|0> = √(1-c²/λ²)|0> + c/λ|1>。
辅助比特测量到 |1> 时，对应振幅恰好是 c/λ，实现了特征值倒数编码。

### 参数 c 的选择
c 必须满足 c ≤ |λ_min|，否则 arcsin(c/λ) 无意义。通常取 c = λ_min 以最大化后选择成功概率。成功概率为 Σ |b_j|² · c²/λ_j²。

### isQ中的实现
在isQ中，通常用 switch-case 对时钟寄存器的每个可能值分别执行不同角度的 Ry 旋转：
```isq
switch clock {
    case |1>: Ry(2*arcsin(c/1), anc);
    case |2>: Ry(2*arcsin(c/2), anc);
    // ...
}
```
这就是HHL参考实现中 CRot 过程的原理。

## isqTrain/1194

- task_id: `isqTrain/1194`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `5189`

### Prompt

Implement the following in isQ: implements the phase_estimation pattern. Include explicit identity operations in the circuit (H-H pair before M(anc[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this quantum phase estimation circuit step by step.

The goal is to implement phase estimation for the T gate, which has eigenvalue e^(iπ/4) for eigenstate |1⟩.

Qubits: 4 total (anc[0], anc[1], anc[2], target[0]), measuring anc[0], anc[1], anc[2].

Step-by-step state evolution:

1. Initial state: |0000⟩

2. X(target[0]): |0001⟩ (target becomes |1⟩)

3. H(anc[0]), H(anc[1]), H(anc[2]): (|0⟩+|1⟩)/√2 for each ancilla
   State: (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ |1⟩
   = 1/2√2 (|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩) ⊗ |1⟩

4. Controlled-T on anc[0] → target: applies T to target when anc[0]=|1⟩
   T|1⟩ = e^(iπ/4)|1⟩
   So anc[0]=|1⟩ terms pick up phase e^(iπ/4)
   State: 1/2√2 (|000⟩ + e^(iπ/4)|001⟩ + |010⟩ + e^(iπ/4)|011⟩ + |100⟩ + e^(iπ/4)|101⟩ + |110⟩ + e^(iπ/4)|111⟩) ⊗ |1⟩
   
   Wait, let me re-index. Let me use anc[0] as the least significant bit.
   Actually in isQ, the indexing matters for measurement. Let me just track the phase carefully.

5. Controlled-S on anc[1] → target: S|1⟩ = i|1⟩ = e^(iπ/2)|1⟩
   So anc[1]=|1⟩ terms pick up additional phase e^(iπ/2)
   
   Combined phases from T and S:
   - anc[0]=1: phase e^(iπ/4)
   - anc[1]=1: phase e^(iπ/2)
   
   Let's track by ancilla state |a2 a1 a0⟩:
   - |000⟩: phase 1
   - |001⟩: phase e^(iπ/4)
   - |010⟩: phase e^(iπ/2)
   - |011⟩: phase e^(iπ/4 + iπ/2) = e^(i3π/4)
   - |100⟩: phase e^(iπ) = -1 (from controlled-Z, since Z|1⟩ = -|1⟩)
   - |101⟩: phase e^(iπ/4 + iπ) = -e^(iπ/4) = e^(i5π/4)
   - |110⟩: phase e^(iπ/2 + iπ) = -e^(iπ/2) = e^(i3π/2)
   - |111⟩: phase e^(i3π/4 + iπ) = e^(i7π/4)

6. Now apply inverse QFT to ancilla register.
   
   The phase is φ = 1/8 = 0.001 in binary.
   
   The standard QPE gives us |001⟩ in the ancilla register after inverse QFT.
   
   Let me verify: The phase of T gate on |1⟩ is φ = 1/8 (since T|1⟩ = e^(i2πφ)|1⟩ = e^(iπ/4)|1⟩, so φ = 1/8).
   
   In binary, φ = 0.001, so the ancilla should read |001⟩.

7. The inverse QFT should give us |001⟩.

8. Then H(anc[0]) followed by H(anc[0]) are applied (identity pair):
   H⊗H = I, so no effect.

9. Measurement of ancilla should give |001⟩.

But wait, The predicted output {|100⟩: 1.0}. Let me reconsider the bit ordering.

The measurement output is described as "array indexed by measurement bitstring (earlier measured qubit = higher bit)."

So if we measure M(anc[0]), M(anc[1]), M(anc[2]) in that order:
- anc[0] is measured first → highest bit
- anc[1] is measured second → middle bit  
- anc[2] is measured last → lowest bit

## isqTrain/2816

- task_id: `isqTrain/2816`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_if_else`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2562`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
oracle A(4,1) = [0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1];
oracle g(2,1) = [0,1,1,0]; 
int a;
qbit q[4], p[3];
procedure hadamard_layer(int k){
    H(q[2*k]);
    H(q[2*k+1]);
}
procedure recursive_fourier_sampling(int k){
    if (k == 2){
        A(q[0], q[1], q[2], q[3], p[2]);
    }else{
        hadamard_layer(k);
        X(p[k+1]);
        H(p[k+1]);
        recursive_fourier_sampling(k+1);
        hadamard_layer(k);
        g(q[2*k],q[2*k+1], p[k]);
        hadamard_layer(k);
        recursive_fourier_sampling(k+1);
        hadamard_layer(k);
        H(p[k+1]);
        X(p[k+1]);
    }
}
procedure main(){
    X(q[0]); 
    a = 0;
    recursive_fourier_sampling(a);
    int g = M(p[0]);    
    print g;
}
```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The program implements a recursive Fourier sampling algorithm. Let me trace through it carefully.

**Initial state:** 
- q[0..3] and p[0..2] all start in |0⟩
- After `X(q[0])`: q[0] = |1⟩, rest are |0⟩
- Initial state: |1⟩|000⟩|000⟩ (qubits q[0], q[1], q[2], q[3], p[0], p[1], p[2])

Wait, let me re-read the program. The main function:
1. X(q[0]) - flips q[0] to |1⟩
2. Calls recursive_fourier_sampling(0)

Let me trace recursive_fourier_sampling(0):
- k=0, not equal to 2, so:
  - hadamard_layer(0): H(q[0]), H(q[1])
  - X(p[1]), H(p[1])
  - recursive_fourier_sampling(1)
  - hadamard_layer(0): H(q[0]), H(q[1])
  - g(q[0], q[1], p[0]) - oracle g with inputs q[0], q[1] and output p[0]
  - hadamard_layer(0): H(q[0]), H(q[1])
  - recursive_fourier_sampling(1)
  - hadamard_layer(0): H(q[0]), H(q[1])
  - H(p[1]), X(p[1])

Now recursive_fourier_sampling(1):
- k=1, not equal to 2, so:
  - hadamard_layer(1): H(q[2]), H(q[3])
  - X(p[2]), H(p[2])
  - recursive_fourier_sampling(2)
  - hadamard_layer(1): H(q[2]), H(q[3])
  - g(q[2], q[3], p[1])
  - hadamard_layer(1): H(q[2]), H(q[3])
  - recursive_fourier_sampling(2)
  - hadamard_layer(1): H(q[2]), H(q[3])
  - H(p[2]), X(p[2])

recursive_fourier_sampling(2):
- k=2, so: A(q[0], q[1], q[2], q[3], p[2])

This is a complex recursive circuit. Let me think about what oracle g and A do.

Oracle g(2,1) = [0,1,1,0]:
This is a 2-input, 1-output oracle. For inputs |x1, x2⟩, it computes f(x1,x2) and XORs it into the output qubit.
g = [0,1,1,0] means f(00)=0, f(01)=1, f(10)=1, f(11)=0
This is f(x1,x2) = x1 ⊕ x2 (XOR)

Oracle A(4,1) = [0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1]:
4-input, 1-output oracle. A[0000]=0, A[0001]=1, A[0010]=1, A[0011]=0, A[0100]=0, A[0101]=0, A[0110]=0, A[0111]=0, A[1000]=0, A[1001]=0, A[1010]=1, A[1011]=1, A[1100]=0, A[1101]=1, A[1110]=0, A[1111]=1

Now this is a recursive Fourier sampling algorithm. The key insight is that we only measure p[0] at the end.

This is Bernstein-Vazirani / recursive Fourier sampling. The oracle A encodes some function, and the recursive structure with Hadamards and sub-oracles g implements the Fourier sampling.

The predicted output {'0': 1.0}, meaning p[0] is always measured as 0.

Let me verify this more carefully. In recursive Fourier sampling, the idea is:
- The oracle A has a "hidden" property
- The recursive structure with Hadamards extracts this property
- The measurement of p[0] gives the result

Since The predicted output p[0] = 0 with probability 1.0, let me verify.

Actually, let me think about this differently. The structure is:
- H⊗2 on (q[0], q[1])
- Phase kickback from recursive call
- H⊗2 on (q[0

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4542

- task_id: `isqTrain/4542`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3684`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;

qbit q[2];
qbit a[2];

procedure my_oracle() {
    CNOT(q[1], a[1]);
}

procedure main() {
    H(q[0]); H(q[1]);
    my_oracle();
    H(q[0]); H(q[1]);
    H(q[1]); // superposition on last qubit
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ quantum program.
    *   Output: A concise, step-by-step circuit analysis using Dirac notation (3-8 lines for simple, up to 15 for complex).
    *   Required Format: Start with "## Circuit Analysis", end with predicted probability distribution.
    *   Constraints: Output ONLY the analysis, no isQ code blocks.

2.  **Analyze the isQ Program:**
    *   Global qubits: `q[2]`, `a[2]`. All initialized to |0>.
    *   Initial state: $|q[0] q[1] a[0] a[1]\rangle = |0000\rangle$
    *   `H(q[0]); H(q[1]);` -> $|00\rangle \xrightarrow{H \otimes H} \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$ for $q$. State is $|\psi_1\rangle = \frac{1}{2}(|00\rangle_q + |01\rangle_q + |10\rangle_q + |11\rangle_q) \otimes |00\rangle_a$.
    *   `my_oracle()` -> `CNOT(q[1], a[1])`.
        *   State becomes $|\psi_2\rangle = \frac{1}{2}(|0000\rangle + |0101\rangle + |1000\rangle + |1101\rangle)$.
    *   `H(q[0]); H(q[1]);` -> Apply H to both q qubits.
        *   $|00\rangle \rightarrow |00\rangle + |01\rangle + |10\rangle + |11\rangle$
        *   $|01\rangle \rightarrow |00\rangle - |01\rangle + |10\rangle - |11\rangle$
        *   $|10\rangle \rightarrow |00\rangle + |01\rangle - |10\rangle - |11\rangle$
        *   $|11\rangle \rightarrow |00\rangle - |01\rangle - |10\rangle + |11\rangle$
        *   Let's look at the q state depending on $a[1]$:
            *   $a[1]=0$: $|00\rangle+|10\rangle = 2|+\rangle|+\rangle \xrightarrow{H \otimes H} 2|00\rangle$
            *   $a[1]=1$: $|01\rangle+|11\rangle = 2|+\rangle|-\rangle \xrightarrow{H \otimes H} 2|01\rangle$
        *   Actually, let's just do it systematically:
            $H \otimes H (|00\rangle + |10\rangle) = |00\rangle$
            $H \otimes H (|01\rangle + |11\rangle) = |01\rangle$
            So the state becomes $|\psi_3\rangle = \frac{1}{2}(2|00\rangle|00\rangle_a + 2|01\rangle|01\rangle_a) = |00\rangle|00\rangle + |01\rangle|01\rangle$ for $q$ and $a$. Wait, no. Let's trace carefully:
            $\frac{1}{2}(|00\rangle_q|00\rangle_a + |01\rangle_q|01\rangle_a + |10\rangle_q|00\rangle_a + |11\rangle_q|01\rangle_a)$.
            Apply $H \otimes H$ on $q$:
            $\frac{1}{2} [ (|00\rangle+|01\rangle+|10\rangle+|11\rangle)|00\rangle_a + (|00\rangle-|01\rangle+|10\rangle-|11\rangle)|01\rangle_a + (|00\rangle+|01\rangle-|10\rangle-|11\rangle)|00\rangle_a + (|00\rangle-|01\rangle-|10\rangle+|11\rangle)|01\rangle_a ]$
            Combine $a$ terms:
            For $|00\rangle_a$: $2|00\rangle + 2|01\rangle$? No, for $|00\rangle_a$: $\frac{1}{2} [ |00\rangle + |01\rangle + |10\rangle + |11\rangle + |00\rangle + |01\rangle - |10\rangle - |11\rangle ] = \frac{1}{2} [ 2|00\rangle + 2|01\rangle ] = |

### Reference answer

{'predicted_probs': {'00': 0.5, '01': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.5000, P(|01>) = 0.5000.'}

## isqTrain/1285

- task_id: `isqTrain/1285`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3668`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the iqp_circuit pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to write a reasoning section for an iqp_circuit variant that uses q[2] -> q[4] with an expanded qubit register.

Let me analyze The implementation:
- It uses 4 qubits (q[0], q[1], q[2], q[3])
- But the variant should use q[2] -> q[4], meaning 5 qubits total
- The active qubits would be q[2] and q[3], with q[0], q[1], q[4] in ground state

Let me trace through the circuit:
1. Start: |00000> (5 qubits)
2. H on q[2], q[3]: creates superposition
3. S on q[2], q[3]: adds phase
4. CZ(q[2], q[3]): conditional phase
5. H on q[2], q[3]: second Hadamard
6. Measure all 5 qubits

The IQP circuit pattern:
1. H layer on active qubits
2. Diagonal gates (S, T, CZ, etc.)
3. H layer on active qubits
4. Measure

For q[2] and q[3]:
- After H on both: (|00> + |01> + |10> + |11>)/2 on q[2],q[3]
- After S on both: phases added
- After CZ: conditional phase on |11>
- After H on both: interference leads to specific outcomes

Let me trace more carefully:
1. |00000> 
2. H(q[2]), H(q[3]): |0>⊗|0>⊗(|00>+|01>+|10>+|11>)/2⊗|0>
3. S(q[2]): phase on |1> of q[2]
4. S(q[3]): phase on |1> of q[3]
5. CZ(q[2], q[3]): phase on |11>
6. H(q[2]), H(q[3]): interfere

For the expected measurement probabilities like {|00000>: 0.5, |00110>: 0.5} or similar, the active qubits q[2],q[3] would need to be in an entangled state that measures to specific values.

Actually, let me think about what the IQP circuit does. The pattern is:
- H|0> = |+>
- S|+> = (|0> + i|1>)/√2
- CZ adds phase to |11>
- H creates interference

For 2 qubits:
Initial: |00>
After H,H: |++> = (|00>+|01>+|10>+|11>)/2
After S,S: (|00>+i|01>+i|10>+i²|11>)/2 = (|00>+i|01>+i|10>-|11>)/2
After CZ: (|00>+i|01>+i|10>-|11>)/2 (CZ adds -1 to |11>, but we already have -|11>, so it becomes +|11>)
Wait, CZ applies Z when control is |1>, which adds a phase of -1 to |11>.

So after CZ: (|00>+i|01>+i|10>+|11>)/2
After H,H on both qubits...

Actually, let me reconsider. The measurement probabilities given are {|0000>: 0.5, |1100>: 0.5} for 4 qubits, where q[0] and q[1] are active.

For the variant with q[2]->q[4] (meaning 5 qubits, active on q[2] and q[3]):
Expected probabilities might be {|00000>: 0.5, |00110>: 0.5}

Let me write the reasoning:

## Reasoning
1. Goal: Implement IQP circuit variant on q[2]-q[3] with expanded 5-qubit register
2. Uses 5 qubits; active qubits q[2],q[3] measured along with ground-state qubits q[0],q[1],q[4]
3. Initial state: |00000>
4. H(q[2]), H(q[3]): |0>₁|+⟩₂|+⟩₃|0>₄ (q[0],q[1],q[4] remain |0>)
5. S(q[2]), S(q[3]): applies π/2 phase to |1> components → |0>₁(|00>+i|01>+i|10>-|11>)₂₃/2|0>₄
6. CZ(q[2],q[3]): conditional phase on

## isqQA/quantum_algorithms/111_step_by_step

- task_id: `isqQA/quantum_algorithms/111_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `step_by_step`, `algorithm`, `量子傅里叶变换QFT电路`
- source: `qa_pipeline`
- dataset_index: `1744`

### Prompt

请以3量子比特系统为例，一步步教学并手动追踪量子傅里叶变换（QFT）算法的计算过程。要求解释电路中Hadamard门和受控旋转门的作用规律，并计算输入计算基态|5⟩（即二进制|101⟩）时，量子状态是如何一步步演化的，最后提供完整的isQ语言代码实现。

### Reference answer

<think>
首先明确目标输入为3量子比特态$|q_2 q_1 q_0\rangle = |101\rangle$。QFT算法的核心逻辑是逐个处理比特，利用Hadamard门创造等概率叠加，并通过受低位比特控制的旋转门$R_k$编码二进制小数相位。

推导思路如下：
1. **处理最高位$q_2$**：先作用H门，因$q_2=1$，态变为$(|0\rangle - |1\rangle)/\sqrt{2}$，引入基础相位$\pi$。接着判断受控旋转：因$q_1=0$跳过$R_2$；因$q_0=1$触发$R_3$门，附加$\pi/4$相位。这完成了最高位小数$0.101$的相位编码。
2. **处理中间位$q_1$**：作用H门（$q_1=0$，无基础相位），因$q_0=1$触发受控旋转$R_2$，附加$\pi/2$相位。
3. **处理最低位$q_0$**：仅作用H门产生基础相位，无需受控旋转。
4. **状态合成与换位**：将三个比特的演化结果写成张量积，会发现输出状态中比特顺序颠倒，因此电路最后需加上SWAP门交换$q_2$和$q_0$。
5. **代码映射**：按此自顶向下的电路结构，将H门、受控Rk门及SWAP门操作依次翻译为isQ语言的量子门调用即可。
</think>

量子傅里叶变换（QFT）是Shor等著名量子算法的核心子程序。它可以将计算基态转换为具有不同相位差的叠加态。为了让你彻底理解其运行机制，我们将以3量子比特系统为例，手动追踪输入状态|5⟩（即二进制表示下的|101⟩，设从高位到低位为q₂q₁q₀）的完整演化过程。在量子态的多项式表示中，QFT将|q₂q₁q₀⟩映射为各项带有二进制小数相位因子的张量积态，其核心思想是利用高位比特受低位比特控制的相位旋转来编码频率信息。

第一步：处理最高位量子比特q₂。初始状态为|1⟩₂|0⟩₁|1⟩₀。首先对q₂作用Hadamard（H）门。因为q₂处于|1⟩态，H门会将其变为(|0⟩ - |1⟩)/√2，这等价于引入了一个π的基础相位。接着，我们执行受控旋转操作。q₂受q₁控制作用R₂门（相移π/2）。由于q₁当前为|0⟩，该控制门不触发。随后，q₂受q₀控制作用R₃门（相移π/4）。因为q₀当前为|1⟩，该门触发，使得q₂的|1⟩态获得π/4的额外相位。此时三个比特的联合状态演化为：1/√2 (|0⟩ - e^(iπ/4)|1⟩)₂ |0⟩₁ |1⟩₀。这完美体现了二进制小数0.101（十进制5/8）的相位累加：2π×(1/2 + 0 + 1/8) = 5π/4，而 -e^(iπ/4) 等价于 e^(i5π/4)。

第二步：处理中间位量子比特q₁。当前状态中q₁仍为|0⟩。对q₁作用H门，使其变为(|0⟩ + |1⟩)/√₂。然后q₁受q₀控制作用R₂门（相移π/2）。因为q₀为|1⟩，该门触发，q₁的|1⟩态获得π/2的相位。状态演化为：1/√2 (|0⟩ + e^(iπ/2)|1⟩)₁，这对应于二进制小数0.01（十进制1/4）的相位2π×(0 + 1/4) = π/2。联合状态变为：1/√2 (|0⟩ - e^(iπ/4)|1⟩)₂ ⊗ 1/√2 (|0⟩ + e^(iπ/2)|1⟩)₁ ⊗ |1⟩₀。

第三步：处理最低位量子比特q₀。当前q₁为|1⟩，直接对其作用H门，状态演化为1/√2 (|0⟩ - |1⟩)₀，这对应于二进制小数0.1（十进制1/2）的相位π。值得注意的是，此时得到的张量积顺序是反的（高位包含了所有低位的相位信息）。为了符合常规的QFT定义，需要通过SWAP操作将量子比特顺序逆转。由于isQ不直接支持SWAP门，我们可以通过3个CNOT门来实现等效交换。

第四步：使用isQ代码实现上述3比特QFT过程。我们可以通过自定义R₂和R₃旋转门，并利用控制语句精确模拟受控旋转。

import std;

qbit q[3];

// 定义受控旋转门
// R2对应相移 pi/2
deriving gate R2 = [[1, 0], [0, exp(i * pi / 2)]];
// R3对应相移 pi/4
deriving gate R3 = [[1, 0], [0, exp(i * pi / 4)]];

procedure main() {
    // 初始化状态为 |5> = |101>
    X(q[0]);
    X(q[2]);

    // 处理最高位 q[2]
    H(q[2]);
    ctrl @[q[1]] R2(q[2]);
    ctrl @[q[0]] R3(q[2]);

    // 处理中间位 q[1]
    H(q[1]);
    ctrl @[q[0]] R2(q[1]);

    // 处理最低位 q[0]
    H(q[0]);

    // 执行SWAP操作以反转比特顺序（用CNOT模拟SWAP）
    // 交换 q[0] 和 q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
}

## isqTrain/2063

- task_id: `isqTrain/2063`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `interference`
- source: `isq_train_cot`
- dataset_index: `3754`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    ctrl SWAP(q[0], q[1], q[2]);
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 3 qubits to the state |000>. It applies a Hadamard gate to q0, followed by a controlled-swap operation (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)) with q0 as the control and q1, q2 as the targets, and finally another Hadamard gate to q0 before measuring it.
2. Initial state: |000>.
3. After H(q[0]): The state becomes (1/√2)(|000> + |100>).
4. After ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2]): The control qubit is q0. When q0 is |0>, no operation occurs. When q0 is |1>, q1 and q2 are swapped. Since both q1 and q2 are in the |0> state, swap (three-CNOT decomposition)(|00>) = |00>. Thus, the state remains unchanged as (1/√2)(|

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'SWAP test for identical |0> states: P(|0>)=1.0.'}

## isqQA/quantum_algorithms/105_hardware_limitations

- task_id: `isqQA/quantum_algorithms/105_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hardware_limitations`, `algorithm`, `Shor算法中的模幂运算`
- source: `qa_pipeline`
- dataset_index: `2731`

### Prompt

在Shor算法中，模幂运算是线路深度最大、消耗资源最多的核心模块。请详细剖析在当前的NISQ（含噪声中等规模量子）设备上，试图执行大整数（例如RSA-2048级别）的模幂运算时，会受到退相干效应以及拓扑连通性等硬件局限的哪些根本性阻碍？为说明这些阻碍，请基于模乘法的基础组件——量子加法器，提供一个简化版的半加器isQ语言代码实现，并以此代码为例阐释在真实NISQ硬件上运行的挑战。

### Reference answer

在Shor算法中，模幂运算 $U_f|x\rangle|0\rangle = |x\rangle|a^x \bmod N\rangle$ 的量子线路实现是决定算法复杂度与成败的关键。然而，在当前的NISQ（含噪声中等规模量子）设备上，针对大整数（如RSA-2048）执行模幂运算面临着几乎不可逾越的物理阻碍。这些挑战主要体现在以下三个维度：

1. 极深的线路深度与退相干时间的矛盾：实现2048位的模乘法需要将其分解为数以百万计的基本量子逻辑门。当前的NISQ设备（如超导量子计算机）的退相干时间（$T_1$和$T_2$）通常仅在微秒到百微秒量级。执行如此庞大的模幂运算所需的运行时间远远超出了量子比特保持相干性的极限。在计算完成之前，量子态的相位信息已经完全耗散，导致后续的量子傅里叶变换（QFT）只能采样到随机噪声，根本无法提取出分解大整数所需的周期 $r$。

2. 有限的拓扑连通性与庞大的SWAP开销：模幂运算线路中包含海量多量子比特受控门（如受控加法、受控乘法）。由于NISQ硬件往往只具备最近邻或有限的网格连通性，物理上不相邻的量子比特进行相互作用时，必须通过插入大量的SWAP网络来重新排列量子态。这不仅极大地增加了线路深度，还显著放大了门操作的误差。

3. 无量子纠错（QEC）下的误差累积：模幂运算需要进行大量的临时辅助比特操作。在缺乏有效的容错量子纠错机制下，每一个物理门的微小误差（目前单比特门约99.9%，双比特门约99%）会随着线路深度呈指数级累积，导致最终状态保真度无限趋近于零。

为了更直观地理解，我们可以看一个模乘法中最底层的组件——极简的半加器代码。在Shor算法中，完整的模乘法是由此类加法器通过量子傅里叶变换或基础逻辑门级联而成的。以下为isQ语言的代码示例：

import std;

qbit q[4]; 
// q[0]: 控制位
// q[1]: 被加数 A
// q[2]: 加数 B
// q[3]: 进位位 C

procedure main() {
    // 假设进行受控加法，初始化状态
    X(q[0]); // 控制位为 |1>
    X(q[1]); // A = 1
    X(q[2]); // B = 1

    // 实施半加器核心逻辑：
    // 进位操作 C = A AND B
    Toffoli(q[1], q[2], q[3]);
    
    // 本位求和操作 Sum = A XOR B
    CNOT(q[1], q[2]);
}

局限性分析与代码映射：上述代码中仅包含一个Toffoli门和一个CNOT门。但在真实的硬件上，NISQ设备通常没有原生的三比特Toffoli门，它必须被分解为至少6个CNOT门和数个单比特门。在完整的2048位模幂运算中，我们需要执行数以百万计的此类门操作。这意味着，即使底层硬件具有极高的保真度，频繁执行Toffoli门所引发的误差累积和相干时间耗尽，也会直接摧毁计算结果。因此，在没有实现通用容错量子计算之前，Shor算法在NISQ设备上只能停留在分解极小整数（如15、21）的原理验证阶段。

## isqTrain/4108

- task_id: `isqTrain/4108`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5309`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[4];

procedure main() {
    X(q[1]);
    X(q[3]);

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    H(q[3]);
    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit starts with 4 qubits: q[0], q[1], q[2], q[3] all in |0⟩.

1. X(q[1]) → |0101⟩ (binary: q[3]q[2]q[1]q[0] = 1010... wait, let me be careful)

Actually, let me track the state more carefully. The initial state is |0000⟩ for q[0], q[1], q[2], q[3].

After X(q[1]) and X(q[3]):
State: |1010⟩ (where q[3]=1, q[2]=0, q[1]=1, q[0]=0)

Now the circuit applies a QFT-like structure. Let me trace through:

The sequence H(q[0]), followed by controlled-Rz gates on q[0] controlled by q[1], q[2], q[3] is the QFT pattern.

Actually, let me look at this more carefully. The circuit structure is:

1. X(q[1]), X(q[3]) → state |1010⟩

Then we have what looks like a QFT on all 4 qubits (in the bit-reversed order or something similar):

H(q[0])
CRz(π/2, q[1], q[0])
CRz(π/4, q[2], q[0])
CRz(π/8, q[3], q[0])

H(q[1])
CRz(π/2, q[2], q[1])
CRz(π/4, q[3], q[1])

H(q[2])
CRz(π/2, q[3], q[2])

H(q[3])

This is a QFT-like circuit. In the standard QFT, we'd have:
- H on qubit, then controlled rotations with increasing angle denominators.

Wait, but in standard QFT, the controlled rotation from q[k] to q[j] (where k > j) uses angle 2π/2^(k-j+1). Let me check:

Here Rz(2π/4, q[1], q[0]) means Rz(π/2) on q[0] controlled by q[1]. That's 2π/2^2 = π/2. ✓
Rz(2π/8, q[2], q[0]) means Rz(π/4) on q[0] controlled by q[2]. That's 2π/2^3 = π/4. ✓
Rz(2π/16, q[3], q[0]) means Rz(π/8) on q[0] controlled by q[3]. That's 2π/2^4 = π/8. ✓

This is indeed a QFT structure.

In the standard QFT, the gates are:
- H(q[0])
- CR_k(q[1], q[0]) with k=2 → Rz(2π/2^2) = Rz(π/2)
- CR_k(q[2], q[0]) with k=3 → Rz(2π/2^3) = Rz(π/4)
- CR_k(q[3], q[0]) with k=4 → Rz(2π/2^4) = Rz(π/8)
- H(q[1])
- CR_k(q[2], q[1]) with k=2 → Rz(π/2)
- CR_k(q[3], q[1]) with k=3 → Rz(π/4)
- H(q[2])
- CR_k(q[3], q[2]) with k=2 → Rz(π/2)
- H(q[3])

Yes, this is exactly the QFT!

Now, the input state is |q[3]q[2]q[1]q[0]⟩ = |1010⟩, which represents the number 10 in binary (with q[0] as LSB) or equivalently q[3]=1, q[2]=0, q[1]=1, q[0]==0, so the number is q[0] + 2*q[1] + 4*q[2] + 8*q[3] = 0 + 2 + 0 + 8 = 10.

Wait, I need to be more careful about the QFT convention. The QFT maps |j⟩ to a superposition over |k⟩ with phase factors ω^(jk).

For input |j⟩ = |10⟩ = |1010⟩ (in the q[3]q[2]q[1]q[

### Reference answer

Uniform distribution across 16 states

## isqTrain/614

- task_id: `isqTrain/614`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4750`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;

qbit q[2];

procedure main() {
    X(q[1]);
    H(q[1]);
    H(q[0]);
    
    CNOT(q[0], q[1]);
    
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict probability distribution of measurement outcomes for an isQ program.
    *   Input: isQ program involving 2 qubits, X, H, CNOT, H, M(q[0]).
    *   Constraints: Concise (3-8 lines for simple), step-by-step reasoning using Dirac notation. Output ONLY the analysis section starting with "## Circuit Analysis". End with the predicted probability distribution.

2.  **Analyze the Circuit (State Evolution):**
    *   Initial state: $|00\rangle$
    *   `X(q[1])` -> $|01\rangle$
    *   `H(q[1])` -> $|0\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = \frac{1}{\sqrt{2}}(|00\rangle - |01\rangle)$
    *   `H(q[0])` -> $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = \frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$
    *   `CNOT(q[0], q[1])` -> Control=q[0], Target=q[1].
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to |01\rangle$
        *   $|10\rangle \to |11\rangle$
        *   $|11\rangle \to |10\rangle$
        *   Resulting state: $\frac{1}{2}(|00\rangle - |01\rangle + |11\rangle - |10\rangle) = \frac{1}{2}((|0\rangle - |1\rangle) \otimes |0\rangle + (|1\rangle - |0\rangle) \otimes |1\rangle) = \frac{1}{2}(|0\rangle - |1\rangle)(|0\rangle - |1\rangle)$ ? Wait, let's simplify carefully.
        *   $\frac{1}{2}(|00\rangle - |01\rangle + |11\rangle - |10\rangle) = \frac{1}{2}(|0\rangle(|0\rangle - |1\rangle) - |1\rangle(|0\rangle - |1\rangle)) = \frac{1}{2}(|0\rangle - |1\rangle) \otimes (|0\rangle - |1\rangle)$. No, that is not right.
        *   Let's re-evaluate: $\frac{1}{2}(|0\rangle(|0\rangle - |1\rangle) + |1\rangle(|1\rangle - |0\rangle)) = \frac{1}{2}(|0\rangle(|0\rangle - |1\rangle) - |1\rangle(|0\rangle - |1\rangle)) = \frac{1}{2}(|0\rangle - |1\rangle) \otimes (|0\rangle - |1\rangle) = |-\rangle \otimes |-\rangle$. Yes it is!
    *   `H(q[0])` -> Apply H to q[0].
        *   State of q[0] is $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   $H |-\rangle = \frac{1}{\sqrt{2}}(H|0\rangle - H|1\rangle) = \frac{1}{\sqrt{2}}(|+\rangle - |-\rangle) = \frac{1}{\sqrt{2}}(\frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) - \frac{1}{\sqrt{2}}(|0\rangle-|1\rangle)) = \frac{1}{2}(2|1\rangle) = |1\rangle$.
        *   Total state: $|1\rangle \otimes |-\rangle$.
    *   `M(q[0])` -> Measure q[0].
        *   It is deterministically in state $|1\rangle$.
        *   Probability of measuring $|1\rangle$ is 1.0.

3.  **Draft the Explanation:**
    *   *Initial State:* $|00\rangle$
    *   *After X(q[1]), H(q[1]), H(q[0]):* The state becomes $|+\rangle \otimes |-\

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/208. Dimension: predict probabilities for reference circuit.'}

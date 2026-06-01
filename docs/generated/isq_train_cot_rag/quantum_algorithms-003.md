# ISQ training COT RAG corpus: quantum_algorithms shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3659

- task_id: `isqTrain/3659`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `5340`

### Prompt

I need an isQ program to 3-bit quantum phase estimation for phase angle 2*pi/4 (in multiples of 2π/8). Use 3 precision qubits, controlled-Rz rotations, and a 3-qubit inverse QFT. Measure all 4 qubits (3 precision + 1 eigenstate).

### Chain-of-thought reasoning

Let me analyze this quantum phase estimation (QPE) circuit step by step.

The goal is to implement 3-bit QPE for a phase angle of 2π/4 = π/2 (i.e., θ = 2/8 = 1/4 in multiples of 2π).

Wait, let me re-read. The phase angle is 2π/4 = π/2. In the code, it's written as `2.0 * pi * 2.0 / 8.0` which equals `2*pi*2/8 = pi/2`. So the unitary U has eigenvalue e^(iπ/2) = i for eigenstate |1⟩.

Qubits: q[0], q[1], q[2] are precision qubits, q[3] is the eigenstate qubit.

Let me trace through:

**Step 1: Prepare eigenstate |1⟩**
- Apply X(q[3])
- State: |0001⟩

**Step 2: Hadamard on precision qubits**
- Apply H(q[0]), H(q[1]), H(q[2])
- State: |+++1⟩ = (1/2√2)(|0⟩+|1⟩)⊗3 ⊗ |1⟩

**Step 3: Controlled-Rz rotations**
The unitary U = Rz(π/2) has eigenvalue e^(iπ/2) = i for |1⟩ (since Rz(θ)|1⟩ = e^(-iθ/2)|1⟩).

Wait, let me be more careful. Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]].

So Rz(π/2)|1⟩ = e^(iπ/4)|1⟩.

The controlled-Rz with rotation angle 2π*2/8 * 2^k:
- q[0] controls Rz(2π*2/8 * 1) = Rz(π/2), applying phase e^(iπ/4) to |1⟩ when q[0]=|1⟩
- q[1] controls Rz(2π*2/8 * 2) = Rz(π), applying phase e^(iπ/2) to |1⟩ when q[1]=|1⟩
- q[2] controls Rz(2π*2/8 * 4) = Rz(2π), applying phase e^(iπ) to |1⟩ when q[2]=|1⟩

Wait, but controlled-Rz applies Rz to the target. The phase acquired on |1⟩ of the target is e^(iθ/2) where θ is the rotation angle.

Actually, let me think about this differently. The controlled-Rz(θ, control, target) applies Rz(θ) to the target when control is |1⟩.

For target in |1⟩: Rz(θ)|1⟩ = e^(iθ/2)|1⟩

So after all controlled operations on |+++1⟩:
- q[0]=1 contributes phase e^(i*π/2*1/2) = e^(iπ/4)
- q[1]=1 contributes phase e^(i*π*1/2) = e^(iπ/2)  
- q[2]=1 contributes phase e^(i*2π*1/2) = e^(iπ)

Wait, I need to be more careful. The rotation angles are:
- For q[0]: Rz(2π*2/8 * 1) = Rz(π/2), phase on |1⟩ = e^(i*π/4)
- For q[1]: Rz(2π*2/8 * 2) = Rz(π), phase on |1⟩ = e^(i*π/2)
- For q[2]: Rz(2π*2/8 * 4) = Rz(2π), phase on |1⟩ = e^(iπ)

Hmm, but the phase φ = 2/8 = 1/4, so 2^k * φ * 2π gives us:
- k=0: π/2, phase = e^(iπ/4) → this encodes bit φ_3 (MSB) but wait...

Actually, let me think about this more carefully in terms of the QPE algorithm.

In QPE, we want to estimate φ where U|u⟩ = e^(2πiφ)|u⟩.

Here U = Rz(π/2), and |u⟩ = |1⟩.
Rz(π/2)|1⟩ = e^(iπ/4)|1⟩

So e^(2πiφ)

## isqTrain/2858

- task_id: `isqTrain/2858`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2496`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    Toffoli(q[0], q[1], q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State**: The 3-qubit system starts in the basis state $|000\rangle$.
2. **X Gate**: The `X(q[0])` gate flips the first qubit, changing the state to $|100\rangle$.
3. **Toffoli Gate**: The `Toffoli(q[0], q[1], q[2])` gate (Toffoli) flips the target qubit (q[2]) if and only if both control qubits (q[0] and q[1]) are in the $|1\rangle$ state. Since q[1] is $|0\rangle$, the condition is not met, and the state remains $|100\rangle$.
4. **Final State**: The quantum state before measurement is exactly $|100\rangle$.
5. **Measurement**: Measuring the qubits yields the bitstring corresponding to the final state.

Predicted probability distribution: {'100': 1.0}

### Reference answer

{'predicted_probs': {'100': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqExpand/algo/127

- task_id: `isqExpand/algo/127`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `ancilla_usage`
- source: `isq_expansion`
- dataset_index: `5065`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[6];
procedure main() {
    X(q[0]); X(q[1]); X(q[2]);
    CNOT(q[0], q[2]);
    Toffoli(q[0], q[2], q[4]);
    Toffoli(q[1], q[3], q[5]);
    Toffoli(q[1], q[4], q[5]);
    Toffoli(q[3], q[4], q[5]);
    CNOT(q[1], q[3]);
    CNOT(q[4], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]); M(q[5]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
CNOT(q[0],q[2]) changes q[2] to S0 = A0 XOR B0 BEFORE Toffoli reads it.
Toffoli then computes carry = A0 AND S0 instead of carry = A0 AND B0.

Fix: Swap order -- Toffoli first, then CNOT.

Correct result: 3 + 1 = 4 = 100 binary.
q=[1,1,0,0,1,1] -> index 51.

## isqTrain/1882

- task_id: `isqTrain/1882`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1223`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[3];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    X(q[0]); H(q[0]);
    H(q[1]); CNOT(q[1], q[2]);
    CNOT(q[0], q[1]); H(q[0]);
    CNOT(q[1], q[2]); ctrl my_z(q[0], q[2]);
    H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The program uses 3 qubits: q[0], q[1], q[2]

Initial state: |000⟩

Step 1: X(q[0]); H(q[0]);
- X(q[0]): |000⟩ → |100⟩
- H(q[0]): |100⟩ → (|000⟩ - |100⟩)/√2

Step 2: H(q[1]); CNOT(q[1], q[2]);
- H(q[1]): (|000⟩ - |100⟩)/√2 → (|000⟩ + |010⟩ - |100⟩ - |110⟩)/2
- CNOT(q[1], q[2]): (|000⟩ + |011⟩ - |100⟩ - |111⟩)/2

Now we have a Bell pair between q[1] and q[2], and q[0] is in |−⟩ state.

Step 3: CNOT(q[0], q[1]); H(q[0]);
- CNOT(q[0], q[1]): (|000⟩ + |011⟩ - |110⟩ - |101⟩)/2
- H(q[0]): Let me compute this carefully.
  H on q[0]:
  |000⟩ → (|000⟩ + |100⟩)/√2
  |011⟩ → (|011⟩ + |111⟩)/√2
  |110⟩ → (|110⟩ + |010⟩)/√2  wait, H|1⟩ = (|0⟩ - |1⟩)/√2
  
Let me redo:
State before H(q[0]): (|000⟩ + |011⟩ - |110⟩ - |101⟩)/2

H(q[0]) acts:
|000⟩ → (|000⟩ + |100⟩)/√2
|011⟩ → (|011⟩ + |111⟩)/√2
|110⟩ → (|010⟩ - |110⟩)/√2
|101⟩ → (|001⟩ - |101⟩)/√2

So the state becomes:
(|000⟩ + |100⟩ + |011⟩ + |111⟩ - |010⟩ + |110⟩ - |001⟩ + |101⟩)/(2√2)

= (-|001⟩ + |000⟩ - |010⟩ + |100⟩ + |011⟩ + |101⟩ + |110⟩ + |111⟩)/(2√2)

Hmm, let me be more careful. Let me label qubits as q[0], q[1], q[2] where q[0] is the most significant bit.

State: (|000⟩ + |011⟩ - |110⟩ - |101⟩)/2

Here |abc⟩ means q[0]=a, q[1]=b, q[2]=c.

H on q[0]:
|0⟩_0 → (|0⟩ + |1⟩)/√2
|1⟩_0 → (|0⟩ - |1⟩)/√2

|000⟩ → (|000⟩ + |100⟩)/√2
|011⟩ → (|011⟩ + |111⟩)/√2
|110⟩ → (|010⟩ - |110⟩)/√2
|101⟩ → (|001⟩ - |101⟩)/√2

Total: (|000⟩ + |100⟩ + |011⟩ + |111⟩ + |010⟩ - |110⟩ - |001⟩ + |101⟩)/(2√2)

Let me group by q[0]:
= (|000⟩ - |001⟩ + |010⟩ + |011⟩)/(|0⟩_0) + (|100⟩ + |101⟩ - |110⟩ + |111⟩)/(|1⟩_0)) / (2√2)

Wait, let me just list them:
|000⟩: +1
|001⟩: -1
|010⟩: +1
|011⟩: +1
|100⟩: +1
|101⟩: +1
|110⟩: -1
|111⟩: +1

Sum divided by 2√2.

Step 4: CNOT(q[1], q[2]); ctrl my_z(q[0], q[2]);
- my_z is Z gate, so ctrl my_z(q[0], q[2]) is CZ(q[0], q[2]) which applies Z to q[2] when q[0]=1.

First CNOT(q[1], q[2]):
|000⟩ → |000⟩
|001⟩ → |001⟩
|010⟩ → |011⟩
|011⟩ → |010⟩
|100⟩ → |100⟩
|101⟩ → |101⟩

### Reference answer

{'predicted_probs': {'001': 0.25, '011': 0.25, '101': 0.25, '111': 0.25}, 'explanation': 'Expected probabilities: [0.0, 0.25, 0.0, 0.25, 0.0, 0.25, 0.0, 0.25]'}

## isqQA/quantum_algorithms/93_comparison

- task_id: `isqQA/quantum_algorithms/93_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `comparison`, `algorithm`, `Simon算法与指数加速`
- source: `qa_pipeline`
- dataset_index: `5118`

### Prompt

在量子隐含子群问题的框架下，Simon算法与Deutsch-Jozsa算法相比，其真正的指数级加速本质体现在哪里？相较于经典概率算法，其实际的适用场景和局限性是什么？请详细阐述，并使用isQ语言编写一个寻找2比特隐藏字符串s=11的Simon算法完整量子电路代码。

### Reference answer

<重思>
数学推导与理论对比分析：
1. 经典复杂度：Simon问题要求找到隐藏字符串 $s \in \{0,1\}^n$，使得黑盒函数 $f(x) = f(x \oplus s)$。在经典计算中，根据生日悖论，概率算法需要查询 $\Omega(2^{n/2})$ 次才能以高概率找到碰撞。
2. 量子复杂度：Simon算法通过量子叠加和Hadamard变换，只需 $O(n)$ 次查询即可得到满足 $y \cdot s = 0$ 的方程组，进而通过高斯消元法解出 $s$。
3. 与Deutsch-Jozsa算法对比：虽然Deutsch-Jozsa算法证明了量子相对经典确定性算法的指数加速，但经典概率算法只需 $O(1)$ 次查询即可高概率解决DJ问题。因此，DJ算法并未展现相对于所有经典算法的真正指数分离。而Simon算法是首个在理论上严格证明相对经典概率图灵机具有无条件指数加速（$O(n)$ vs $\Omega(2^{n/2})$）的算法，它直接启发了后来的Shor算法。
4. 适用场景与局限性：Simon算法适用于满足二对一映射承诺的黑盒函数分析，是证明量子优越性的绝佳理论工具。但在实际应用场景中，它局限于解决特定的异或掩码问题，且严重依赖精确的Oracle构造与无噪声环境，现实中直接的商业应用较少。
5. 代码逻辑：设定 $n=2$，隐藏字符串 $s=11$。构造函数 $f(x) = x_0 \oplus x_1$，满足 $f(00)=f(11)=0$ 且 $f(01)=f(10)=1$。在isQ中用两个CNOT门模拟Oracle，通过相位反演（输出位置为$|-$态）和Hadamard变换提取正交向量。
</重思>

在探讨量子计算相对于经典计算的指数级加速时，Simon算法具有举足轻重的地位，主要体现在以下对比分析中：

**1. 与Deutsch-Jozsa算法的对比**
Deutsch-Jozsa（DJ）算法是量子计算早期的重要突破，它证明了在黑盒模型下，量子算法可以做到一次查询就百分之百确定函数是常数还是平衡的。然而，如果放宽条件引入经典概率算法，DJ问题只需常数级 $O(1)$ 的查询即可大概率解决。因此，DJ算法并未体现出量子计算相对经典概率计算的实质性指数优势。
Simon算法则不同，它解决的也是隐藏子群问题，但其目标是在二对一映射的承诺下找到隐藏字符串 $s$。经典概率算法解决Simon问题不可避免地会遇到“生日悖论”，查询复杂度下界为 $\Omega(2^{n/2})$。而Simon算法利用量子态的叠加与干涉，仅需要 $O(n)$ 次查询即可生成线性方程组求解 $s$。这是量子算法首次在理论上被证明相对经典概率算法具有无条件的指数级加速，为后来的Shor质因数分解算法奠定了核心数学基础。

**2. 适用场景与局限性**
*   **优点与适用场景**：Simon算法是验证NISQ（含噪声中等规模量子）设备计算能力的标准基准测试算法之一。它特别适用于需要验证量子逻辑门保真度、以及研究量子纠缠和傅里叶采样机制的学术场景。
*   **局限性**：它的适用范围非常狭窄，要求黑盒函数必须严格满足 $f(x) = f(x \oplus s)$ 的强承诺条件。此外，它没有直接对应广泛存在的高价值商业应用（如Shor算法对应密码破解，Grover算法对应无序搜索）。

**3. isQ代码实现：双比特Simon算法（$s=11$）**
为了寻找 $s=11$，我们构造满足 $f(x) = x_0 \oplus x_1$ 的黑盒。当输入为00和11时输出0，当输入为01和10时输出1。

```isq
import std;

qbit q[2]; // 输入寄存器
qbit anc;  // 输出寄存器

procedure main() {
    // 初始化输出寄存器为 |-> 态，用于相位反演
    X(anc);
    H(anc);

    // 对输入寄存器应用Hadamard门，创建均匀叠加态
    H(q[0]);
    H(q[1]);

    // 实现Oracle: f(x) = x0 XOR x1
    // 这将满足 f(00)=f(11)=0 且 f(01)=f(10)=1，即 s=11
    CNOT(q[0], anc);
    CNOT(q[1], anc);

    // 再次对输入寄存器应用Hadamard门进行干涉测量
    H(q[0]);
    H(q[1]);

    // 测量输入寄存器
    // 理论上测量结果必定满足 y·s = 0 mod 2。
    // 由于s=11，可能的非零正交向量不存在，因此测量结果必定是 00。
    // 结合全0结果，系统可推导并验证出 s=11。
    int r0 = M(q[0]);
    int r1 = M(q[1]);
}
```

## isqTrain/86

- task_id: `isqTrain/86`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `155`

### Prompt

请用isQ语言编写一个量子电路：implements the amplitude_amplification pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

The user wants a reasoning section for an isQ quantum program that implements amplitude amplification with an alternative gate decomposition (CNOT -> H CZ H).

Let me trace through the circuit:

1. Initial state: |00>

2. After H(q[0]), H(q[1]): (|00> + |01> + |10> + |11>)/2 = |++>

3. The my_cz procedure applies H-H-CZ-H-H to qubits a and b
   - Note: H(b) is called twice before CZ and twice after, so effectively H^4 = I on b
   - Wait, let me re-read: H(b) is called twice, then CZ(a,b), then H(b) twice more
   - H * H = I, so H^4 = I, but the CZ is in the middle
   - So it's H(b) * H(b) * CZ(a,b) * H(b) * H(b) = I * CZ(a,b) * I = CZ(a,b)
   
   Actually wait, looking at the code more carefully:
   
   
   So my_cz just implements CZ! The H-H pairs cancel out.

4. After my_cz(q[0], q[1]) as oracle for |11>:
   - CZ applies a phase of -1 to |11>
   - State: (|00> + |01> + |10> - |11>)/2

5. Diffuser:
   - H(q[0]), H(q[1]): Transforms back to computational basis superposition
   - X(q[0]), X(q[1]): Bit flips
   - my_cz(q[0], q[1]): This is CZ, controlled phase flip
   - X(q[0]), X(q[1]): Bit flips back
   - H(q[0]), H(q[1]): Back to H basis

Let me trace more carefully. After oracle:
State: (|00> + |01> + |10> - |11>)/2

Diffuser:
H⊗2: Transforms |0> -> |+>, |1> -> |->
(|00> + |01> + |10> - |11>)/2 after H⊗2
= (|++> + |+-> + |-+> - |-->)/2

Actually let me be more careful. The standard diffuser is:
2|ψ><ψ| - I where |ψ> = |++>

In terms of gates: H⊗2 X⊗2 CZ H⊗2 (or using controlled-Z with |00> marked)

After H⊗2 X⊗2:
The state transforms. Let me use matrix notation.

After oracle, state is: (|00> + |01> + |10> - |11>)/2

Apply H⊗2:
Each qubit: |0> -> (|0>+|1>)/√2, |1> -> (|0>-|1>)/√2

|00> -> (|0>+|1>)(|0>+|1>)/2 = (|00>+|01>+|10>+|11>)/2
|01> -> (|0>+|1>)(|0>-|1>)/2 = (|00>-|01>+|10>-|11>)/2
|10> -> (|0>-|1>)(|0>+|1>)/2 = (|00>+|01>-|10>-|11>)/2
|11> -> (|0>-|1>)(|0>-|1>)/2 = (|00>-|01>-|10>+|11>)/2

Sum with coefficients [1,1,1,-1]/2:
= (|00>+|01>+|10>+|11> + |00>-|01>+|10>-|11> + |00>+|01>-|10>-|11> - |00>+|01>+|10>-|11>)/4
= (0|00> + 2|01> + 2|10> - 0|11>)/4... wait let me recalculate

Actually, let me just use the known result. The Grover diffuser with CZ (marking |11>) and H⊗2 X⊗2 ... H⊗2 X⊗2 CZ X⊗2 H⊗2 should work.

Actually the standard diffuser is:
H⊗2 (2|0...0><0...0| - I) H⊗2

Which can be implemented as H⊗2 X⊗2 CZ X⊗2 H⊗2 when CZ marks |11> = X⊗2|00>

Let

## isqTrain/3631

- task_id: `isqTrain/3631`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1391`

### Prompt

实现以下量子计算任务（使用isQ）：the 3-qubit Quantum Fourier Transform (QFT) applied to the input state |110>. The circuit should:
1. Prepare the input state by applying X gates where needed
2. Apply the QFT using Hadamard and controlled-Rz gates
3. Include the final bit-reversal swaps
4. Measure all 3 qubits

### Chain-of-thought reasoning

The user wants me to implement a 3-qubit QFT applied to |110>. Let me trace through the circuit:

1. Start with |000⟩
2. Apply X(q[0]) and X(q[1]) to get |110⟩ (q[0] is least significant, q[2] is most significant... wait, let me check the convention)

Actually, In the implementation, X(q[0]) and X(q[1]) prepare |110⟩. So if q[0] and q[1] are set to 1, then the state is |110⟩ where q[0] is the rightmost bit (LSB). So |q[2]q[1]q[0]⟩ = |110⟩.

Now let me trace the QFT:

QFT on 3 qubits:
- |110⟩ → X on q[0], q[1] → |110⟩

QFT stage for qubit 0 (the LSB):
- H(q[0]): |1⟩ → |−⟩ = (|0⟩ − |1⟩)/√2
- The state becomes |11⟩ ⊗ |−⟩ = |11−⟩

- ctrl Rz(π/2, q[1], q[0]): Since q[1] = |1⟩, this applies Rz(π/2) to q[0]
  - |−⟩ → e^{-iπ/4}|−⟩... wait, let me be more careful.
  - Rz(θ)|0⟩ = e^{-iθ/2}|0⟩, Rz(θ)|1⟩ = e^{iθ/2}|1⟩
  - So Rz(π/2)|−⟩ = (e^{-iπ/4}|0⟩ - e^{iπ/4}|1⟩)/√2

Actually, let me think about this differently. The QFT formula is:

QFT|k⟩ = (1/√N) Σ_j e^{2πijk/N} |j⟩

For N=8 and k=6 (since |110⟩ = |6⟩):

QFT|6⟩ = (1/√8) Σ_{j=0}^{7} e^{2πi·6·j/8} |j⟩
= (1/√8) Σ_{j=0}^{7} e^{3πij/2} |j⟩

Let me compute each term:
- j=0: e^0 = 1
- j=1: e^{3πi/2} = -i
- j=2: e^{3πi} = -1
- j=3: e^{9πi/2} = i
- j=4: e^{6πi} = 1
- j=5: e^{15πi/2} = -i
- j=6: e^{9πi} = -1
- j=7: e^{21πi/2} = i

So QFT|6⟩ = (1/√8)(|0⟩ - i|1⟩ - |2⟩ + i|3⟩ + |4⟩ - i|5⟩ - |6⟩ + i|7⟩)

The probabilities are all |1/√8|² = 1/8 = 0.125.

So The resulting probabilities should be uniform: 0.125 for each basis state.

Now for the reasoning, I need to trace through step by step:

1. Initialize |000⟩
2. X(q[0]), X(q[1]) → |110⟩
3. QFT stages:
   - H(q[0]) on |110⟩: qubit 0 is |1⟩ → |−⟩, state is |1,1,−⟩ = |11⟩⊗|−⟩
   - CRz(π/2) with q[1] controlling q[0]: since q[1]=|1⟩, applies phase. But the control is on q[1]... 
   
Wait, in the QFT circuit, for the k-th qubit, we apply H, then controlled rotations from qubits with higher index. Let me re-read the code:

So this is the standard QFT pattern. Let me trace more carefully.

After state preparation: |q[2]q[1]q[0]⟩ =

## isqTrain/2041

- task_id: `isqTrain/2041`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4117`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    Rz(0.785398163397448, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(0.785398163397448, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
Let me trace through this circuit step by step. Initial state: |00⟩

1. X(q[0]): |00⟩ → |10⟩
2. CNOT(q[0], q[1]): |10⟩ → |11⟩
3. Rz(π/4, q[1]): |11⟩ → e^{-iπ/8}|11⟩
4. CNOT(q[0], q[1]): e^{-iπ/8}|11⟩ → e^{-iπ/8}|10⟩
5. H(q[0]), H(q[1]): e^{-iπ/8}|10⟩ → e^{-iπ/8}|−+⟩ = e^{-iπ/8}(1/2)(|00⟩ - |10⟩ + |01⟩ - |11⟩)
6. CNOT(q[0], q[1]): → e^{-iπ/8}(1/2)(|00⟩ - |11⟩ + |01⟩ - |10⟩)
7. Rz(π/4, q[1]): → e^{-iπ/8}(1/2)(|00⟩ - e^{-iπ/4}|11⟩ + |01⟩ - e^{-iπ/4}|10⟩)
8. CNOT(q[0], q[1]): → e^{-iπ/8}(1/2)(|00⟩ - e^{-iπ/4}|10⟩ + |01⟩ - e^{-iπ/4}|11⟩)
9. H(q[0]), H(q[1]): Apply H⊗H

Let me compute this more carefully.

After step 5: e^{-iπ/8}(1/2)(|00⟩ - |10⟩ + |01⟩ - |11⟩)

After CNOT (step 6): CNOT flips q[1] when q[0]=1.
|00⟩ → |00⟩
-|10⟩ → -|11⟩
|01⟩ → |01⟩
-|11⟩ → -|10⟩

So: e^{-iπ/8}(1/2)(|00⟩ - |11⟩ + |01⟩ - |10⟩)

After Rz(π/4) on q[1] (step 7):
|00⟩ → |00⟩
-|11⟩ → -e^{-iπ/4}|11⟩
|01⟩ → e^{-iπ/8}|01⟩
-|10⟩ → -|10⟩

So: e^{-iπ/8}(1/2)(|00⟩ - e^{-iπ/4}|11⟩ + e^{-iπ/8}|01⟩ - |10⟩)

After CNOT (step 8):
|00⟩ → |00⟩
-e^{-iπ/4}|11⟩ → -e^{-iπ/4}|10⟩
e^{-iπ/8}|01⟩ → e^{-iπ/8}|01⟩
-|10⟩ → -|11⟩

So: e^{-iπ/8}(1/2)(|00⟩ - e^{-iπ/4}|10⟩ + e^{-iπ/8}|01⟩ - |11⟩)

Now apply H⊗H (step 9):
H⊗H|00⟩ = |++⟩ = (1/2)(|00⟩+|01⟩+|10⟩+|11⟩)
H⊗H|10⟩ = |--⟩ = (1/2)(|00⟩-|01⟩-|10⟩+|11⟩)
H⊗H|01⟩ = |+−⟩ = (1/2)(|00⟩-|01⟩+|10⟩-|11⟩)
H⊗H|11⟩ = |−+⟩ = (1/2)(|00⟩+|01⟩-|10⟩-|11⟩)

Collecting:
coefficient of |00⟩: e^{-iπ/8}(1/2)(1/2)(1 - e^{-iπ/4}(-1) + e^{-iπ/8}(1) - (-1))
= e^{-iπ/8}(1/4)(1 + e^{-iπ/4} + e^{-iπ/8} + 1)
= e^{-iπ/8}(1/4)(2 + e^{-iπ/4} + e^{-iπ/8})

Hmm, this is getting complex. Let me just compute the probabilities numerically.

Let θ = π/4. After step 4, state is e^{-iθ/2}|10⟩ (up to global phase, just |10⟩).

Actually let me redo this more carefully with exact numerical computation.

θ = π/4, Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2})

Step 1: |

### Reference answer

{'predicted_probs': {'01': 0.1464, '10': 0.8536}, 'explanation': 'Lie-Trotter H=XX+ZZ on |10>: P(|01>)~0.146, P(|10>)~0.854.'}

## isqTrain/4115

- task_id: `isqTrain/4115`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `4283`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];

procedure main() {
    X(q[1]);

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |000⟩ (all qubits in |0⟩)

1. X(q[1]): Flip q[1]
   State: |010⟩

2. CNOT(q[0], q[2]): q[0] controls q[2], but q[0] is |0⟩, so nothing changes
   State: |010⟩

3. CNOT(q[2], q[0]): q[2] controls q[0], but q[2] is |0⟩, so nothing changes
   State: |010⟩

4. CNOT(q[0], q[2]): q[0] controls q[2], but q[0] is |0⟩, so nothing changes
   State: |010⟩

5. H(q[2]): Apply H to q[2]
   State: |01⟩ ⊗ |+⟩ = |01+⟩ = |010⟩/√2 + |011⟩/√2

6. ctrl Rz(-π/2, q[2], q[1]): If q[2] is |1⟩, apply Rz(-π/2) to q[1]
   Rz(-π/2) = [[e^(iπ/4), 0], [0, e^(-iπ/4)]] ... wait, let me recalculate.
   
   Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
   
   So Rz(-π/2) = [[e^(iπ/4), 0], [0, e^(-iπ/4)]]
   
   When q[2] = |1⟩, apply this to q[1]:
   
   State: |01⟩|0⟩/√2 + (Rz(-π/2) on q[1])|01⟩|1⟩/√2
   
   |01⟩ = |0⟩|1⟩
   
   Rz(-π/2)|0⟩ = e^(iπ/4)|0⟩
   Rz(-π/2)|1⟩ = e^(-iπ/4)|1⟩
   
   So Rz(-π/2)|01⟩ = e^(iπ/4)|01⟩
   
   State: e^(iπ/4)·|010⟩/√2... wait, no. Let me redo.
   
   Actually, let me be more careful. The state after step 5 is:
   |010⟩/√2 + |011⟩/√2
   
   Step 6: ctrl Rz(-π/2, q[2], q[1])
   This means q[2] is control, q[1] is target.
   
   When q[2] = |0⟩: no change
   When q[2] = |1⟩: apply Rz(-π/2) to q[1]
   
   So |010⟩/√2 stays as |010⟩/√2
   And |011⟩/√2 becomes (Rz(-π/2) ⊗ I)|011⟩/√2 where Rz(-π/2) acts on q[1].
   
   Rz(-π/2)|1⟩ = e^(iπ/4)|1⟩
   
   So state becomes: |010⟩/√2 + e^(iπ/4)|011⟩/√2
   
   Or equivalently: |0⟩ ⊗ |1⟩ ⊗ (|0⟩ + e^(iπ/4)|1⟩)/√2

7. H(q[1]): Apply H to q[1]
   |1⟩ → |−⟩ = (|0⟩ - |1⟩)/√2
   
   State: |0⟩ ⊗ |−⟩ ⊗ (|0⟩ + e^(iπ/4)|1⟩)/√2
   = (|000⟩ - |010⟩)/2 ⊗ (|0⟩ + e^(iπ/4)|1⟩)/√2
   
   Hmm, let me be more careful with the tensor product.
   
   State before H(q[1]):
   |010⟩/√2 + e^(iπ/4)|011⟩/√2
   
   H on q[1]:
   |010⟩ → H|1⟩ on q[1] = (|000⟩ - |010⟩)/√2... wait.
   
   |010⟩ means q[0]=0, q[1]=1, q[2]=0.
   H on q[1]: |1⟩ → (|0⟩-|1⟩)/√2
   
   So |010⟩/√2 → (|000⟩ - |010⟩)/2
   
   And

### Reference answer

Uniform distribution across 8 states

## isqTrain/4820

- task_id: `isqTrain/4820`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_import_qft`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4263`

### Prompt

请用isQ语言编写一个量子电路：applies QFT to a 2-qubit register in state |01> (q[1]=|1>). Import std and qft. Declare 2 global qubits. Apply X(q[1]) to prepare |01>, then apply qft(q). Measure both qubits. The QFT of |01> on 2 qubits produces uniform measurement probabilities.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply the 2-qubit Quantum Fourier Transform to state |01⟩ and verify uniform output probabilities.
Qubits: 2 global qubits q[0], q[1]; both measured.

State evolution:
- |00⟩ →X(q[1])→ |01⟩
- QFT circuit: H(q[0]) → ctrl@[q[1]] S(q[0]) → H(q[1]) → swap (three-CNOT decomposition)
- After H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |1⟩ = (|01⟩+|11⟩)/√2
- After controlled-S (applies phase i when q[1]=|1⟩): (|01⟩+i|11⟩)/√2
- After H(q[1]): (|00⟩+i|10⟩−|01⟩−i|11⟩)/2
- After swap (three-CNOT decomposition): (|00⟩+i|01⟩−|10⟩−i|11⟩)/2

Each amplitude has magnitude |1/2|, so all four measurement outcomes {|00⟩,|01⟩,|10⟩,|11⟩} have equal probability 0.25.

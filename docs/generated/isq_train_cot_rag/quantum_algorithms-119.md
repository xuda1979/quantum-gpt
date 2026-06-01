# ISQ training COT RAG corpus: quantum_algorithms shard 119

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4470

- task_id: `isqTrain/4470`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `ancilla_usage`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4526`

### Prompt

What does this isQ program output when measured?

```isq
import std;

qbit q[4];

procedure main() {
    // Ancilla in |-> state
    X(q[3]);
    H(q[3]);
    // Inputs in superposition
    H(q[0]);
    H(q[1]);
    H(q[2]);
    // Balanced oracle: f(x) = x[0]
    CNOT(q[0], q[3]);
    // Decode
    H(q[0]);
    H(q[1]);
    H(q[2]);
    // Measure: expect |100> (balanced)
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of the given isQ program to predict the measurement probability distribution. The output must be a specific format, concise (3-15 lines), start with "## Circuit Analysis", end with the predicted probability distribution, and use Dirac notation.

2.  **Analyze the Code:**
    *   `qbit q[4];`: 4 qubits, initialized to $|0000\rangle$.
    *   Ancilla `q[3]`:
        *   `X(q[3])`: $|0001\rangle$
        *   `H(q[3])`: $\frac{1}{\sqrt{2}}(|0000\rangle - |0001\rangle)$
    *   Inputs `q[0], q[1], q[2]`:
        *   `H(q[0]); H(q[1]); H(q[2]);`: Creates uniform superposition over first 3 qubits: $\frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   Oracle: `CNOT(q[0], q[3]);`:
        *   Standard Deutsch-Jozsa oracle phase kickback. $f(x) = x_0$. If $x_0=1$, $|-\rangle \to -|-\rangle$.
        *   State becomes $\frac{1}{\sqrt{8}} \sum_{x} (-1)^{x_0} |x\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   Equivalently, for $q[0]$: $|0\rangle \to |0\rangle$, $|1\rangle \to -|1\rangle$. So $q[0]$ is in state $|-\rangle$. $q[1], q[2]$ are in $|+\rangle$.
    *   Decode: `H(q[0]); H(q[1]); H(q[2]);`:
        *   $H|-\rangle = |1\rangle$.
        *   $H|+\rangle = |0\rangle$.
        *   State of first 3 qubits becomes $|100\rangle$.
        *   Total state: $|100\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   Trick gates on `q[0]`: `H(q[0]); Z(q[0]); H(q[0]);`:
        *   $HZH = X$.
        *   Applies $X$ to $q[0]$.
        *   $X|1\rangle = |0\rangle$.
        *   Total state becomes $|000\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   Measurement: `M(q[0]); M(q[1]); M(q[2]);`:
        *   Measures $q[0], q[1], q[2]$.
        *   Expected outcome is `000` with probability 1.0. (Wait, the prompt says "Expected measurement probabilities: {|0000>: 1.0}". The measurement bitstring indexing in the prompt reference maps `M(q[0])` to the highest bit, so `000` for `q[2]q[1]q[0]` -> `0`. Actually, 4 qubits implies measuring `q[3]`? No, code says `M(q[0]); M(q[1]); M(q[2]);`, so 3 qubits are measured. The prompt says "Expected measurement probabilities: {|0000>: 1.0}" but wait, only 3 qubits are measured! Ah, `M(q[0])` is bit 2, `M(q[1])` is bit 1, `M(q[2])` is bit 0. So bitstring is `000`. Let's trust the code. Measurement collapses to `000`).

3.  **Draft the Explanation:**
    *   Initial state is $|0000\rangle$. Prepare ancilla `q[3]` in $|-\rangle$ and inputs `q[0:3]` in $|+\rangle^{\otimes 3}$.
    *   The `CNOT(q[0], q[3])` acts as a balanced oracle for $f(x) = x_0$, kicking back a phase of $-1$ when $q[0]$ is $|1\r

### Reference answer

{'predicted_probs': {'0000': 1.0}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0000>) = 1.0000.'}

## isqTrain/1188

- task_id: `isqTrain/1188`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `428`

### Prompt

Create an isQ quantum circuit that implements a variant of the phase_estimation pattern using anc[3] -> anc[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this phase estimation circuit step by step.

The circuit implements phase estimation for the T gate, but with an expanded ancilla register of 4 qubits (anc[0..3]), though only 3 ancilla qubits are used in the computation.

1. **Goal**: Estimate the phase of the T gate eigenvalue (e^{iπ/4}) using phase estimation with 3 evaluation qubits and an expanded ancilla register.

2. **Qubits**: anc[4] (ancilla for phase readout), target[1] (holds eigenstate |1⟩). All 4 ancilla qubits are measured.

3. **State evolution**:
   - Initial: |0000⟩|0⟩
   - X(target[0]): |0000⟩|1⟩
   - H(anc[0]), H(anc[1]), H(anc[2]): |+++0⟩|1⟩ = (1/2√2)Σ_{k=0}^{7} |k,0⟩|1⟩
   
   Wait, anc[3] is not put in superposition, so:
   - After Hadamards on anc[0], anc[1], anc[2]: |+⟩|+⟩|+⟩|0⟩|1⟩ = (1/2√2)Σ_{k=0}^{7} |k,0⟩... 
   
   Actually, anc[3] stays |0⟩, so we have:
   - |+⟩_0|+⟩_1|+⟩_2|0⟩_3|1⟩_target

   Now controlled operations:
   - ctrl T(anc[0], target): T|1⟩ = e^{iπ/4}|1⟩, phase kickback to anc[0]
   - ctrl S(anc[1], target): T² = S, S|1⟩ = i|1⟩ = e^{iπ/2}|1⟩, phase kickback
   - ctrl Z(anc[2], target): T⁴ = Z, Z|1⟩ = -|1⟩ = e^{iπ}|1⟩, phase kickback

   The phase θ of T on |1⟩ is π/8 (since T|1⟩ = e^{iπ/4}|1⟩, but phase in phase estimation convention...)

   Wait, T|1⟩ = e^{iπ/4}|1⟩, so the eigenvalue is e^{2πiθ} where θ = 1/8.

   In binary, θ = 0.001 = 1/8.

   After phase kickback:
   - anc[0] picks up e^{2πi·θ·2²} = e^{2πi·1/8·4} = e^{iπ} → bit value 0 → no, wait

   Let me reconsider. The controlled-U^{2^j} where j indexes from the least significant:
   - anc[0] controls U^{2^0} = T^1: phase e^{2πi·θ·1} = e^{2πi/8} = e^{iπ/4}
   - anc[1] controls U^{2^1} = T^2 = S: phase e^{2πi·θ·2} = e^{2πi·2/8} = e^{iπ/2}
   - anc[2] controls U^{2^2} = T^4 = Z: phase e^{2πi·θ·4} = e^{2πi·4/8} = e^{iπ}

   After phase kickback, ancilla state is:
   (1/2√2)(|0⟩ + e^{iπ/4}|1⟩)(|0⟩ + e^{iπ/2}|1⟩)(|0⟩ + e^{iπ}|1⟩)|0⟩

   Now apply inverse QFT on anc[0], anc[1], anc[2].

   The inverse QFT on 3 qubits with the phase encoding θ = 0.001 (binary) = 1/8 should output |1⟩|0⟩|0⟩.

   Wait, let me check the bit ordering in the QFT. The standard phase estimation has anc[0] corresponding to the most significant bit of θ, but the controlled operations here have:
   - anc[0] → T^1 (least significant power)
   - anc[1] → T^2 
   - anc[2] → T^4 (most significant power)

   So anc[0] is the least significant bit. θ = 1/8 = 0.001 in binary.

   After inverse QFT, we should get |001⟩ (with anc[0]=1 being the LSB).

   But the QFT in

## isqTrain/3452

- task_id: `isqTrain/3452`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `basis_change`, `interference`
- source: `isq_train_cot`
- dataset_index: `1632`

### Prompt

Code this in isQ: Demonstrate phase kickback in isQ using a CNOT gate.

Phase kickback occurs when a controlled gate is applied with the target in an eigenstate. The phase gets 'kicked back' to the control qubit.

Circuit:
1. Prepare target q[1] in |-> (eigenstate of X with eigenvalue -1)
2. Prepare control q[0] in |+> (via Hadamard)
3. Apply CNOT(q[0], q[1])
4. The phase -1 kicks back to q[0], flipping it from |+> to |->
5. Apply H to q[0] before measurement

Expected: q[0] = |1> (because H|-> = |1>), q[1] stays in |->
Declare 2 qubits, measure both.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate phase kickback where CNOT with target in X eigenstate |−⟩ transfers phase to control qubit.
Qubits: 2 (q[0]=control, q[1]=target), both measured.

State evolution:
1. |00⟩ → X(q[1]) → |01⟩
2. |01⟩ → H(q[1]) → |0⟩|−⟩
3. |0⟩|−⟩ → H(q[0]) → |+⟩|−⟩
4. |+⟩|−⟩ → CNOT(q[0],q[1]): Since X|−⟩ = −|−⟩, the −1 phase kicks back: |+⟩|−⟩ → |−⟩|−⟩
5. |−⟩|−⟩ → H(q[0]) → |1⟩|−⟩
6. |1⟩|−⟩ → H(q[1]) → |11⟩

Expected: {|11⟩: 1.0} — final state is |11⟩ with certainty, confirming phase kick

## isqQA/quantum_algorithms/97_principle_advantage

- task_id: `isqQA/quantum_algorithms/97_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `Grover最优迭代次数推导`
- source: `qa_pipeline`
- dataset_index: `1168`

### Prompt

请详细解释Grover搜索算法中寻找目标项的最优迭代次数是如何推导出来的。说明其在宏观原理上相比经典算法的显著优势，并详细分析其时间复杂度及量子加速的根本来源。最后，请使用isQ语言编写一个代码示例，展示在一个包含4个量子位的量子数据集（其中包含1个目标态）中，如何计算并执行最优次数的Grover迭代来进行搜索。

### Reference answer

Grover算法是一种针对无结构数据库的量子搜索算法，其核心在于利用量子叠加和干涉来实现对目标项振幅的放大。

**1. 最优迭代次数的数学推导：**
在Grover算法中，假设搜索空间的大小为$N=2^n$，目标项的数量为$M$（通常先考虑$M=1$的情况）。系统的初始状态被制备成所有可能状态的均匀叠加态 $|s\rangle = \frac{1}{\sqrt{N}} \sum_{x=0}^{N-1} |x\rangle$。我们设目标态为 $|w\rangle$。
初始态 $|s\rangle$ 可以看作是处于由非目标态组成的子空间与目标态 $|w\rangle$ 张成的二维平面内。设 $|s\rangle$ 与非目标子空间的夹角为 $\theta/2$，则有：
$$ \sin\left(\frac{\theta}{2}\right) = \langle w|s \rangle = \frac{1}{\sqrt{N}} $$
每次Grover迭代包含两步：首先应用Oracle算子 $O$ 使得目标态 $|w\rangle$ 的相位反转；然后应用扩散算子 $D = 2|s\rangle\langle s| - I$。这两个操作等价于在上述二维平面中，将系统状态绕原点向目标态 $|w\rangle$ 旋转 $\theta$ 的角度。
经过 $k$ 次迭代后，系统状态与 $|w\rangle$ 的夹角变为 $\frac{\pi}{2} - (k+\frac{1}{2})\theta$。为了让测量时得到目标态的概率最大化，我们希望最终状态尽可能靠近 $|w\rangle$，即要求：
$$ \left(2k + 1\right)\frac{\theta}{2} \approx \frac{\pi}{2} $$
由于当 $N$ 很大时，$\frac{\theta}{2} \approx \sin\left(\frac{\theta}{2}\right) = \frac{1}{\sqrt{N}}$，代入可得最优迭代次数 $k$：
$$ k \approx \frac{\pi}{4} \sqrt{N} - \frac{1}{2} $$
对于 $M$ 个目标项的一般情况，最优迭代次数近似为 $k \approx \frac{\pi}{4} \sqrt{\frac{N}{M}}$。

**2. 原理与优势、量子加速来源：**
*   **宏观原理**：经典算法只能逐个检查数据库中的元素，而Grover算法利用量子比特的叠加态，使得单次量子操作可以同时作用于所有可能的经典状态。通过精心设计的Oracle和扩散算子，使得错误态的几率幅发生相消干涉，而目标态的几率幅发生相长干涉，从而将目标态的概率放大。
*   **时间复杂度对比**：经典无结构搜索的时间复杂度为 $O(N)$。Grover算法通过大约 $O(\sqrt{N})$ 次迭代即可以高概率找到目标，时间复杂度降低到 $O(\sqrt{N})$。
*   **量子加速来源**：这种二次加速的根本来源是量子态的振幅放大机制。经典概率算法每次只能在一个状态中寻找，而量子算法每次迭代在布洛赫球的几何表示中，以 $\theta \approx 2/\sqrt{N}$ 的角度向目标态靠近，因此仅需约 $\pi\sqrt{N}/4$ 步即可完成从初始极小振幅到接近1的振幅翻转。

**3. isQ代码实现：**
下面是使用isQ语言在4个量子位（$N=16$，目标态1个）中执行Grover搜索的示例。计算最优迭代次数 $k \approx \frac{\pi}{4} \sqrt{16} = \pi \approx 3.14$，因此我们取整数3次迭代。

```isQ
import std;

qbit q[4];
qbit anc[3]; // 辅助量子位，用于构造多控门

procedure main() {
    // 初始化辅助比特 anc[2] 为 |-> 状态，用于相位反演
    X(anc[2]);
    H(anc[2]);
    
    // 步骤 1：将搜索量子位初始化为均匀叠加态
    for i in 0:4 {
        H(q[i]);
    }
    
    // 步骤 2：执行3次最优Grover迭代
    for iter in 0:3 {
        // --- Oracle: 标记目标态 |1111> ---
        // 使用辅助位计算与操作
        Toffoli(q[0], q[1], anc[0]);
        Toffoli(q[2], q[3], anc[1]);
        // 如果是 |1111>，则反转 anc[2] 的相位
        Toffoli(anc[0], anc[1], anc[2]);
        // 撤销辅助位的计算
        Toffoli(q[2], q[3], anc[1]);
        Toffoli(q[0], q[1], anc[0]);
        
        // --- 扩散算子 ---
        for i in 0:4 {
            H(q[i]);
        }
        for i in 0:4 {
            X(q[i]);
        }
        
        // 使用 H 和 Toffoli 构造多控Z门
        H(q[3]);
        Toffoli(q[0], q[1], anc[0]);
        Toffoli(q[2], anc[0], q[3]);
        Toffoli(q[0], q[1], anc[0]);
        H(q[3]);
        
        for i in 0:4 {
            X(q[i]);
        }
        for i in 0:4 {
            H(q[i]);
        }
    }
    
    // 步骤 3：测量结果，将以极高概率坍缩到 |1111>
    for i in 0:4 {
        M(q[i]);
    }
}
```

## isqTrain/2644

- task_id: `isqTrain/2644`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `global_phase`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `722`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[4];

procedure main() {
    // Set both input qubits to |1>
    X(q[0]);
    X(q[1]);
    // Weight 1 contribution: add x0 to sum bit 0
    CNOT(q[0], q[2]);
    // Weight 2 contribution: add x1 to sum bit 1
    CNOT(q[1], q[3]);
    // Measure the 2-bit sum output
    M(q[2]);
    M(q[3]);
}

```

Circuit 2:
```isq
import std;
qbit q[4];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Set both input qubits to |1>
    X(q[0]);
    X(q[1]);
    // Weight 1 contribution: add x0 to sum bit 0
    CNOT(q[0], q[2]);
    // Weight 2 contribution: add x1 to sum bit 1
    CNOT(q[1], q[3]);
    // Measure the 2-bit sum output
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes 4 qubits to |0000>, applies X to q[0] and q[1] to yield |1100>, then uses CNOTs to compute the sum into q[2] and q[3], resulting in the final state |1111>.
2. **Program B** applies the exact same initialization, X gates, and CNOT gates as Program A, resulting in the same final state of |1111>.
3. The only difference is that Program B applies `GPhase(0.0)` at the beginning, which multiplies the quantum state by a phase of $e^{i0} = 1$.
4. Because a global phase of 0 has no effect on the quantum state vector, both programs deterministically measure q[2] and q[3] as 1 with identical probability distributions.
5. Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/829

- task_id: `isqTrain/829`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1040`

### Prompt

I need an isQ program to implements a variant of the qft_adder pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has 4 qubits (q[0], q[1], q[2], q[3]).

Initial state: |0000>

After X(q[0]) and X(q[2]):
|1010> (q[0]=1, q[1]=0, q[2]=1, q[3]=0)

Now we apply a 3-qubit QFT on q[2], q[1], q[0]:

Step 1: H(q[2])
|1010> → The q[2] qubit is |1>, H|1> = |-> = (|0> - |1>)/√2
State becomes: 1/√2(|0010> - |1010>)... wait, let me be more careful with the ordering.

Actually, let me think about the bit ordering. q[0] is the rightmost bit in standard notation, so:
|q[3]q[2]q[1]q[0]>

After X(q[0]) and X(q[2]):
|0101> = |5> in the 4-qubit space

Now 3-qubit QFT on q[0], q[1], q[2]:

Qubit 2 (MSB of the 3-qubit register):
- H(q[2]): |0101> → q[2] is |1>, so H|1> = (|0>-|1>)/√2
  State: 1/√2(|0001> - |0101>)

- ctrl S(q[1], q[2]): S applies phase i to |1>. q[1] controls q[2].
  When q[1]=1 and q[2]=1, apply S to q[2]. But looking at our superposition:
  |0001>: q[1]=0, so nothing happens
  |0101>: q[1]=1, q[2]=1, so S is applied to q[2] giving phase i
  State: 1/√2(|0001> - i|0101>)

- ctrl T(q[0], q[2]): T applies phase e^(iπ/4) to |1>. q[0] controls q[2].
  When q[0]=1 and q[2]=1:
  |0001>: q[0]=1, q[2]=0, nothing
  |0101>: q[0]=1, q[2]=1, so T is applied to q[2] giving phase e^(iπ/4)
  State: 1/√2(|0001> - i*e^(iπ/4)|0101>)
  = 1/√2(|0001> - e^(i3π/4)|0101>)

Qubit 1 (middle):
- H(q[1]): 
  |0001> → |0> on q[1] becomes (|0>+|1>)/√2 → |0001>/√2 + |0101>/√2
  e^(i3π/4)|0101> → |1> on q[1] becomes (|0>-|1>)/√2 → e^(i3π/4)|0001>/√2 - e^(i3π/4)|0101>/√2

Wait, I'm getting confused. Let me be more systematic.

Let me denote the state after processing qubit 2 as:
|ψ₁> = 1/√2(|0001> - e^(i3π/4)|0101>)

Actually wait, let me recalculate. After ctrl S(q[1], q[2]):
- For |0001>: q[1]=0, no action
- For |0101>: q[1]=1, q[2]=1, S on q[2] gives phase i
State: 1/√2(|0001> - i|0101>)

After ctrl T(q[0], q[2]):
- For |0001>: q[0]=1, q[2]=0, no action
- For |0101>: q[0]=1, q[2]=1, T on q[2] gives phase e^(iπ/4)
State: 1/√2(|0001> - i·e^(iπ/4)|0101>) = 1/√2(|0001> - e^(i3π/4)|0101>)

Now H(q[1]):
|0001> → H on q[1] (which is |0>) gives: (|0001> + |0101>)/√2
|0101> → H on q[1] (which is |1

## isqTrain/1350

- task_id: `isqTrain/1350`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_if_else`, `mid_circuit_measurement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5274`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

qbit u[1];
qbit anc1[1];
qbit anc0[1];

procedure main() {

    X(u[0]);

    H(anc1[0]);
    ctrl Z(anc1[0], u[0]);
    H(anc1[0]);
    int m1 = M(anc1[0]);

    H(anc0[0]);
    ctrl S(anc0[0], u[0]);

    if (m1 == 1) {
        Rz(-pi/3.0, anc0[0]);
    }
    H(anc0[0]);
    int m0 = M(anc0[0]);

}

```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program and predict the probability distribution of measurement outcomes.
The isQ program involves 3 qubits: `u[0]`, `anc1[0]`, `anc0[0]`.
Wait, only `anc1[0]` and `anc0[0]` are measured.
The predicted output should only include the circuit analysis and the final predicted probability distribution.
Let's trace the program:

Initial state: |0> (for all 3 qubits)
1. `X(u[0])`: u is now |1>. State is |1>_u |0>_anc1 |0>_anc0
2. `H(anc1[0])`: anc1 is now |+>. State is |1>_u (|0>+|1>)_anc1 |0>_anc0 / sqrt(2)
3. `ctrl Z(anc1[0], u[0])`: CZ applies Z to u[0] if anc1[0] is |1>. Since u is |1>, Z|1> = -|1>.
State is |1>_u (|0> - |1>)_anc1 |0>_anc0 / sqrt(2)
4. `H(anc1[0])`: anc1 is now H(|->) = |1>. State is |1>_u |1>_anc1 |0>_anc0
5. `int m1 = M(anc1[0])`: m1 is deterministically 1. State is |1>_u |1>_anc1 |0>_anc0.
Since m1 == 1, the next block will be executed.
6. `H(anc0[0])`: anc0 is now |+>. State is |1>_u |1>_anc1 (|0>+|1>)_anc0 / sqrt(2)
7. `ctrl S(anc0[0], u[0])`: CS applies S to u[0] if anc0[0] is |1>. Since u is |1>, S|1> = i|1>.
State is i |1>_u |1>_anc1 |1>_anc0 / sqrt(2) + |1>_u |1>_anc1 |0>_anc0 / sqrt(2)
8. `if (m1 == 1)` block executes: `Rz(-pi/3.0, anc0[0])`.
Wait, this applies to anc0[0]. Rz applies a phase to |1>.
anc0 is in state (|0> + i|1>) / sqrt(2).
Wait, let's write out the state before Rz:
(|0>_anc0 + i|1>_anc0) / sqrt(2) * |1>_u |1>_anc1
Applying Rz(-pi/3) to anc0[0]:
|0> -> |0>
|1> -> e^{-i pi / 6} |1> = (sqrt(3)/2 - i/2) |1>
So anc0 state becomes |0> + i e^{-i pi / 6} |1> = |0> + i(cos(pi/6) - i sin(pi/6)) |1> = |0> + (sin(pi/6) + i cos(pi/6)) |1> = |0> + (1/2 + i sqrt(3)/2) |1>.
Wait, let me double check Rz(theta) matrix.
Rz(theta) = [[e^{-i theta/2}, 0], [0, e^{i theta/2}]].
So Rz(-pi/3) = [[e^{i pi/6}, 0], [0, e^{-i pi/6}]].
Applied to (|0> + i|1>) / sqrt(2):
e^{i pi/6} |0> + i e^{-i pi/6} |1>.
Wait! IsQ standard Rz might just be [[1, 0], [0, e^{i theta}]].
Let's check the docs: "Rz(theta, q) ... Z = [[1,0],[0,-1]]".
If Rz(theta) = [[1,0],[0, e^{i theta}]], then:
Rz(-pi/3) = [[1, 0], [0, e^{-i pi/3}]].
State becomes |0> + i e^{-i pi/3} |1> = |0> + i(cos(pi/3) - i sin(pi/3)) |1> = |0> + (sin(pi/3) + i cos(pi/3)) |1> = |0> + (sqrt(3)/2 + i/2) |1>.
Let's assume standard

### Reference answer

{'predicted_probs': {'2': 0.9330127018922192, '3': 0.0669872981077807}, 'explanation': 'Parametric variant of isqEval/496. Dimension: param_variant: pi2_to_pi3.'}

## isqQA/quantum_algorithms/124_math_derivation

- task_id: `isqQA/quantum_algorithms/124_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `math_derivation`, `algorithm`, `量子随机数生成`
- source: `qa_pipeline`
- dataset_index: `1447`

### Prompt

请详细推导基于单量子比特的量子真随机数生成（QRNG）的物理与数学原理。要求从初始量子态的矩阵表示开始，推导经过阿达马门（Hadamard Gate）演化后的量子态，并基于玻恩法则计算输出0和1的概率分布，证明其满足均匀分布。最后，请给出使用isQ语言实现这一量子真随机数生成过程的核心代码，并对代码中的量子态初始化、演化与测量步骤进行简要说明。

### Reference answer

<think>
首先，明确单量子比特的计算基态，将其初始化为列矩阵向量 $|0\rangle$。接着，为了引入量子叠加态，引入阿达马门（H门）的二维酉矩阵表示。通过线性代数的矩阵乘法规则，将H门作用于初始态向量，严谨推导出系统演化后的等概率叠加态表达式。随后，应用量子力学的核心公设——玻恩法则，提取演化后量子态在计算基下的概率幅。通过计算振幅的模平方，得出测量结果为0和1的概率均严格等于1/2，从而在数学上证明了输出结果满足完美的均匀分布。最后，将这一物理与数学推导过程映射到量子编程逻辑中：在isQ语言框架下，设计按顺序执行“分配并初始化量子比特”、“应用H门进行酉演化”以及“添加测量操作并返回经典比特”的核心代码结构。
</think>

<text>
量子随机数生成器是利用量子力学内禀的随机性来生成真随机数的算法。与经典计算机中依赖确定性算法生成的伪随机数不同，量子态在测量时的坍缩过程从根本上是不确定的，这为我们提供了无法被预先预测的真正随机性。

我们可以通过单量子比特的演化与测量来严密推导这一过程：

1. **初始量子态制备**：
在量子计算中，我们首先将量子比特制备到确定的基态上。通常设定初始态为 |0⟩，其列向量矩阵表示为：
[ |0⟩ = [ 1, 0 ]^T ]

2. **量子态演化（阿达马门作用）**：
为了使系统进入具有最大不确定性的叠加态，我们对初始态施加阿达马门（Hadamard Gate, H）。阿达马门是一个至关重要的酉算子，其矩阵表示为：
[ H = 1/sqrt(2) * [ [1, 1], [1, -1] ] ]
将H门作用于初始态 |0⟩，我们进行如下的矩阵乘法运算：
[ H|0⟩ = 1/sqrt(2) * [ [1, 1], [1, -1] ] * [ [1], [0] ] = 1/sqrt(2) * [ [1*1 + 1*0], [1*1 + (-1)*0] ] = 1/sqrt(2) * [ [1], [1] ] = (1/sqrt(2))|0⟩ + (1/sqrt(2))|1⟩ ]
此时，量子比特成功演化为等概率幅的叠加态，这是产生随机性的核心量子态。

3. **测量与概率分布（玻恩法则）**：
在演化结束后，我们在计算基（即 {|0⟩, |1⟩}）下对该量子比特进行测量。根据量子力学中的玻恩法则，测量得到结果 x 的概率等于该量子态处于对应基矢的概率振幅的模平方。
由于演化后的态为 |ψ⟩ = (1/sqrt(2))|0⟩ + (1/sqrt(2))|1⟩，基矢 |0⟩ 和 |1⟩ 的概率振幅均为 1/sqrt(2)。
因此，测量结果为 0 的概率 P(0) 为：
[ P(0) = |1/sqrt(2)|^2 = 1/2 = 50% ]
同理，测量结果为 1 的概率 P(1) 为：
[ P(1) = |1/sqrt(2)|^2 = 1/2 = 50% ]
这严密地证明了测量结果将产生概率均等的0和1，即完美的均匀分布。由于量子测量坍缩的内在随机性，每一次测量的结果都是不可预测的，从而生成了真随机比特。

4. **isQ 语言核心实现**：
以下是使用 isQ 语言实现上述量子真随机数生成的核心代码。代码逻辑完全对应于前文的数学推导。
```isq
import std;

qbit q[1]; // 全局声明一个包含1个量子比特的数组，默认被初始化为 |0⟩ 状态

procedure main() {
    // 量子态演化：对初始处于 |0⟩ 的量子比特施加阿达马门 (H门)
    // 施加后，该量子比特的态矢量演化为 1/sqrt(2)*|0⟩ + 1/sqrt(2)*|1⟩
    H(q[0]);

    // 测量：在计算基下对量子比特进行测量
    // 根据玻恩法则，变量 r 将以 50% 的概率等于 0，50% 的概率等于 1
    int r = M(q[0]);
}
```
</text>

## isqTrain/2822

- task_id: `isqTrain/2822`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4246`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    for i in 1:3 {
        CNOT(q[i-1], q[i]);
    }
    for i in 0:3 {
        M(q[i]);
    }
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **H(q[0])**: Applies Hadamard to qubit 0, creating superposition: |000⟩ → (|000⟩ + |100⟩)/√2
2. **CNOT(q[0], q[1])**: Entangles qubits 0 and 1: (|000⟩ + |100⟩)/√2 → (|000⟩ + |110⟩)/√2
3. **CNOT(q[1], q[2])**: Entangles qubit 2: (|000⟩ + |110⟩)/√2 → (|000⟩ + |111⟩)/√2
4. **Final state**: This is the 3-qubit GHZ state, an equal superposition of |000⟩ and |111⟩.
5. **Measurement**: Each basis state has probability 1/2.

**Predicted probability distribution:**
- |000⟩: 0.5
- |001⟩: 0
- |010⟩: 0
- |011⟩: 0
- |100⟩: 0
- |101⟩: 0
- |110⟩: 0
- |111⟩: 0.5

### Reference answer

{'predicted_probs': {'000': 0.5, '111': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/126_optimization_variant

- task_id: `isqQA/quantum_algorithms/126_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `optimization_variant`, `algorithm`, `隐藏子群问题`
- source: `qa_pipeline`
- dataset_index: `1137`

### Prompt

隐藏子群问题（HSP）是量子计算中一个核心的计算框架，标准量子傅里叶变换（QFT）方法在阿贝尔群上表现出指数级加速。然而，将其推广到非阿贝尔群（如对称群Sn）以解决图同构等问题时，却面临着波函数坍缩和测量样本效率低下的重大挑战。请问为了克服非阿贝尔HSP的这些困难，学术界提出了哪些重要的优化变体或改进算法框架？这些变体在原理上有何创新，并如何改变了测量与提取隐藏子群信息的策略？

### Reference answer

隐藏子群问题（Hidden Subgroup Problem, HSP）的标准量子算法依赖于在陪集态上应用量子傅里叶变换（QFT），随后进行计算基上的测量来获取隐藏子群的信息。在非阿贝尔群（如对称群 $S_n$ 或二面体群 $D_N$）上，由于非阿贝尔QFT后的概率分布极为复杂，且对多数量子态进行标准测量会导致波函数不可逆地坍缩至单一陪集，破坏了丰富的全局关联信息，使得经典重构子群变得极其困难。为了克服这些瓶颈，学术界发展了多种深刻的优化变体和替代框架。

第一种重要的改进变体是**同时对角化测量**，由Ethan Bernstein和Umesh Vazirani等人的早期工作引申，后被Kuperberg等人应用到具体群结构中。该变体的核心创新在于放弃了强依赖于群结构的QFT，转而利用局部酉变换将多个寄存器中的隐藏子群信息转换为可以同时测量的相位结构。通过精心设计的多粒子干涉网络，同时读取多个样本的相对相位，从而以多项式级甚至亚指数级的样本复杂度提取出子群的生成元。该方法在二面体群HSP中表现出极大的优势，将算法的时间复杂度从指数级降低到了亚指数级 $2^{O(\sqrt{\log N})}$。

第二种关键的优化框架是**偏迹与纠缠过滤**。针对 $S_n$ 上的图同构问题，摩尔和罗素等人证明了标准的强测量需要指数级样本。因此，后续变体转而研究密度矩阵的偏迹操作。具体而言，在制备包含隐藏子群信息的纠缠态后，不对整个系统进行全局测量，而是对其中一部分量子比特进行部分求迹，再对剩余子系统执行特定的可观测量测量。这种策略能够提取出隐藏子群在杨氏图上的特定表示特征，虽然至今尚未能在一般 $S_n$ 上实现多项式级加速，但它为理解多粒子纠缠与子群代数结构提供了关键的优化视角。

第三种创新策略是**迭代量子傅里叶变换与相位估计混合法**。在某些特定的非阿贝尔群（如半直积群）中，通过结合量子相位估计算法（QPE）和QFT，可以构造出迭代的自适应性量子线路。算法不再一次性测量所有频率，而是逐位估计频率的各个比特。当发现某一位测量结果受噪声或概率分布影响不确定时，线路会自适应地引入旋转门（如 $R_z$）和逆门来修正相位，并重新迭代。这种自适应变体大幅减少了因波函数坍缩导致的信息浪费。

为了展示在量子线路上如何通过特定的旋转和受控非门来优化和提取隐藏子群的相位信息（这与偏迹和同时对角化的核心思想紧密相关），我们可以使用以下 isQ 代码演示一个简化的二面体群特征提取优化变体线路。该代码利用了多量子比特的受控旋转来捕获隐藏常数的相位特征，避免了直接的高维强测量：

```isQ
import std;

qbit q[4];

procedure main() {
    // 初始化四个量子比特，模拟包含隐藏子群特征的叠加态
    for i in 0:4 {
        H(q[i]);
    }

    // 模拟隐藏子群带来的相对相位（Oracle作用的简化）
    // 假设隐藏结构使得 q[1] 获得相位，q[3] 作为辅助纠缠比特
    Z(q[1]);
    CNOT(q[1], q[3]);

    // 优化变体：实施受控旋转的同时对角化网络
    // 目的是将隐藏的相位信息转移到可以通过局部观测量提取的子空间中
    Rz(3.14159265 / 2.0, q[0]);
    ctrl @[q[0]] X(q[1]);
    ctrl @[q[1]] Rz(3.14159265 / 4.0, q[2]);
    ctrl @[q[0]] Rz(3.14159265 / 8.0, q[2]);

    // 利用 Toffoli 门进一步提取多重纠缠中的隐藏关联
    Toffoli(q[1], q[2], q[3]);

    // 执行优化后的局域测量准备
    // 应用逆变换以消除计算基中的冗余纠缠，突显隐藏的相位特征
    inv T(q[2]);
    H(q[3]);

    // 测量以提取特征
    for i in 0:4 {
        M(q[i]);
    }
}
```

上述算法变体与代码线路表明，通过从强计算基测量转向同时纠缠对角化、自适应相位提取以及部分纠缠过滤，量子算法能够更高效地剥离隐藏子群的信息，从而在更广泛的非阿贝尔结构中寻求计算优势。

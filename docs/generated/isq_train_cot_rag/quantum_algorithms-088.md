# ISQ training COT RAG corpus: quantum_algorithms shard 88

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/138

- task_id: `isqTrain/138`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `148`

### Prompt

Code this in isQ: implements the gate_decomposition pattern with modified rotation parameters (pi3_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

The user is asking me to generate a reasoning section for an isQ quantum program that implements a gate decomposition pattern with modified rotation parameters (pi3_to_pi4).

Let me analyze The implementation:
1. Two qubits q[0] and q[1]
2. Ry(pi/4.0, q[0]) - rotation on qubit 0
3. Ry(pi/4.0, q[1]) - rotation on qubit 1
4. CNOT(q[0], q[1]) - entangling gate
5. Measurements on both qubits

The task mentions "pi3_to_pi4" which suggests changing rotation angles from pi/3 to pi/4. The implementation already uses pi/4, so this seems to be the target.

Let me trace the state evolution:

Initial state: |00>

After Ry(pi/4, q[0]):
Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
Ry(pi/4)|0⟩ = cos(pi/8)|0⟩ + sin(pi/8)|1⟩

So state becomes: (cos(pi/8)|0⟩ + sin(pi/8)|1⟩) ⊗ |0⟩

After Ry(pi/4, q[1]):
State becomes: (cos(pi/8)|0⟩ + sin(pi/8)|1⟩) ⊗ (cos(pi/8)|0⟩ + sin(pi/8)|1⟩)
= cos²(pi/8)|00⟩ + cos(pi/8)sin(pi/8)|01⟩ + sin(pi/8)cos(pi/8)|10⟩ + sin²(pi/8)|11⟩

Let me calculate:
cos(pi/8) ≈ 0.9239
sin(pi/8) ≈ 0.3827

cos²(pi/8) ≈ 0.8536
cos(pi/8)sin(pi/8) ≈ 0.3536
sin²(pi/8) ≈ 0.1464

After CNOT(q[0], q[1]):
CNOT flips q[1] when q[0] is |1⟩
|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

So state becomes:
cos²(pi/8)|00⟩ + cos(pi/8)sin(pi/8)|01⟩ + sin(pi/8)cos(pi/8)|11⟩ + sin²(pi/8)|10⟩
= cos²(pi/8)|00⟩ + cos(pi/8)sin(pi/8)|01⟩ + sin²(pi/8)|10⟩ + cos(pi/8)sin(pi/8)|11⟩

Probabilities:
|00⟩: cos⁴(pi/8) ≈ 0.8536² ≈ 0.7285
|01⟩: cos²(pi/8)sin²(pi/8) ≈ 0.8536 × 0.1464 ≈ 0.125
|10⟩: sin⁴(pi/8) ≈ 0.1464² ≈ 0.0214
|11⟩: cos²(pi/8)sin²(pi/8) ≈ 0.125

Let me verify:
cos(pi/8) = cos(22.5°) = √(2 + √2)/2 ≈ 0.9239
sin(pi/8) = sin(22.5°) = √(2 - √2)/2 ≈ 0.3827

cos²(pi/8) = (2 + √2)/4 ≈ 0.8536
sin²(pi/8) = (2 - √2)/4 ≈ 0.1464

cos⁴(pi/8) = ((2 + √2)/4)² = (6 + 4√2)/16 = (3 + 2√2)/8 ≈ 0.7286
sin⁴(pi/8) = ((2 - √2)/4)² = (6 - 4√2)/16 = (3 - 2√2)/8 ≈ 0.0214
cos²(pi/8)sin²(pi/8) = (4 - 2)/16 = 2/16 = 1/8 = 0.125

the predicted output match:
|00⟩: 0.7285533905932737 ≈ (3 + 2√2)/8
|01⟩: 0.125 = 1/8
|10⟩: 0.02144660940672623

## isqQA/quantum_algorithms/89_principle_advantage

- task_id: `isqQA/quantum_algorithms/89_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `DJ算法与经典查询复杂度对比`
- source: `qa_pipeline`
- dataset_index: `2938`

### Prompt

作为量子计算的学习者，我了解到Deutsch-Jozsa（DJ）算法是展示量子计算优越性的经典案例。请问DJ算法的宏观原理是什么？与经典算法相比，它在时间复杂度上有何具体优势？这种量子加速的根本来源是什么？能否结合isQ语言提供一个具体示例？

### Reference answer

Deutsch-Jozsa（DJ）算法是量子计算领域中最早证明量子计算相对于经典计算具有指数级加速潜力的算法之一。

**1. 宏观原理**
DJ算法解决的核心问题是：给定一个未知的黑盒函数 $f: \{0,1\}^n \rightarrow \{0,1\}$，已知该函数要么是“常函数”（对所有输入都返回0或都返回1），要么是“平衡函数”（对恰好一半的输入返回0，另一半返回1）。DJ算法的目的就是仅需一次对黑盒的查询，便确定这个函数是常函数还是平衡函数。

**2. 时间复杂度对比**
在经典计算模型中，如果采用确定性算法，最坏情况下需要查询黑盒 $2^{n-1} + 1$ 次。即使采用概率经典算法，在允许极小错误率的情况下，也需要至少查询常数次（如 $k$ 次）才能获得足够高的置信度。而在量子计算模型中，DJ算法利用量子叠加态，**仅需1次查询**即可得出确定结论。随着输入位宽 $n$ 的增加，量子算法相对于经典确定性算法实现了从 $O(2^n)$ 到 $O(1)$ 的指数级查询加速。

**3. 量子加速来源**
DJ算法之所以能实现如此惊人的加速，根本来源在于**量子叠加（Quantum Superposition）**和**量子干涉（Quantum Interference）**机制：
- **量子叠加**：通过将 $n$ 个工作量子比特初始化为 $|0\rangle^{\otimes n}$ 并施加Hadamard门，我们构建了一个包含所有 $2^n$ 个可能输入状态的等概率叠加态。同时将辅助比特置于 $|0\rangle - |1\rangle$ 的状态。这样，单次调用预言机就能同时处理所有 $2^n$ 个输入。
- **量子干涉**：预言机的作用相当于根据函数 $f(x)$ 的值给对应的量子态赋予不同的相位（常函数保持相位一致，平衡函数引入相位翻转）。随后的Hadamard变换起到了相长干涉和相消干涉的作用：如果 $f(x)$ 是常函数，计算基态的振幅会在全零态 $|00...0\rangle$ 发生相长干涉；如果是平衡函数，振幅会在 $|00...0\rangle$ 发生完全相消干涉。因此，最后只需测量工作比特，如果全为0则是常函数，否则是平衡函数。

**4. isQ 代码实现**
下面以 $n=3$ 为例，假设预言机实现的是一个平衡函数 $f(x_0, x_1, x_2) = x_0 \oplus x_1$。我们使用 isQ 语言编写完整的 DJ 算法程序：

```isq
import std;

qbit q[3];
qbit ancilla[1];

// 构建平衡函数的预言机：f(x) = x0 XOR x1
// 由于辅助比特处于(|0>-|1>)/sqrt(2)状态，对辅助比特施加控制非门等价于对控制态相位翻转
procedure oracle_balanced() {
    CNOT(q[0], ancilla[0]);
    CNOT(q[1], ancilla[0]);
}

procedure main() {
    // 初始化辅助比特为|1>，以便后续通过H门制备|->态
    X(ancilla[0]);
    
    // 对所有工作比特和辅助比特应用Hadamard门，进入叠加态
    for i in 0:3 {
        H(q[i]);
    }
    H(ancilla[0]);
    
    // 调用黑盒预言机（仅调用1次）
    oracle_balanced();
    
    // 再次对所有工作比特施加Hadamard门，进行干涉变换
    for i in 0:3 {
        H(q[i]);
    }
    
    // 测量工作比特
    // 如果结果为 000，则为常函数；本例中预期测量结果包含1（非全零），判定为平衡函数
    for i in 0:3 {
        int r = M(q[i]);
        print r;
    }
}
```

## isqTrain/3716

- task_id: `isqTrain/3716`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2933`

### Prompt

I need an isQ program to QAOA (p=1) for the MaxCut problem on a 3-node path graph with edges [(0, 1), (1, 2)]. Use parameters gamma=0.500 and beta=1.000. The circuit:
1. Initialize all qubits in superposition
2. Apply cost unitary: for each edge, use CNOT-Rz-CNOT
3. Apply mixer: Rx(2*beta) on each qubit
4. Measure all 3 qubits

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the QAOA MaxCut circuit on a 3-node path graph.

Let me trace through the circuit:

1. Start with |000>
2. Apply H to all 3 qubits: |+++> = (1/√8)(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)
3. Cost unitary for edge (0,1): CNOT-Rz(1.0)-CNOT on q[0], q[1]
4. Cost unitary for edge (1,2): CNOT-Rz(1.0)-CNOT on q[1], q[2]
5. Mixer: Rx(2.0) on each qubit

Let me work through this more carefully.

After H gates: |+++> = (1/√8) Σ |xyz> for x,y,z ∈ {0,1}

Edge (0,1): CNOT-Rz(2γ)-CNOT implements exp(-iγ Z₀Z₁)
With γ = 0.5, Rz(1.0) applies phase e^{-i*0.5} to |1> state.

The CNOT-Rz(2γ)-CNOT sequence:
- CNOT(q[0], q[1]): flips q[1] when q[0]=1
- Rz(2γ, q[1]): applies phase e^{-iγ} to |1> of q[1]
- CNOT(q[0], q[1]): undoes the flip

This effectively applies:
- No phase to |00>, |01>, |10> (wait, let me think more carefully)

Actually, the CNOT-Rz-CNOT sequence:
- CNOT(0,1): maps |00>→|00>, |01>→|01>, |10>→|11>, |11>→|10>
- Rz(θ, q[1]): maps |00>→|00>, |01>→e^{-iθ/2}|01>, |10>→|10>... wait, Rz applies to the target qubit.

Let me be more careful. Rz(θ)|0> = e^{-iθ/2}|0>, Rz(θ)|1> = e^{iθ/2}|1>

So Rz(θ, q[1]) on the two-qubit basis:
|00> → e^{-iθ/2}|00>
|01> → e^{iθ/2}|01>
|10> → e^{-iθ/2}|10>
|11> → e^{iθ/2}|11>

Wait no, Rz only acts on q[1]:
|00> = |0>₀|0>₁ → |0>₀ Rz(θ)|0>₁ = e^{-iθ/2}|0>₀|0>₁ = e^{-iθ/2}|00>
|01> = |0>₀|1>₁ → |0>₀ Rz(θ)|1>₁ = e^{iθ/2}|0>₀|1>₁ = e^{iθ/2}|01>
|10> = |1>₀|0>₁ → |1>₀ Rz(θ)|0>₁ = e^{-iθ/2}|1>₀|0>₁ = e^{-iθ/2}|10>
|11> = |1>₀|1>₁ → |1>₀ Rz(θ)|1>₁ = e^{iθ/2}|1>₀|1>₁ = e^{iθ/2}|11>

Now CNOT-Rz(θ)-CNOT:
First CNOT(0,1):
|00> → |00>
|01> → |01>
|10> → |11>
|11> → |10>

Then Rz(θ, q[1]):
|00> → e^{-iθ/2}|00>
|01> → e^{iθ/2}|01>
|11> → e^{iθ/2}|11>
|10> → e^{-iθ/2}|10>

Then CNOT(0,1):
|00> → |00>
|01> → |01>
|11> → |10>
|10> → |11>

So overall:
|00> → e^{-iθ/2}|00>
|01> → e^{iθ/2}|01>
|10> → e^{-iθ/2}|11> → wait let me redo this

After first CNOT: |10> → |11>
After Rz: |11> → e^{iθ/2}|11>
After second CNOT: |11> → |10>

So

## isqTrain/841

- task_id: `isqTrain/841`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5258`

### Prompt

Code this in isQ: implements the gfp_multiplication pattern. Include explicit identity operations in the circuit (X-X pair before M(q[4])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement GF(3) multiplication where a=1 (binary 01) × b=2 (binary 10) = 2, demonstrating identity X-X pair cancellation.

**Qubits**: 6 qubits (q[0..5]), measuring q[4] and q[5] (product register).

**State evolution**:
- **Initial**: |000000⟩
- **X(q[0])**: |000001⟩ — encode a=1 (q[0]=1, q[1]=0)
- **X(q[3])**: |001001⟩ — encode b=2 (q[

## isqTrain/4830

- task_id: `isqTrain/4830`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_import_qft`, `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `294`

### Prompt

Write isQ code for the following quantum task: applies a CNOT gate in the QFT domain. Import std and qft. Declare 2 global qubits. Apply X(q[0]) to prepare |10>. Apply qft(q). Apply CNOT(q[0], q[1]) in frequency domain. Apply qft_inv(q). Measure both qubits.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. The goal is to apply a CNOT gate in the QFT (frequency) domain, starting from |10>, and verify the result.

2. We need 2 qubits, both measured.

3. State evolution:
- Initialize: |00>
- After X(q[0]): |10>
- After QFT(q): The QFT on 2 qubits transforms |10>. Let me compute this.

For 2 qubits, QFT is:
QFT|10> = (1/2) * Σ_{k=0}^{3} e^{2πi*2*k/4} |k>
= (1/2) * [|0> - |1> + |2> - |3>]
= (1/2) * [|00> - |01> + |10> - |11>]

- After CNOT(q[0], q[1]) in frequency domain:
CNOT swaps |01> ↔ |11>, and leaves |00> and |10> unchanged.
State becomes: (1/2)[|00> - |11> + |10> - |01>]
= (1/2)[|00> - |01> + |10> - |11>]

- After QFT_inv(q): This should bring us back to some computational basis state.

Let me reconsider. The key insight is that CNOT in the QFT domain corresponds to some operation in the computational basis.

Actually, let me think about this more carefully. The QFT and QFT_inv are inverses of each other. So:
QFT_inv * CNOT * QFT applied to |10>

This is a conjugation of CNOT by QFT. The result depends on how CNOT interacts with QFT.

Let me just trace through numerically for 2 qubits.

QFT on 2 qubits has matrix (1/2)[[1,1,1,1],[1,i,-1,-i],[1,-1,1,-1],[1,-i,-1,i]]

Starting from |10> = [0,0,1,0]^T

QFT|10> = (1/2)[1,-1,1,-1]^T = (1/2)(|00> - |01> + |10> - |11>)

After CNOT(q[0], q[1]): CNOT flips q[1] when q[0] is |1>.
|00> → |00>
|01> → |01>
|10> → |11>
|11> → |10>

So: (1/2)(|00> - |01> + |11> - |10>)

After QFT_inv:
We need QFT_inv * (1/2)[1,-1,-1,1]^T

QFT_inv = (1/2)[[1,1,1,1],[1,-i,-1,i],[1,-1,1,-1],[1,i,-1,-i]]

Result = (1/4)[1+(-1)+(-1)+1, 1+i+(-1)+(-i), 1+1+(-1)+(-1), 1+(-i)+(-1)+i]
= (1/4)[0, 0, 0, 0]

Wait, that can't be right. Let me redo this.

(1/2) * [1, -1, -1, 1]^T

QFT_inv * this vector:
Row 0: (1/2)(1*1 + 1*(-1) + 1*(-1) + 1*1) = (1/2)(1-1-1+1) = (1/2)(0) = 0
Row 1: (1/2)(1*1 + (-i)*(-1) + (-1)*(-1) + i*1) = (1/2)(1+i+1+i) = (1/2)(2+2i) = 1+i
Row 2: (1/2)(1*1 + (-1)*(-1) + 1*(-1) + (-1)*1) = (1/2)(1+1-1-1) = 0
Row 3: (1/2)(1*1 + i*(-1) + (-1)*(-1) + (-i)*1) = (1/2)(1-i+1-i) = (1/2)(2-2i) = 1-i

So we get [0, 1+i, 0, 1-i]^T, which is not a basis state...

Hmm, but The predicted output {|11>: 1.0}. Let me reconsider.

Wait, maybe I have the QFT matrix wrong, or maybe the

## isqTrain/4494

- task_id: `isqTrain/4494`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4661`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;

qbit q[3];

procedure main() {
    
    X(q[2]);
    
    H(q[0]);
    
    ctrl CNOT(q[0], q[1], q[2]);
    ctrl CNOT(q[0], q[2], q[1]);
    ctrl CNOT(q[0], q[1], q[2]);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction for an isQ program.
    *   Input code: 3 qubits, starts with X on q[2], H on q[0], three controlled CNOTs (Toffoli gates), X on q[0], then measurements.
    *   predicted output: A concise step-by-step analysis using Dirac notation, ending with the probability distribution.
    *   Constraint: "Output ONLY the analysis, starting with '## Circuit Analysis'", no code blocks, strict line limits (3-15 lines).

2.  **Analyze the isQ Program:**
    *   Initial state: $|000\rangle$
    *   `X(q[2])` -> state is $|001\rangle$ (q[2] is the rightmost bit typically, but let's be careful about bit ordering. Let's use $|q_0 q_1 q_2\rangle$). So $|001\rangle$.
    *   `H(q[0])` -> state is $\frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$. (Assuming standard notation $|q_0\rangle \otimes |q_1\rangle \otimes |q_2\rangle$).
    *   `ctrl CNOT(q[0], q[1], q[2])` -> This is a Toffoli gate. Controls are q[0], q[1]. Target is q[2].
        *   Wait, isQ syntax: `ctrl CNOT(c1, c2, target)`? The prompt says `ctrl @[c1, c2] Gate(target)`. But the code uses `ctrl CNOT(q[0], q[1], q[2])`. Wait, `CNOT` normally takes 2 arguments: `CNOT(control, target)`. So `ctrl CNOT(c1, c2, t)` means `c1` is the new control, and `CNOT(c2, t)` is the gate. So `c1` and `c2` are controls, `t` is target. This matches Toffoli.
        *   Toffoli(q[0], q[1], q[2]).
        *   In $\frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$, the state $|101\rangle$ has q[0]=1, q[1]=0. Since q[1]=0, the Toffoli does NOT flip q[2].
        *   So state remains $\frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$.
    *   `ctrl CNOT(q[0], q[2], q[1])` -> Toffoli(q[0], q[2], q[1]).
        *   $|001\rangle$: q[0]=0, q[2]=1. Doesn't flip.
        *   $|101\rangle$: q[0]=1, q[2]=1. Flips q[1].
        *   State becomes $\frac{1}{\sqrt{2}}(|001\rangle + |111\rangle)$.
    *   `ctrl CNOT(q[0], q[1], q[2])` -> Toffoli(q[0], q[1], q[2]).
        *   $|001\rangle$: q[0]=0, q[1]=0. Doesn't flip.
        *   $|111\rangle$: q[0]=1, q[1]=1. Flips q[2].
        *   State becomes $\frac{1}{\sqrt{2}}(|001\rangle + |110\rangle)$.
    *   Let's re-verify this sequence. It looks like the standard Toffoli decomposition or something similar.
        *   Wait, is it?
        *   Initial: $\frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$.
        *   Let's track just the $|101\rangle$ component:
            *   Toffoli(0,1,2) on $|101\rangle$ -> $|101\rangle$.
            *   Toffoli(0,2,1) on $|101\rangle$ -> $|111\rangle$.
            *   Toffoli(0,1,2) on $|111\rangle$ -> $|110\rangle$.
        *   So $|101\rangle$ becomes $|110\rangle$.
        *   Total state: $\frac{1}{\sqrt{2}}(|001\rangle + |110\rangle)$.
    *   `X(q[0])` -> Flips q[0].
        *   $

### Reference answer

{'predicted_probs': {'010': 0.5, '101': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|010>) = 0.5000, P(|101>) = 0.5000.'}

## isqTrain/2665

- task_id: `isqTrain/2665`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `global_phase`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5444`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[3];

procedure main() {
    // Prepare input x = |10>
    X(q[0]);
    // Bit-flip oracle for f(x) = x[0] XOR x[1]
    // XOR decomposes as two CNOT gates targeting q[2]
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    // XOR(1,0)=1, output flips to |1>
    M(q[0]); M(q[1]); M(q[2]);
}

```

vs.

```isq
import std;
qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Prepare input x = |10>
    X(q[0]);
    // Bit-flip oracle for f(x) = x[0] XOR x[1]
    // XOR decomposes as two CNOT gates targeting q[2]
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    // XOR(1,0)=1, output flips to |1>
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes the state to |000>, applies an X gate to q[0] to prepare |100>, and then evaluates the bit-flip oracle using two CNOTs. The first CNOT flips q[2] to yield |101>, and the second CNOT does nothing, leaving the final state as |101>.
2. **Program B** follows the exact same sequence but prefixes it with a `GPhase(0.0)` gate applied to the initial |000> state. 
3. The key difference is the `GPhase(0.0)` gate in Program B, which applies a global phase factor of $e^{i0} = 1$.
4. Because a phase of 0 is physically meaningless and mathematically equal to the identity operation, the quantum state remains unaffected. Both programs result in the exact same final state of |101> and yield identical measurement probabilities (100% for measuring 101).
5. Verdict: Equivalent: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/757

- task_id: `isqTrain/757`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4241`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[3];

procedure main() {
    // Encode a = 1 (binary 01)
    X(q[0]);
    // Add 1: increment the register
    // First flip LSB
    X(q[0]);
    // Carry: if LSB wrapped to 0, flip MSB
    nctrl X(q[0], q[1]);
    // Now register = 2 (binary 10), no overflow needed
    // Overflow detection (value >= 3)
    Toffoli(q[0], q[1], q[2]);
    // Modular correction (only fires if overflow=1)
    CNOT(q[2], q[0]);
    CNOT(q[2], q[1]);
    // Measure result: should be 2 = |10>
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step circuit analysis of a given isQ program, predicting the final probability distribution. The output must be concise (3-15 lines), use Dirac notation, and follow a specific format ending with the predicted probability distribution.

2.  **Analyze the isQ Code:**
    *   `qbit q[3];` -> 3 qubits initialized to $|000\rangle$.
    *   `X(q[0]);` -> q[0] becomes 1. State is $|001\rangle$ (q[2]q[1]q[0]).
    *   `X(q[0]);` -> q[0] becomes 0. State is $|000\rangle$.
    *   `nctrl X(q[0], q[1]);` -> "nctrl" means negative control. It applies X to q[1] if q[0] is $|0\rangle$. Since q[0] is $|0\rangle$, q[1] becomes 1. State is $|010\rangle$.
    *   `Toffoli(q[0], q[1], q[2]);` -> Toffoli with controls q[0], q[1] and target q[2]. Since q[0] is $|0\rangle$, Toffoli does nothing. State remains $|010\rangle$.
    *   `CNOT(q[2], q[0]);` -> CNOT with control q[2], target q[0]. Since q[2] is $|0\rangle$, CNOT does nothing. State remains $|010\rangle$.
    *   `CNOT(q[2], q[1]);` -> CNOT with control q[2], target q[1]. Since q[2] is $|0\rangle$, CNOT does nothing. State remains $|010\rangle$.
    *   `M(q[0]); M(q[1]);` -> Measures q[0] and q[1].

3.  **Trace Quantum State Evolution:**
    *   Initial: $|000\rangle$
    *   After `X(q[0])`: $|001\rangle$
    *   After `X(q[0])`: $|000\rangle$
    *   After `nctrl X(q[0], q[1])`: q[0] is $|0\rangle$, so X acts on q[1]. State is $|010\rangle$.
    *   Subsequent gates (Toffoli, CNOTs) don't change the state because their control qubits (q[0], q[2]) are $|0\rangle$.
    *   Final state: $|010\rangle$.

4.  **Determine Measurement Outcomes:**
    *   Measuring q[0] and q[1] on $|010\rangle$.
    *   q[1] = 1, q[0] = 0.
    *   In bitstrings (higher bit = earlier measured qubit), "01" means q[0]=1, q[1]=0 or q[0]=0, q[1]=1? Wait.
    *   Let's check standard bitstring notation in isQ. Earlier measured = higher bit.
    *   q[0] is measured first -> highest bit.
    *   q[1] is measured second -> lowest bit.
    *   Wait, the state is q[2]=0, q[1]=1, q[0]=0.
    *   So q[0] = 0, q[1] = 1.
    *   Bitstring: q[0] is the highest bit, q[1] is the lowest bit.
    *   So q[0]=0 (top bit), q[1]=1 (bottom bit) -> "01".
    *   Let's double check standard Qiskit/isQ ordering. M(q[0]) is index 0. M(q[1]) is index 1.
    *   Array indexed by bitstring: usually bit 0 is the right-most bit.
    *   If q[0]=0, q[1]=1, then the bitstring is `10` if q[0] is right-most, or `01` if q[0] is left-most.
    *   The prompt says "array indexed by measurement bitstring (earlier measured qubit = higher bit)".
    *   M(q[0]) is earlier -> higher bit (left-most).
    *   M(q[1]) is later -> lower bit (right-most).
    *   Therefore, q[0]=0 (left) and q[1]=1 (right) gives "01".
    *

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/281. Dimension: predict probabilities for reference circuit.'}

## isqTrain/2838

- task_id: `isqTrain/2838`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3767`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    T(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial state:** The qubit starts in the $|0\rangle$ state.
2. **Hadamard gate (H):** Creates an equal superposition, evolving the state to $|+\rangle = \frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$.
3. **T gate:** Applies a $\pi/4$ phase shift ($e^{i\pi/4}$) to the $|1\rangle$ state. The state becomes $\frac{1}{\sqrt{2}}|0\rangle + e^{i\pi/4}\frac{1}{\sqrt{2}}|1\rangle$.
4. **Measurement:** The probability of each basis state is the squared magnitude of its amplitude. Since the global phase factor $e^{i\pi/4}$ has a magnitude of 1, both $P

### Reference answer

{'predicted_probs': {'0': 0.4999999999999999, '1': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1200

- task_id: `isqTrain/1200`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5337`

### Prompt

帮我写一个isQ程序：implements the qaoa pattern with modified rotation parameters (num_pi4_to_pi6). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

The user wants me to analyze the given isQ program for a QAOA pattern with modified rotation parameters.

Let me trace through the circuit:

1. **Goal**: QAOA p=1 for MaxCut on 2-node graph with modified angles (pi/4→pi/6 for gamma).

2. **Qubits**: 2 qubits (q[0], q[1]), both measured.

3. **State evolution**:

Initial state: |00⟩

After H(q[0]), H(q[1]):
|+⟩|+⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

Cost layer with CNOT-Rz-CNOT:
- gamma was originally pi/4, now changed to pi/6 ≈ 0.52359877559830... wait, that's actually pi/6.

Wait, let me recalculate:
- pi/4 ≈ 0.7853981633974483
- pi/6 ≈ 0.5235987755982988

So the Rz angle is -0.52359877559830 which is approximately -pi/6.

And the Rx angle is 0.52359877559830 which is approximately pi/6.

After CNOT(q[0], q[1]):
(1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩)

Wait, CNOT with q[0] as control and q[1] as target:
|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

So: (1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩)

After Rz(-pi/6, q[1]):
Rz(θ)|0⟩ = e^{-iθ/2}|0⟩
Rz(θ)|1⟩ = e^{iθ/2}|1⟩

So Rz(-pi/6) on q[1]:
|0⟩ → e^{i*pi/12}|0⟩
|1⟩ → e^{-i*pi/12}|1⟩

State becomes:
(1/2)(e^{i*pi/12}|00⟩ + e^{-i*pi/12}|01⟩ + e^{-i*pi/12}|11⟩ + e^{i*pi/12}|10⟩)

After CNOT(q[0], q[1]):
(1/2)(e^{i*pi/12}|00⟩ + e^{-i*pi/12}|01⟩ + e^{-i*pi/12}|10⟩ + e^{i*pi/12}|11⟩)

So we can write this as:
(1/2)(e^{i*pi/12}(|00⟩ + |11⟩) + e^{-i*pi/12}(|01⟩ + |10⟩))

After Rx(pi/6, q[0]) and Rx(pi/6, q[1]):

Rx(θ) = [[cos(θ/2), -i*sin(θ/2)], [-i*sin(θ/2), cos(θ/2)]]

Rx(pi/6):
cos(pi/12) ≈ 0.9659
sin(pi/12) ≈ 0.2588

This is getting complex. Let me think about the predicted output.

The resulting probabilities should be:
|00⟩: 0.14174682452694481
|01⟩: 0.35825317547305524
|10⟩: 0.35825317547305524
|11⟩: 0.14174682452694481

This is symmetric as expected for the MaxCut problem on a 2-node graph. The cut states |01⟩ and |10⟩ have higher probability.

Let me verify with the angles. The problem says "num_pi4_to_pi6" suggesting we changed pi/4 to pi/6.

gamma = pi/6 (was pi/4)
beta = pi/12 (was pi/8)?

Wait, the code shows:
- Rz(-0.52359877559830) which is -pi/6
- Rx(0.52359877559830) which is pi/6

So gamma = pi/6 and 2*beta = pi/6, so beta = pi/12.

Actually wait, looking more carefully at the reference code comments:
- "gamma = pi/4" in comment but Rz uses -0.52359877559830 which is -pi/6
- "beta = pi/8" in comment but Rx uses 0.523598

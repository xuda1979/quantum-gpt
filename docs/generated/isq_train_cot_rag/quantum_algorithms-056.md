# ISQ training COT RAG corpus: quantum_algorithms shard 56

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/68

- task_id: `isqExpand/algo/68`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `vqe`, `variational_circuit`, `multi_layer`, `circuit_depth`
- source: `isq_expansion`
- dataset_index: `3520`

### Prompt

实现以下量子计算任务（使用isQ）：implementing a 2-layer variational circuit on 2 qubits. Each layer consists of Ry rotations followed by a CNOT entangling gate:
- Layer 1: Ry(pi/4) on both qubits, then CNOT(q[0], q[1])
- Layer 2: Ry(pi/3) on both qubits, then CNOT(q[0], q[1])
Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: 2-layer VQE ansatz with different rotation angles per layer.

Circuit: |00> -> [Ry(pi/4) x2, CNOT] -> [Ry(pi/3) x2, CNOT]

Layer 1:
- Ry(pi/4) on each: cos(pi/8)|0>+sin(pi/8)|1> for both
- CNOT entangles: creates 4 non-zero amplitudes

Layer 2:
- Ry(pi/3) on the already-entangled state rotates each qubit further
- Second CNOT re-entangles

The deeper circuit can represent more complex states than a single layer.
Numerical computation gives: P(00)=0.2622, P(01)=0.1981, P(10)=0.4831, P(11)=0.0566.
The dominant state |10> with P~0.48 shows the circuit exploring a specific region of Hilbert space.

## isqTrain/4556

- task_id: `isqTrain/4556`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `731`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[5];

procedure main() {
    
    X(q[0]); X(q[1]);
    
    X(q[2]); X(q[3]);
    
    ctrl ctrl X(q[0], q[2], q[4]);
    
    ctrl ctrl X(q[1], q[3], q[4]);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[4]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the request:**
    *   Task type: output prediction for an isQ program.
    *   Input is an isQ program applying X gates, two Toffoli gates, an X gate, and measuring `q[4]`.
    *   Constraint: Output MUST start with "## Circuit Analysis". Concise (3-15 lines). End with the predicted probability distribution. Use Dirac notation.

2.  **Analyze the circuit:**
    *   `qbit q[5];` -> Initial state $|00000\rangle$.
    *   `X(q[0]); X(q[1]); X(q[2]); X(q[3]);` -> Flips $q_0, q_1, q_2, q_3$ to $|1\rangle$.
        *   State: $|11110\rangle$. (Let's use the order $q_4 q_3 q_2 q_1 q_0$ or $q_0 q_1 q_2 q_3 q_4$. Let's stick to $q_0 q_1 q_2 q_3 q_4$).
        *   Wait, standard bitstring is usually $q_{N-1} \dots q_0$, but let's just write out the qubits: $|1_0 1_1 1_2 1_3 0_4\rangle$.
    *   `ctrl ctrl X(q[0], q[2], q[4]);` -> Toffoli gate with controls $q_0, q_2$, target $q_4$.
        *   $q_0=1, q_2=1 \implies q_4$ flips to 1.
        *   State: $|1_0 1_1 1_2 1_3 1_4\rangle$.
    *   `ctrl ctrl X(q[1], q[3], q[4]);` -> Toffoli gate with controls $q_1, q_3$, target $q_4$.
        *   $q_1=1, q_3=1 \implies q_4$ flips back to 0.
        *   State: $|1_0 1_1 1_2 1_3 0_4\rangle$.
    *   `X(q[0]);` -> Flips $q_0$ back to 0.
        *   State: $|0_0 1_1 1_2 1_3 0_4\rangle$.
    *   `M(q[4]);` -> Measures $q_4$. The outcome is deterministically 0.
    *   Wait, the prompt says "Expected measurement probabilities: {|00000>: 1.0}". Oh, the predicted output format says `{|00000>: 1.0}`? Let's check The implementation text: `Expected measurement probabilities: {|00000>: 1.0}`. Wait! If $q_1=1, q_2=1, q_3=1$, the state is $q_4q_3q_2q_1q_0 = |01110\rangle$. Why does the reference say `{|00000>: 1.0}`?
    *   Let me re-read the isQ program.
    *   Ah, `--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit).`
    *   In `--probs` mode, are *only* measured qubits included in the bitstring? "Number of qubits measured: 5" is In the implementation? No, "Number of qubits measured: 5" is what the user put in the reference? Wait, the prompt text says:
        "circuit implementation / circuit code:
        isq
        ...
        
        Expected measurement probabilities: {|00000>: 1.0}
        Number of qubits measured: 5
        "
        Actually, this reference text is a bit garbled, but it's clear the desired distribution is `{|01110>: 1.0}` if all 5 are measured, OR maybe only $q[4]$ is measured? No, the standard state evaluation for this usually maps qubit indices to bits. If $q_0=0, q_1=1, q_2=1, q_3=1, q_4=0$, the bitstring is $01110$. Wait, maybe the expected bitstring is $|01110\rangle$? Let me provide the state $|0

### Reference answer

{'predicted_probs': {'00000': 1.0}, 'explanation': 'This isQ program operates on 5 qubit(s). The measurement probability distribution is: P(|00000>) = 1.0000.'}

## isqTrain/1354

- task_id: `isqTrain/1354`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_if_else`, `mid_circuit_measurement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2635`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;

qbit u[1];
qbit anc1[1];
qbit anc0[2];

procedure main() {

    X(u[0]);

    H(anc1[0]);
    ctrl Z(anc1[0], u[0]);
    H(anc1[0]);
    int m1 = M(anc1[0]);

    H(anc0[0]);
    ctrl S(anc0[0], u[0]);

    if (m1 == 1) {
        Rz(-pi/2.0, anc0[0]);
    }
    H(anc0[0]);
    int m0 = M(anc0[0]); M(anc0[1]);

}

```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The program has 3 qubits that are measured:
- `anc1[0]` - measured first as `m1`
- `anc0[0]` - measured as `m0`
- `anc0[1]` - measured last (always in |0⟩ state)

Wait, let me re-read. The qubits are:
- `u[0]` - the system qubit
- `anc1[0]` - ancilla qubit 1
- `anc0[0]` and `anc0[1]` - ancilla qubits 0

The measurements are:
1. `M(anc1[0])` - first measurement
2. `M(anc0[0])` - second measurement  
3. `M(anc0[1])` - third measurement

According to the rules: "earlier measured qubit = higher bit", so the bitstring is `m1 m0 anc0[1]`.

Now let me trace through the circuit:

Initial state: |0⟩ for all qubits
- u[0]: |0⟩
- anc1[0]: |0⟩
- anc0[0]: |0⟩
- anc0[1]: |0⟩

Step 1: X(u[0])
u[0] becomes |1⟩
State: |u⟩|anc1⟩|anc0[0]⟩|anc0[1]⟩ = |1⟩|0⟩|0⟩|0⟩

Step 2: H(anc1[0])
anc1[0] becomes |+⟩ = (|0⟩ + |1⟩)/√2
State: |1⟩(|0⟩ + |1⟩)/√2 |0⟩|0⟩

Step 3: ctrl Z(anc1[0], u[0])
This is a CZ gate with anc1[0] as control and u[0] as target. CZ applies Z to target when control is |1⟩.

When anc1[0] = |1⟩ and u[0] = |1⟩, Z is applied to u[0]: |1⟩ → -|1⟩

State: (|1⟩|0⟩|0⟩|0⟩ - |1⟩|1⟩|0⟩|0⟩)/√2
= |1⟩(|0⟩ - |1⟩)/√2 |0⟩|0⟩

Step 4: H(anc1[0])
Applying H to anc1[0]:
H(|0⟩ - |1⟩)/√2 = H|0⟩/√2 - H|1⟩/√2
H|0⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = (|0⟩ - |1⟩)/√2
So: (|0⟩ + |1⟩ - |0⟩ + |1⟩)/(√2·√2) = 2|1⟩/2 = |1⟩

State: |1⟩|1⟩|0⟩|0⟩

Step 5: M(anc1[0])
Measuring anc1[0] in computational basis gives |1⟩ with probability 1.
m1 = 1

State after measurement: |1⟩|1⟩|0⟩|0⟩

Step 6: H(anc0[0])
anc0[0] becomes |+⟩
State: |1⟩|1⟩(|0⟩ + |1⟩)/√2 |0⟩

Step 7: ctrl S(anc0[0], u[0])
This is a controlled-S with anc0[0] as control and u[0] as target. S applies phase i to |1⟩ when control is |1⟩.

When anc0[0] = |1⟩ and u[0] = |1⟩: u[0] gets S applied, |1⟩ → i|1⟩

State: |1⟩|1⟩(|0⟩ + i|1⟩)/√2 |0⟩

Step 8: Since m1 = 1, we apply Rz(-π/2, anc0[0])
Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
Rz(-π/2) = [[e^(iπ/4), 0], [0, e^(-iπ/4)]]

Applying to (|0⟩ + i|1⟩)/√2:
|0⟩ component: e^(iπ/4)|0⟩
|1⟩ component: i·e^(-iπ/4)|1⟩

Let me compute: i·e^(-iπ/4) = i·(cos(-π/4

### Reference answer

{'predicted_probs': {'4': 1.0}, 'explanation': 'Parametric variant of isqEval/496. Dimension: qubit_variant: anc0[1] -> anc0[2].'}

## isqTrain/2804

- task_id: `isqTrain/2804`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `974`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];

procedure main(){
    X(q[0]); 

    H(q[0]);
    ctrl X(q[0],q[1]);

    int a = M(q[0]);
    int b = M(q[1]);
    print a - b;
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts in |00>, applies an X gate to q[0], followed by a Hadamard (H) gate, and then a CNOT with q[0] as control and q[1] as target.
2. State evolution: |00> ->(X on q[0])-> |10> ->(H on q[0])-> (|0> - |1>)|0>/√2 = (|00> - |10>)/√2.
3. After the CNOT, the target q[1] flips when the control q[0] is |1>, changing the state to (|00> - |11>)/√2.
4. Measuring this state yields either '00' or '11' with equal probability, ensuring `a == b` and `a - b == 0`.

Predicted probability distribution: [0.5, 0.0, 0.0, 0.5]

### Reference answer

{'predicted_probs': {'00': 0.5000000000000001, '11': 0.4999999999999999}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3486

- task_id: `isqTrain/3486`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `691`

### Prompt

Help me write isQ code that the 3-qubit bit-flip code with error on q[0] and correction in isQ.

1. Encode |0> -> |000>
2. Inject X error on q[0]
3. Syndrome: anc[0]=q[0] XOR q[1], anc[1]=q[0] XOR q[2]
   (compare q[0] against both q[1] and q[2])
4. Syndrome 11 on (anc[0],anc[1]) means q[0] is flipped
5. Correct with Toffoli
Declare q[3] and anc[2]. Measure q[0..2]. Expected: |000>.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Encode a logical |0⟩ via 3-qubit bit-flip code, inject an X error on q[0], extract syndrome, and correct.

**Qubits:** 5 total (q[0..2] data, anc[0..1] ancilla); measure only q[0..2].

**State evolution:**
1. Initial: |000⟩⊗|00⟩ (all zeros)
2. Encode: CNOT(q[0],q[1]), CNOT(q[0],q[2]) → |000⟩⊗|00⟩ (|0⟩ encodes to |000⟩)
3. Error: X(q[0]) → |100⟩⊗|00⟩
4. Syndrome: CNOT(q[0],anc[0]), CNOT(q[1],anc[0]) puts q[0]⊕q[1]=1 in anc[0]; CNOT(q[0],anc[1]), CNOT(q[2],anc[1]) puts q[0]⊕q[2]=1 in anc[1] → |100⟩⊗|11⟩
5. Correction: Toffoli(anc[0],anc[1],q[0]) triggers on syndrome |11⟩, flipping q[0] back → |000⟩⊗|11⟩

**Result:** Final data state is |000⟩, yielding measurement probability {|000⟩: 1.0} as the error is perfectly corrected.

## isqQA/quantum_algorithms/128_optimization_variant

- task_id: `isqQA/quantum_algorithms/128_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `optimization_variant`, `algorithm`, `超密编码`
- source: `qa_pipeline`
- dataset_index: `4715`

### Prompt

超密编码协议允许发送方通过传输一个量子比特向接收方传递两个经典比特的信息。然而，标准的超密编码通常基于最大纠缠态（如Bell态）。在更为复杂的场景中，例如处理非最大纠缠态、高维系统或多方通信时，超密编码有哪些重要的优化变体？能否以三方超密编码为例，简述其原理并使用isQ语言构建相应的量子线路框架？

### Reference answer

<thought>
数学推导与代码构思：
1. 标准超密编码：基于Bell态 $|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$，Alice通过对她的量子比特应用 $I, X, Z, iY=XZ$ 操作，编码2个经典比特，然后发送给Bob，Bob通过Bell基测量解码。
2. 改进变体分析：
   - 非最大纠缠态变体：当共享态为非最大纠缠时，可以实现概率性超密编码或确定性但信息容量降低的超密编码。
   - 高维系统变体：利用 $d$ 维量子系统（qudits），最大可传输 $2\log_2 d$ 个经典比特。
   - 多方超密编码：利用多粒子纠缠态（如GHZ态）在多方之间传递信息。例如，三方GHZ态 $|GHZ\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$。Alice拥有第一个粒子，Bob和Charlie拥有其他粒子。Alice通过对第一个粒子施加局域操作（如 $I, X, Z, XZ$），可以将2个经典比特信息编码进GHZ态的局域分支中。当Alice将粒子发送给Bob（或联合接收方）时，接收方通过联合逆制备线路即可提取信息。
3. isQ代码构建：
   - 全局声明3个量子比特 `qbit q[3];`。
   - GHZ态制备：`H(q[0]); CNOT(q[0], q[1]); CNOT(q[0], q[2]);`。
   - Alice编码：假设Alice要发送经典信息 '11'，对应应用 $X$ 门和 $Z$ 门。即 `X(q[0]); Z(q[0]);`。
   - Bob/Charlie解码（逆GHZ制备）：`CNOT(q[0], q[2]); CNOT(q[0], q[1]); H(q[0]);`。
   - 测量：使用 `M(q[i])` 进行测量提取信息。
</thought>
超密编码是量子信息论中展示量子信道超越经典信道能力的经典协议。随着量子网络和分布式量子计算的发展，研究人员提出了多种重要的优化版本和变体，以适应不同的物理场景和通信需求：

1. **非最大纠缠态超密编码**：在实际物理系统中，完美纠缠难以维持。该变体研究了当共享量子态为非最大纠缠态时，如何通过引入辅助比特或局域正定算子值测量（POVM）来实现概率性超密编码。虽然具有一定的失败概率，但在某些退相干环境中比等待完美纠缠更具实际效率。

2. **高维超密编码**：通过使用 $d$ 维量子系统，高维超密编码打破了双态系统的限制。理论上，发送一个 $d$ 维的量子比特（ qudit ）可以传输高达 $2\log_2 d$ 个经典比特。这种变体在光子的轨道角动量或时间箱编码中被广泛研究，能够极大提高光纤网络的信道容量。

3. **多方量子网络超密编码**：标准协议仅限于双方通信。多方变体通过引入多粒子纠缠态（如 GHZ 态或 Cluster 态），允许网络中的多方进行协同通信。例如，基于 GHZ 态的三方超密编码允许发送方通过操作单一量子比特，向网络中的多个接收方广播经典信息，接收方通过联合测量重建信息。

以**基于 GHZ 态的三方超密编码**为例，发送方 Alice 与接收方 Bob、Charlie 共享 GHZ 态 $|GHZ\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$。Alice 对其拥有的粒子执行四个幺正操作（$I, X, Z, iY$）之一来编码 2 个经典比特，并将粒子发送给 Bob。Bob 和 Charlie 联合对三个粒子进行逆 GHZ 制备线路的演化，通过最终的测量结果即可确定 Alice 编码的具体经典信息。

以下是使用 isQ 语言编写的基于 GHZ 态的三方超密编码量子线路框架：

```isq
import std;

// 全局声明3个量子比特用于构建GHZ态通道
qbit q[3];

procedure main() {
    // 第一步：制备三方共享的 GHZ 纠缠态 (|000> + |111>)/sqrt(2)
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);

    // 第二步：Alice 对其拥有的 q[0] 进行局域编码
    // 假设 Alice 想要发送的经典比特是 '11' (对应 iY = XZ 操作)
    X(q[0]);
    Z(q[0]);
    // 此时的 GHZ 态演化为 (|100> - |011>)/sqrt(2)
    
    // Alice 将 q[0] 发送给接收方 Bob，Bob 拥有全部三个粒子

    // 第三步：Bob 和 Charlie 联合解码
    // 执行逆 GHZ 制备操作以提取信息
    CNOT(q[0], q[2]);
    CNOT(q[0], q[1]);
    H(q[0]);

    // 第四步：测量以读取 Alice 发送的经典信息
    int r0 = M(q[0]);
    int r1 = M(q[1]);
    int r2 = M(q[2]);
}
```

在此 isQ 代码中，通过合理的 GHZ 态制备与逆向解纠缠操作，接收方可以在无需额外经典信道辅助的情况下，直接通过测量坍缩结果获取发送方编码的二维经典信息，展现了多方量子通信的潜力。

## isqTrain/707

- task_id: `isqTrain/707`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5774`

### Prompt

帮我写一个isQ程序：implements the integer_comparator pattern. Include explicit identity operations in the circuit (H-H pair before M(q[2])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a threshold comparator checking if 2-bit integer a ≥ 2, with a = 3 encoded in q[1:0], result in q[2].

2. **Qubits**: 3 qubits (q[0], q[1] for input a, q[2] for output flag); only q[2] is measured.

3. **State evolution**:
   - Initial: |000⟩
   - X(q[0]): |001⟩
   - X(q[1]): |011⟩ (encodes a = 3 as binary 11)
   - CNOT(q[1], q[2]): |111⟩ (q[1]=|1⟩ flips q[2] to |1⟩, flagging a ≥ 2)
   - H(q[2]): |11−⟩ where |−⟩ = (|0⟩−|1⟩)/√2
   - H(q[2]): |111⟩ (H-H = I, gate cancellation restores |1⟩)

4. **Expected probabilities**: {|1⟩: 1.0} — the H-H identity pair leaves q[2] in |1⟩, so measurement yields 1 with certainty.

## isqTrain/2705

- task_id: `isqTrain/2705`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `651`

### Prompt

What does this isQ program output when measured?

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

**Circuit type:** Deutsch-Jozsa algorithm with a constant oracle.

**Operations:**
1. `X(anc[0])` — prepares ancilla in |1>
2. `H(q)` — applies Hadamard to all 4 main qubits
3. `H(anc[0])` — puts ancilla into |->
4. `constant(q, anc)` — phase oracle; since oracle always returns `true`, it applies a phase of -1 for every input state (global phase)
5. `H(q)` — Hadamard on all 4 main qubits again

**State evolution:**
- Initial: |0000⟩|0⟩
- After X(anc): |0000⟩|1⟩
- After H(q): |+++++⟩|1⟩ = (1/4)Σ_x |x⟩|1⟩
- After H(anc): (1/4)Σ_x |x⟩|−⟩
- After oracle (global phase -1): -(1/4)Σ_x |x⟩|−⟩
- After H(q): -|0000⟩|−⟩

**Result:** The Hadamard transform perfectly reverses |+⟩⊗4 back to |0000⟩. The constant oracle contributes only a global phase, so measurement of q[] yields |0000⟩ with certainty.

**Predicted probability distribution:**
- 0000: 1.0
- 0001: 0.0
- 0010: 0.0
- 0011: 0.0
- 0100: 0.0
- 0101: 0.0
- 0110: 0.0
- 0111: 0.0
- 1000: 0.0
- 1001: 0.0
- 1010: 0.0
- 1011: 0.0
- 1100: 0.0
- 1101: 0.0
- 1110: 0.0
- 1111: 0.0

### Reference answer

{'predicted_probs': {'0000': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/705

- task_id: `isqTrain/705`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3791`

### Prompt

Implement the following in isQ: implements the integer_comparator pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this problem carefully.

The task is to implement an integer comparator using an alternative gate decomposition (CNOT -> H CZ H).

First, let me understand the standard integer comparator pattern and then the alternative decomposition.

The standard CNOT gate can be decomposed as: CNOT = (H ⊗ I) · CZ · (H ⊗ I), but wait, that's not quite right. Let me think again.

Actually, CNOT with control on qubit 1 and target on qubit 2 can be written as:
CNOT(c, t) = (I ⊗ H) · CZ(c, t) · (I ⊗ H)

This is because:
1. H on target converts |0> to |+> and |1> to |->
2. CZ applies Z to target when control is |1>
3. H on target converts back

Let me verify:
- |00> → |0>|+> → |0>|+> → |00>
- |01> → |0>|-> → |0>|-> → |01>
- |10> → |1>|+> → |1>|-> → |11>
- |11> → |1>|-> → |1>|+> → |10>

Yes! So CNOT(c, t) = (I ⊗ H) · CZ · (I ⊗ H) on target qubit.

Now, Analyzing the circuit requirements:
- q[0] and q[1] encode a = 3 (binary 11)
- The comparator checks if a >= 2 by checking if the MSB (q[1]) is set
- This is essentially a controlled operation: if q[1] is |1>, flip q[2]

The circuit should:
1. X(q[0]) - set bit 0
2. X(q[1]) - set bit 1 (MSB)
3. H(q[2]) - prepare superposition
4. CZ(q[1], q[2]) - controlled-Z
5. H(q[2]) - convert back
6. M(q[2]) - measure result

Wait, the reference is already using H-CZ-H decomposition! So the reference is showing the alternative decomposition.

Let me trace through the state evolution:

Initial: |000>

After X(q[0]): |100>
After X(q[1]): |110>
After H(q[2]): |11+> = (1/√2)(|110> + |111>)

Now CZ(q[1], q[2]) applies Z to q[2] when q[1] is |1>:
|11+> = |1>(1/√2)(|10> + |11>) 
→ |1>(1/√2)(|10> - |11>) = |1>|-> = |11->

After H(q[2]): |11-> → (1/√2)|1>(|0> - (|0> - |1>)/√2) 

Wait, let me be more careful.

|+> = (|0> + |1>)/√2
|-> = (|0> - |1>)/√2

H|+> = |0>
H|-> = |1>

So after H(q[2]) on |11->:
|11-> → |111>

So the final state is |111>, and measuring q[2] gives |1> with probability 1.0.

This makes sense! The comparator checks if q[1] (MSB of the integer) is set, and since a=3, the MSB is set, so the result should be 1.

Now the question asks for an "alternative gate decomposition" using CNOT → H CZ H. 

But wait, the reference IS already using H-CZ-H. So perhaps the task is asking me to write the same thing in a slightly different way, or perhaps the reference is meant to be the "alternative" and the "standard" would be using CNOT directly?

Let me re-read the prompt: "Write an isQ program that implements the integer_comparator pattern using an alternative gate decomposition (CNOT -> H CZ H)."

So the alternative decomposition replaces CNOT with H-CZ-H. The implementation already shows this alternative decomposition.

The circuit should:
1. Encode a = 3 (or some integer)
2. Compare against a threshold
3. Use H-CZ-H instead of CNOT

Analyzing the circuit requirements, it's using q[1] as the MSB and checking if it's set (a >= 2).

So my answer should essentially be the same as the reference - using H-CZ-H decomposition.

Let me write the reasoning:

## Reasoning

1. Goal: Implement an integer comparator that checks if a >= threshold using H-CZ-H decomposition instead of CNOT.

2

## isqQA/quantum_algorithms/91_optimization_variant

- task_id: `isqQA/quantum_algorithms/91_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `optimization_variant`, `algorithm`, `BV算法的不同隐藏字符串实现`
- source: `qa_pipeline`
- dataset_index: `2953`

### Prompt

在Bernstein-Vazirani算法中，除了标准的受控非门（CNOT）结合辅助比特的实现方式外，有哪些基于相位神谕的优化变体？请详细推导这种无辅助比特的变体是如何通过仅使用单量子比特门来提取隐藏字符串信息的，并给出针对隐藏字符串 s=101 的具体isQ代码实现。

### Reference answer

<thought>
Bernstein-Vazirani算法的标准实现中，我们通常需要一个辅助量子比特（通常初始化为 |−⟩ 状态）来提取隐藏字符串 s 的信息。其神谕操作 Uf 通过受控非门将计算结果编码到辅助比特上。

然而，存在一种极其优雅的优化变体：相位神谕变体。这种变体不仅完全去除了辅助量子比特，降低了量子比特的硬件资源需求，而且其核心神谕操作可以仅通过单量子比特门（Z门）来实现，彻底消除了双比特纠缠门。

数学推导如下：
设隐藏字符串 s∈{0,1}^n。我们定义一个相位神谕 Us，其作用是翻转与 s 内积为1的计算基态的相位：
Us|x⟩=(−1)^(s⋅x)|x⟩

在无辅助比特的变体中，我们的输入状态是 |0⟩^⊗n。
第一步，施加 n 个Hadamard门，将状态转化为均匀叠加态：
|ψ1⟩=H^⊗n|0⟩^⊗n=1/√(2^n) ∑x∈{0,1}^n |x⟩

第二步，应用相位神谕 Us。根据定义，它为每个基态 |x⟩ 添加了相位因子 (−1)^(s⋅x) ：
|ψ2⟩=Us|ψ1⟩=1/√(2^n) ∑x (−1)^(s⋅x) |x⟩

第三步，再次施加 H^⊗n 门。由于 (−1)^(s⋅x) 的特性，Hadamard变换将直接映射回隐藏字符串状态：
H^⊗n (1/√(2^n) ∑x (−1)^(s⋅x) |x⟩) = |s⟩

关键点在于构建 Us。由于 s⋅x=s0x0⊕s1x1⊕…⊕s(n−1)x(n−1) ，且相位相乘等价于指数相加模2：
(−1)^(s⋅x)=(−1)^(s0x0)(−1)^(s1x1)…(−1)^(s(n−1)x(n−1))

因此，Us 可以分解为各个量子比特上的独立操作。在叠加态下，Z|x⟩=(−1)^x|x⟩。当且仅当 si=1 时，我们在第 i 个量子比特上施加一个Z门，即可实现乘积相位。
所以，Us=⨂(i=0 to n−1) Zi^(si)。
这种变体将原本需要纠缠的受控非门阵列完全转化为了单比特Z门阵列，大幅降低了量子线路深度。
</thought>
Bernstein-Vazirani (BV) 算法的优化变体中最具代表性的是**无辅助比特的相位神谕变体**。传统的BV算法使用一个额外的辅助量子比特（初始化为 |−⟩ 态）并通过一系列受控非门（CNOT）来实现黑盒函数 f(x)=s⋅x mod 2 。而在相位变体中，通过巧妙利用量子相位特性，我们不仅去除了辅助量子比特，还把复杂的双比特纠缠门全部替换为了单比特Z门。这极大地优化了量子线路的深度和硬件资源占用，提高了在含噪声量子设备上的鲁棒性。

在该变体中，黑盒神谕被重新定义为对计算基态引入相对相位：
Us|x⟩=(−1)^(s⋅x)|x⟩
对于隐藏字符串 s，由于指数上的模2加法等价于复数的乘法，该相位可以分解为独立位相位的乘积：
(−1)^(s⋅x) = (−1)^(s0x0) (−1)^(s1x1) ... (−1)^(s(n-1)x(n-1))
这意味着，在叠加态下，如果要让 xi=1 的分支获得 (−1)^(si xi) 的相位，只需要在对应 si=1 的量子线路上施加一个Z门。因为Z门在计算基下的作用为 Z|xi⟩=(−1)^xi|xi⟩。执行完单比特Z门后，再次施加Hadamard变换，利用 HZH=X 的性质，即可直接将隐藏字符串 s 转换为计算基态进行测量输出。

以3位隐藏字符串 s=101 （即 s0=1, s1=0, s2=1）为例，其无辅助比特变体的isQ代码实现如下：

import std;

qbit q[3]; // 全局声明3个量子比特，不再需要辅助比特

procedure main() {
    // 1. 初始化：对所有的量子比特施加Hadamard门，创建等概率叠加态
    for i in 0:3 {
        H(q[i]);
    }

    // 2. 构建相位神谕变体：隐藏字符串为 s=101
    // 只需在 s_i = 1 的对应位置施加Z门，无需引入任何纠缠门
    Z(q[0]); // s_0 = 1
    // s_1 = 0，所以跳过 q[1]
    Z(q[2]); // s_2 = 1

    // 3. 再次施加Hadamard门将相位变化转换为振幅（计算基态）变化
    for i in 0:3 {
        H(q[i]);
    }

    // 4. 在计算基下测量，将直接以100%的概率得到状态 |101⟩
    for i in 0:3 {
        M(q[i]);
    }
}

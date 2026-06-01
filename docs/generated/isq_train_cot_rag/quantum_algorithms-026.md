# ISQ training COT RAG corpus: quantum_algorithms shard 26

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2948

- task_id: `isqTrain/2948`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `basis_change`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3715`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```isq
import std;
qbit q[2];
// X-basis measurement: prepare |+> then measure in X basis
procedure main() {
    // X(q[0]); // BUG: missing initialization
    X(q[1]);
    H(q[0]);
    H(q[1]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug:** The `X(q[0])` gate is commented out, leaving `q[0]` in the initial `|0>` state instead of `|1>`.
2. **Fix:** Uncomment the `X(q[0])` line to flip `q[0]` to `|1>`.
3. **State evolution (corrected):**
   - Start: `|00>`
   - `X(q[0])`, `X(q[1])`: Flips both qubits to `|11>`.
   - `H(q[0])`, `H(q[1])`: Applies Hadamard to both, changing `|1>` to `|->` for each, resulting in the superposition `(|00> - |01> - |10> + |11>) / 2`.
   - Measurement: Yields a 25% probability for each of the states `|00>`, `|01>`, `|10>`, and `|11>`.

## isqTrain/3572

- task_id: `isqTrain/3572`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3142`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 2-qubit transverse-field Ising, 1 Trotter step.

### Chain-of-thought reasoning

The bug is in the CNOT direction for the ZZ interaction implementation.

For implementing exp(-i*J*dt*Z0Z1), the standard decomposition is:
1. CNOT(control=q[0], target=q[1])
2. Rz(2*J*dt, q[1])
3. CNOT(control=q[0], target=q[1])

The buggy code has the first CNOT as CNOT(q[1], q[0]) instead of CNOT(q[0], q[1]). This means q[1] is the control and q[0] is the target, which would implement exp(-i*J*dt*Z1Z0) — which is actually the same operator since Z0Z1 = Z1Z0, but the Rz needs to be applied to the target qubit. In the buggy code, the first CNOT has q[0] as target and q[1] as control, but the Rz is applied to q[1] (the control), not q[0] (the target). That's the inconsistency.

Let me trace through:

Buggy code:
- CNOT(q[1], q[0]): control=q[1], target=q[0]
- Rz(1.0, q[1]): applied to q[1] which is the CONTROL, not the target
- CNOT(q[0], q[1]): control=q[0], target=q[1]

This doesn't properly implement the ZZ interaction because after the first CNOT, the Rz should be applied to the target of that CNOT.

Correct code:
- CNOT(q[0], q[1]): control=q[0], target=q[1]
- Rz(1.0, q[1]): applied to q[1] which IS the target ✓
- CNOT(q[0], q[1]): control=q[0], target=q[1]

So the bug is that the first CNOT has its control and target swapped, and the Rz is applied to the wrong qubit as a result. The fix swaps the first CNOT to have q[0] as control and q[1] as target.

Let me verify the state evolution of the corrected circuit:

Starting from |00⟩:

1. CNOT(q[0], q[1]): control=|0⟩, so target unchanged. State: |00⟩

2. Rz(1.0, q[1]): Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}). Applied to q[1] which is |0⟩: e^{-i*0.5}|00⟩

3. CNOT(q[0], q[1]): Still |00⟩, no change. State: e^{-i*0.5}|00⟩

4. Rx(0.5, q[0]): Rx(θ)|0⟩ = cos(θ/2)|0⟩ - i*sin(θ/2)|1⟩
   cos(0.25)|0⟩ - i*sin(0.25)|1⟩ on q[0]

5. Rx(0.5, q[1]): same on q[1]

State: e^{-i*0.5} * [cos(0.25)|0⟩ - i*sin(0.25)|1⟩] ⊗ [cos(0.25)|0⟩ - i*sin(0.25)|1⟩]

|00⟩ amplitude: e^{-i*0.5} * cos²(0.25)
|01⟩ amplitude: e^{-i*0.5} * cos(0.25) * (-i*sin(0.25))
|10⟩ amplitude: e^{-i*0.5} * (-i*sin(0.25)) * cos(0.25)
|11⟩ amplitude: e^{-i*0.5} * (-i*sin(0.25))² = -sin²(0.25)

Probabilities:
P(|00⟩) = cos⁴(0.25) ≈ (0.9689)² ≈ 0.9389... hmm let me recalculate.

cos(0.25) ≈ 0.9689, sin(0.25) ≈ 0.2474

P(|00⟩) = cos⁴(0.25) ≈ 0.9689⁴ ≈ 0.8820
P(|01⟩) = cos²(0.25)*sin²(0.25) ≈ 0.9389 * 0.0612 ≈ 0.0575
P(|10⟩) = sin²(0.25)*cos²(0.25) ≈ 0.0575
P(|11⟩) = sin⁴(0.25

## isqTrain/110

- task_id: `isqTrain/110`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2210`

### Prompt

用isQ实现implements a variant of the qft_subcircuit pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this task carefully.

The task asks me to write an isQ program that:
1. Implements a variant of the qft_subcircuit pattern using q[2] -> q[4]
2. Uses a significantly expanded qubit register (more qubits than the base version)
3. Additional qubits should be left in the ground state |0>

Analyzing the circuit requirements:
- It uses `qbit q[4]` - a 4-qubit register
- It measures q[0], q[2], and q[3] - 3 qubits measured
- The circuit implements a phase estimation-like circuit:
  - Prepares |1> on q[1] using X gate
  - Creates superposition on q[0] using H
  - Applies controlled-Z (my_z) with q[0] as control and q[1] as target
  - Applies inverse QFT (just H for 1 qubit) on q[0]
  - Measures q[0], q[2], q[3]

Let me trace through the state evolution:

Initial state: |0000>

After X(q[1]): |0100>

After H(q[0]): (|0> + |1>)/√2 ⊗ |1> ⊗ |0> ⊗ |0> = (|0100> + |1100>)/√2

After ctrl my_z(q[0], q[1]):
- When q[0] = |0>: nothing happens, state |0100>
- When q[0] = |1>: Z applied to q[1], |1> becomes -|1>, so |1100> → -|1100>
Result: (|0100> - |1100>)/√2

After H(q[0]):
H on q[0]: (|0> - |1>)/√2 stays as the superposition part
Actually, let me be more careful. The state is (|0100> - |1100>)/√2

We can write this as: q[0] ⊗ q[1] ⊗ q[2] ⊗ q[3]
= (|0> - |1>)_0/√2 ⊗ |1>_1 ⊗ |0>_2 ⊗ |0>_3

Applying H to q[0]:
H(|0> - |1>)/√2 = (1/√2)(H|0> - H|1>) = (1/√2)((|0>+|1>)/√2 - (|0>-|1>)/√2) = (1/√2)(2|1>/√2) = |1>

So after H(q[0]): |1100>

Measuring q[0], q[2], q[3]:
- q[0] = 1 (this is the highest bit in the measurement bitstring)
- q[2] = 0
- q[3] = 0

Expected result: |100> with probability 1.0

This matches the predicted output!

Now, the task says "write an isQ program that implements a variant of the qft_subcircuit pattern using q[2] -> q[4]". This suggests I should modify the circuit to operate on qubits q[2] through q[4] instead of q[0] and q[1].

Wait, let me re-read. "q[2] -> q[4]" might mean the expanded register goes from index 2 to 4, or it might mean using qubits q[2] through q[4].

Actually, looking more carefully at the task, it says The implementation is provided, and I should "write an isQ program" - but then it says "Generate a reasoning section that explains..."

I think I'm being asked to generate reasoning for the given circuit implementation, not write new code.

Let me generate the reasoning for The implementation:

## Reasoning
1. The circuit implements a 1-qubit phase estimation of Z gate's eigenvalue (-1) on q[1], measuring q[0], q[2], and q[3].
2. 4 qubits are used (q[0]-q[3]); 3 are measured: q[0], q[2], q[3] (q[1] is not measured).
3. State evolution: |0000> →X(q[1])→ |0100> →H(q[0])→ (|0100>+|1100>)/√2 →ctrl Z→ (|0100>-|1100>)/√2 →H(q[0])→ |1100>
4. The controlled-Z phase-kicks eigenvalue -1 onto the |1⟩ component of q[0], transforming |+⟩→|−⟩, which H

## isqExpand/algo/93

- task_id: `isqExpand/algo/93`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `qft`, `inverse_qft`, `superposition`, `phase_manipulation`
- source: `isq_expansion`
- dataset_index: `5577`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    H(q[2]);
    inv ctrl S(q[2], q[1]);
    H(q[1]);
    inv ctrl T(q[2], q[0]);
    inv ctrl S(q[1], q[0]);
    H(q[0]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## 电路分析

### 第一部分：状态准备
H(q[0]); H(q[1]); H(q[2]); 将|000>变为|+++>

### 第二部分：IQFT电路
1. H(q[2])
2. ctrl @[q[2]] inv S(q[1])
3. H(q[1])
4. ctrl @[q[2]] inv T(q[0])
5. ctrl @[q[1]] inv S(q[0])
6. H(q[0])

这是标准的3比特IQFT电路（无位反转）。

### 关键关系
QFT|000> = |+++>
因此 IQFT|+++> = |000>

预期结果：P(|000>) = 1.0

### Reference answer

{'predicted_probs': {'000': 1.0, '001': 0.0, '010': 0.0, '011': 0.0, '100': 0.0, '101': 0.0, '110': 0.0, '111': 0.0}, 'explanation': 'The first three H gates create the equal superposition |+++> = (1/sqrt(8)) * sum|x>. The remaining gates form the 3-qubit inverse QFT (IQFT) circuit: H(q[2]), ctrl inv S(q[1]), H(q[1]), ctrl inv T(q[0]), ctrl inv S(q[0]), H(q[0]). Since QFT|000> = |+++>, applying IQFT to |+++> recovers |000> with certainty. Therefore P(|000>) = 1.0.'}

## isqExpand/algo/99

- task_id: `isqExpand/algo/99`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `entanglement`, `basis_change`
- source: `isq_expansion`
- dataset_index: `3266`

### Prompt

帮我写一个isQ程序：implements Simon's algorithm for a 2-bit function with hidden period s=10. The function satisfies f(00)=f(10)=00 and f(01)=f(11)=01, i.e., f depends only on the second bit x1. Use q[0],q[1] as the input register and q[2],q[3] as the output register. Apply H to the input register before and after the oracle, then measure only q[0] and q[1].

### Chain-of-thought reasoning

## Reasoning
Goal: Simon's algorithm for s=10. f(x0,x1)=(0, x1) depends only on x1.

Oracle: CNOT(q[1], q[3]) copies x1 to output register.

1. H on input: uniform superposition
2. Oracle: CNOT(q[1], q[3]) entangles input and output
3. H on input: produces y such that y*s = 0 mod 2
   s=10: y0*1 + y1*0 = y0 = 0
   Solutions: y=00 (index 0) and y=01 (index 1), each prob 0.5

Expected: [0.5, 0.5, 0.0, 0.0]

## isqTrain/2711

- task_id: `isqTrain/2711`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2787`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];

procedure main(){
    H(q[0]);
    ctrl X(q[0],q[1]);

    int a = M(q[0]);
    int b = M(q[1]);
    print a - b;
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with two qubits initialized to the ground state: $|00\rangle$.
2. A Hadamard gate (H) is applied to qubit 0, creating a superposition: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
3. A CNOT gate is applied with qubit 0 as the control and qubit 1 as the target. This flips the state of qubit 1 when qubit 0 is $|1\rangle$, resulting in the maximally entangled Bell state: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
4. Both qubits are measured. The squared amplitudes of the final state yield equal probabilities for the $|00\rangle$ and $|11\rangle$ outcomes, while $|01\rangle$ and $|10\rangle$ have zero probability.

Predicted probability distribution:
["00: 0.5", "01: 0.0", "10: 0.0", "11: 0.5"]

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqExpand/algo/41

- task_id: `isqExpand/algo/41`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `3qubit`, `oracle`, `multi_controlled_z`
- source: `isq_expansion`
- dataset_index: `5251`

### Prompt

Implement a quantum circuit in isQ: implements Grover's algorithm on 3 qubits to search for the state |110>. Apply one Grover iteration (oracle + diffusion). The oracle should flip the phase of |110> only.

### Chain-of-thought reasoning

## Reasoning
Goal: 3-qubit Grover search for |110>.

Oracle for |110>:
- |110> means q[0]=1, q[1]=1, q[2]=0.
- The doubly-controlled Z naturally fires when all inputs are 1 (i.e., |111>).
- Apply X(q[2]) before and after CCZ so it fires when original q[2]=0.
- X(q[2]); ctrl @[q[0], q[1]] Z(q[2]); X(q[2]); marks |110>.

Diffusion: same 3-qubit diffusion operator.

For N=8, 1 solution, 1 iteration:
- P(|110>) = sin^2(3 * arcsin(1/sqrt(8))) = 25/32 = 0.78125
- P(each other) = (1 - 25/32)/7 = 1/32 = 0.03125

Expected probs: index 6 (|110>) = 0.78125, rest = 0.03125.

## isqQA/quantum_algorithms/134_hardware_limitations

- task_id: `isqQA/quantum_algorithms/134_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hardware_limitations`, `algorithm`, `量子递增/递减电路`
- source: `qa_pipeline`
- dataset_index: `5042`

### Prompt

量子递增电路在数学上能够实现状态 $|x\rangle$ 到 $|x+1 \pmod{2^n}\rangle$ 的映射。然而，在当前的NISQ（含噪声中等规模量子）设备上，随着量子比特数量 $n$ 的增加，该电路的保真度会急剧下降。请深入分析这一现象背后的物理与硬件局限性原因（特别是退相干的影响），并探讨如何用尽可能紧凑的isQ代码实现一个3比特的量子递增电路，以尽可能减少门深度。

### Reference answer

在NISQ（含噪声中等规模量子）设备上实现大规模量子递增或递减电路时，保真度急剧下降的核心原因在于**硬件局限性**与**退相干效应**的叠加影响。

首先，从算法映射到硬件的层面来看，一个 $n$ 比特的量子递增电路本质上是级联的多控门（如多控Toffoli门和CNOT门）。在超导量子计算机等实际硬件中，原生支持的仅仅是单比特门（如H, X, RX）和两比特门（如CNOT, CZ）。要实现多控非门，必须将其分解为基础门，这会导致电路深度和量子比特间的连接拓扑（拓扑受限增加了额外的SWAP操作）呈现指数级或多项式级增长。

其次，退相干是破坏量子信息的关键物理过程。量子比特的相干性受限于两个时间参数：纵向弛豫时间 $T_1$（能量丢失）和横向退相干时间 $T_2$（相位丢失）。当递增电路包含大量受控门时，电路的总执行时间 $T_{exec}$ 会迅速增加。一旦 $T_{exec}$ 接近或超过系统的 $T_1$ 和 $T_2$，量子态就会因环境噪声发生不可逆的坍缩或相位翻转。此外，两比特门的误差率通常比单比特门高出1到2个数量级，大量级联的两比特门会使得系统误差呈指数级累积，最终使得计算结果完全被噪声淹没。

为了在NISQ设备上尽可能缓解这些问题，我们需要利用数学上的等效变换，设计不引入额外辅助比特且深度最浅的递增电路。对于一个3量子比特系统，我们可以逆向思维，从最高位到最低位依次应用控制门。以下是使用isQ语言编写的无辅助比特、极简深度的3比特量子递增电路：

```isQ
import std;

qbit q[3];

procedure main() {
    // 假设初始态为 |011> (即十进制的3)
    X(q[0]);
    X(q[1]);
    
    // 执行递增操作 x -> x+1 mod 2^3
    // 逻辑：由于递增是逢二进一，最高位仅当低位全为1时才翻转
    // 我们利用控制门从高位向低位计算，避免使用辅助比特
    
    // 若 q[0] 和 q[1] 均为1，则翻转最高位 q[2]
    Toffoli(q[0], q[1], q[2]);
    
    // 若 q[0] 为1，则翻转 q[1]
    CNOT(q[0], q[1]);
    
    // 最低位 q[0] 无条件翻转
    X(q[0]);
    
    // 此时状态变为 |100> (即十进制的4)，验证成功
}
```

在上述代码中，我们将最高权重的多控门放在前面执行，这是因为当控制位不满足条件时，后续的门操作不会被触发（或者基于初态可以直接确定）。这种无辅助比特的设计不仅极大地节省了NISQ设备上极其有限的量子资源，而且通过仅使用1个Toffoli门、1个CNOT门和1个X门，将电路深度压缩到了物理极限。在真实硬件部署时，这种最简结构能够最小化门的累积误差，并使得总运行时间尽可能短，从而有效对抗退相干效应。

## isqTrain/2898

- task_id: `isqTrain/2898`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4915`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```isq
import std;
qbit q[1];
// Single qubit with Rx(pi/4)
procedure main() {
    Rx(0.7853982, q[0]);
    X(q[0]); // BUG: spurious X before measurement

    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: Line `X(q[0]);` is a spurious X gate inserted between the Rx rotation and measurement. It flips the qubit, swapping |0> and |1> probabilities.

2. **Fix**: Remove `X(q[0]);`. The corrected circuit applies only `Rx(π/4)` then measures directly.

3. **State evolution (corrected)**:
   - |0⟩ → Rx(π/4) → cos(π/8)|0⟩ - i·sin(π/8)|1⟩
   - P(|0⟩) = cos²(π/8) ≈ 0.8536, P(|1⟩) = sin²(π/8) ≈ 0.1464 ✓

## isqTrain/4083

- task_id: `isqTrain/4083`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3306`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[3];

unit grover_oracle(qbit q[3]) {
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[2]);
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

1.  **Analyze the Request:**
    *   Input: An isQ quantum program.
    *   Task: Predict the measurement output, describe probability distribution.
    *   Format: "## Circuit Analysis", 3-15 lines, no code blocks, end with probability distribution, use Dirac notation.
    *   Program Analysis:
        *   3 qubits `q[3]`.
        *   Initialize to $|+\rangle|+\rangle|+\rangle = \frac{1}{2\sqrt{2}} \sum_{x=0}^7 |x\rangle$.
        *   `grover_oracle`:
            *   `X(q[2])` -> flips $q_2$.
            *   `ctrl CZ(q[0], q[1], q[2])` -> applies $Z$ to $q_2$ if $q_0=1$ and $q_1=1$.
            *   `X(q[2])` -> flips $q_2$ back.
            *   Effectively, this flips the phase of states where $q_2$ is *originally* 0, and $q_0=1, q_1=1$. Wait, $X$ on $q_2$ changes $|0\rangle \to |1\rangle$, so if $q_2$ is 0, it becomes 1. The Toffoli-like gate (double-controlled-Z (ctrl @[c1, c2] Z(target))) acts if $q_0=1, q_1=1, q_2=1$. Then $X$ again.
            *   Let's trace exactly:
                Original state: $\sum_{x} \alpha_x |x\rangle$.
                `X(q[2])` transforms $|q_0 q_1 q_2\rangle \to |q_0 q_1 \neg q_2\rangle$.
                `ctrl CZ` (double-controlled-Z (ctrl @[c1, c2] Z(target))) applies phase -1 to $|110\rangle$ (since $q_2$ is flipped, the original $q_2=0$ state is now $|1\rangle$ in $q_2$, wait. Let's write it down.
                $X_2 |q_0 q_1 q_2\rangle = |q_0 q_1 \neg q_2\rangle$.
                double-controlled-Z (ctrl @[c1, c2] Z(target)) applies $Z$ to $q_2$ if $q_0=1, q_1=1$. So it gives phase -1 to $|111\rangle$.
                So we apply phase -1 to $|q_0 q_1 \neg q_2\rangle$ when it's $|111\rangle$. This means original state was $|110\rangle$.
                Then $X_2$ reverts $q_2$.
                So the oracle flips the phase of $|110\rangle$ (binary 6, decimal 6). Let's double check. `ctrl CZ` is a controlled-Z. It adds a -1 if all controls and target are 1. Controls: q0, q1. Target: q2. So phase -1 for $|q_0=1, q_1=1, q_2=1\rangle$. Before this, $q_2$ is flipped by X. So the original state $|1, 1, 0\rangle$ becomes $|1, 1, 1\rangle$, gets phase -1, then $q_2$ is flipped back to 0. Yes, the target state is $|110\rangle$.
        *   `grover_diffusion`:
            *   Standard diffusion operator: $H^{\otimes 3} X^{\otimes 3} double-controlled-Z (ctrl @[c1, c2] Z(target)) X^{\otimes 3} H^{\otimes 3}$.
            *   This reflects the state about the $|+\rangle^{\otimes 3}$ state.
        *   Initial state was $|+\rangle^{\otimes 3}$. The oracle flips the sign of $|110\rangle$. The diffusion amplifies the amplitude of $|110\rangle$.
        *   Since there are $N=8$ states and $M=1$ target state, one Grover iteration rotates the state vector exactly to the target state (geometrically, $\theta \approx \sin\theta = 1/\sqrt{8} = \sqrt{2}/4$, rotation is $2\theta$, $\sin(2\theta) = 2\sin\theta\cos\theta = 2(1/\sqrt{8})(\sqrt{7}/\sqrt{8}) = \sqrt{14}/8 \ne 1$).
        *   Wait, let's trace Grover's algorithm for N=8, M=1

### Reference answer

Dominant output states: |110> with probability ~0.78 each

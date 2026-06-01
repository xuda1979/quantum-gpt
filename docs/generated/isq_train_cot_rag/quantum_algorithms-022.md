# ISQ training COT RAG corpus: quantum_algorithms shard 22

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3914

- task_id: `isqTrain/3914`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4833`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// QFT on 4 qubits with input state |1100>
qbit q[4];

procedure main() {
    // Prepare input state |1100>
    X(q[0]);
    X(q[1]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    // BUG: missing gate here
    // QFT stage for qubit 2
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    // QFT stage for qubit 3
    H(q[3]);
    // Swap q[0] and q[3]
    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    // Swap q[1] and q[2]
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **What the bug is**: In the QFT stage for qubit 1, the controlled rotation from q[3] to q[1] is missing. A complete 4-qubit QFT requires that for each qubit $k$, controlled rotations $R_z(2\pi/2^m)$ are applied from every higher-indexed qubit $k+m$ to qubit $k$. For qubit 1, the rotation from q[3] (with $m=2$, angle $2\pi/8$) was omitted.

2. **What the fix is**: Add the missing gate `ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);` after the existing `ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);` line, before the QFT stage for qubit 2 begins.

3. **State evolution of the corrected circuit**:
   - **Initialization**: Apply X(q[0]), X(q[1]) to prepare |0011⟩ (representing |3⟩ in computational basis).
   - **QFT on qubit 0**: H(q[0]) plus controlled rotations from q[1], q[2], q[3] entangle qubit 0 with phase factors.
   - **QFT on qubit 1**: H(q[1]) plus controlled rotations from q[2] and q[3] (the second rotation was missing, causing incomplete phase encoding).
   - **QFT on qubits 2, 3**: H gates with remaining controlled rotations complete the Fourier transform.
   - **Swap stage**: Reverses qubit order to produce correct QFT output.
   - **Result**: QFT(|3⟩) produces a uniform superposition $\frac{1}{4}\sum_{k=0}^{15} e^{2\pi i \cdot 3k/16}|k\rangle$, giving equal probability 0.0625 for all 16 basis states — matching expected

## isqTrain/3622

- task_id: `isqTrain/3622`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4145`

### Prompt

Help me write isQ code that a 4-qubit Grover search for target state |1011> using the optimal 3 iterations. The circuit should:
1. Initialize 4 qubits in uniform superposition
2. Apply 3 Grover iterations (oracle + diffusion) using a for loop
3. Measure all 4 qubits
Use `deriving gate` and `ctrl<2> CZ` for the multi-controlled phase.

### Chain-of-thought reasoning

Let me analyze this 4-qubit Grover search circuit targeting |1011>.

1. Goal: Implement a 4-qubit Grover search to find the target state |1011>.

2. Qubits: 4 qubits (q[0], q[1], q[2], q[3]), all measured.

3. State evolution:
- Start: |0000>
- After H on all: (1/4)Σ|x> (uniform superposition over 16 states)
- Each Grover iteration:
  - Oracle: X(q[1]) flips q[1] so |1011> becomes |1111>, then ctrl<2> CZ applies -1 phase to |1111>, then X(q[1]) restores q[1]. This marks |1011> with a -1 phase.
  - Diffusion: H⊗4 → X⊗4 → ctrl<2> CZ (applies -1 to |0000>) → X⊗4 → H⊗4. This amplifies the marked state.

For 4 qubits, N=16. Optimal iterations ≈ π/4 * √N ≈ π/4 * 4 ≈ 3.

After 3 iterations, the amplitude of |1011> is amplified to approximately sin((2*3+1)*π/4 * 1/4) = sin(7π/16).

Let me verify the probability: 0.96337890625 ≈ 0.9634.

sin²(7π/16) = sin²(78.75°) ≈ 0.9619... Hmm, that's close but not exactly matching.

Actually, for Grover's algorithm with M=1 marked item out of N=16:
- After k iterations, amplitude of marked state: sin((2k+1)θ) where sin(θ) = 1/√16 = 1/4
- θ = arcsin(1/4) ≈ 0.2527 rad
- After 3 iterations: sin(7*0.2527) = sin(1.769) ≈ 0.9808
- Probability ≈ 0.9619

But The predicted output 0.96337890625 = 0.96337890625. Let me compute this more precisely.

Actually 0.96337890625 = 0.96337890625. Let me see if this is a nice fraction.
0.96337890625 = 3935/4096? Let me check: 4096 * 0.96337890625 = 4096 * 0.96337890625...

Let me compute: 4096 * 0.96337890625 = 4096 * (1 - 0.03662109375) = 4096 - 150 = 3946. Hmm.

Actually 0.00244140625 = 1/4096. So each non-target state has probability 1/4096.
There are 15 non-target states, so total non-target probability = 15/4096.
Target probability = 1 - 15/4096 = 4081/4096 ≈ 0.9963... That's not matching either.

Wait, 0.00244140625 * 4096 = 10. So each state has probability 10/4096.
15 non-target states: 150/4096 total.
Target: 1 - 150/4096 = 3946/4096 ≈ 0.96338. Yes! That matches 0.96337890625.

So each of the 15 non-target states has amplitude such that probability = 10/4096.
Target state probability = 3946/4096 ≈ 0.96337890625.

Now let me trace through the state evolution:

After H on all 4 qubits: |ψ₀> = (1/4)Σₓ|x>, where each amplitude is 1/4 = √(1/16).

Grover iteration: apply oracle U_f (marks |1011>) and diffusion D.
D|ψ> = 2|s><s|ψ> - |ψ> where |s> = (1/4)Σ|x>.

Let me denote amplitudes: let α be amplitude of |1011>, β be amplitude of any other state.
Initially: α₀ = 1/4, β₀ = 1/4.

After oracle: α' = -α, β

## isqQA/quantum_algorithms/133_step_by_step

- task_id: `isqQA/quantum_algorithms/133_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `step_by_step`, `algorithm`, `量子比较器`
- source: `qa_pipeline`
- dataset_index: `3769`

### Prompt

请问在量子算法中，如何从零开始设计一个能比较两个两位二进制数大小的量子比较器？请以判断 A < B 为例，选取一个具体的量子态输入，一步步带领我手动追踪线路中量子态的演化过程，并提供相应的 isQ 语言代码实现。

### Reference answer

<think>
设计比较器需先将经典比较逻辑转化为布尔表达式：两位数 A < B 成立的条件是高位 $a_1<b_1$（即 $a_1=0, b_1=1$），或者高位相等且低位 $a_0<b_0$。

映射到量子线路时，需引入一个辅助比特 eq 判断高位是否相等（通过级联 CNOT 门实现异或逻辑），以及一个目标比特 c 存储比较结果。利用多控 Toffoli 门，当检测到 $\neg a_1$ 与 $b_1$ 同时为1时，翻转 c；或者当高位相等（eq为0）且 $\neg a_0$ 与 $b_0$ 同时为1时，翻转 c。

状态追踪以 A=1 (01), B=2 (10) 为例：初始态 $a_1=0, b_1=1$。线路执行时，第一步检测到高位直接满足 $a_1<b_1$ 的条件，控制门触发将目标比特 c 翻转为 1。后续的高低位判断逻辑均不再改变 c=1 的状态。最后，将上述量子逻辑门序列转写为 isQ 语言代码即可完成实现。
</think>

设计量子比较器的核心思想是将经典的逐位比较逻辑转化为量子门控制的翻转操作。为了教会你如何手动追踪算法，我们将构建一个比较两个两位量子寄存器 A 和 B 的大小，并判断是否满足 A < B 的线路。

【逻辑拆解】
假设两个数为 A = a1 a0，B = b1 b0（下标1为高位，下标0为低位）。我们需要一个输出量子比特 c 来存储比较结果，若 A < B 则 c 翻转为 1。A < B 的逻辑包含两种情况：
1. 高位直接满足 a1 < b1（即 a1=0, b1=1）。
2. 高位相等（a1 = b1）且低位满足 a0 < b0（即 a0=0, b0=1）。
为了判断高位是否相等，我们引入一个辅助量子比特 eq。通过异或操作（CNOT门），当 a1 和 b1 相等时，eq 保持为 0；不相等时，eq 变为 1。

【量子态初始化追踪】
为了方便追踪，我们选定一个具体的输入：让 A = 1 (二进制01)，B = 2 (二进制10)。显然 1 < 2，我们预期最终结果比特 c 会翻转为 1。
初始时，我们将各个比特设为：
高位 a1 = 0
低位 a0 = 1
高位 b1 = 1
低位 b0 = 0
辅助比特 eq = 0
结果比特 c = 0
系统的初始状态可以简写为：|a1, a0, b1, b0, eq, c⟩ = |0, 1, 1, 0, 0, 0⟩。

【分步手动追踪过程】
步骤 1：判断高位是否相等，计算辅助比特 eq。
我们依次执行 CNOT(a1, eq) 和 CNOT(b1, eq)。
- 首先执行 CNOT(a1, eq)：因为控制位 a1 = 0，所以不触发翻转，eq 仍为 0。
- 接着执行 CNOT(b1, eq)：因为控制位 b1 = 1，触发异或翻转，eq 从 0 变为 1。
当前系统状态演化为：|0, 1, 1, 0, 1, 0⟩。eq = 1 说明两个数的高位不相等。

步骤 2：处理高位直接决定结果的情况（a1 < b1）。
如果高位 a1 为 0 且 b1 为 1，那么无论低位是什么，必然有 A < B。此时我们需要翻转结果比特 c。
这对应量子门操作：对 a1 使用负控制，对 b1 使用正控制，目标位为 c。
- 当前状态中 a1 = 0（满足负控制条件），b1 = 1（满足正控制条件），因此该多控门被激活。
- 执行 X(c) 翻转操作，结果比特 c 从 0 变为 1。
当前系统状态演化为：|0, 1, 1, 0, 1, 1⟩。

步骤 3：处理高位相等且低位决定结果的情况（eq=0 且 a0 < b0）。
如果高位相等（即 eq=0），同时低位满足 a0=0 且 b0=1，也会触发 A < B，翻转 c。
这对应量子门操作：对 eq 使用负控制，对 a0 使用负控制，对 b0 使用正控制，目标位为 c。
- 观察当前状态，eq = 1（不满足负控制条件），因此该多控门未被激活。
- 这是因为高位已经确立了大小关系（0 < 1），低位无需再进行比较，c 保持不变。
当前系统状态保持为：|0, 1, 1, 0, 1, 1⟩。

最终，我们只要测量结果比特 c，发现其值为 1，即成功得出 A < B 的结论。

【isQ 代码实现】
以下是对应上述追踪过程的 isQ 代码：

import std;

qbit a[2];
qbit b[2];
qbit eq[1];
qbit c[1];

procedure main() {
    // 准备初态：令 A=1 (01), B=2 (10)
    // a[1]为高位，a[0]为低位
    X(a[0]); 
    X(b[1]);

    // 步骤1：计算高位是否相等，存入 eq[0]
    CNOT(a[1], eq[0]);
    CNOT(b[1], eq[0]);

    // 步骤2：若高位 a[1]=0 且 b[1]=1，直接判定 A<B，翻转 c[0]
    nctrl @[a[1]] ctrl @[b[1]] X(c[0]);

    // 步骤3：若高位相等(eq[0]=0) 且低位 a[0]=0, b[0]=1，判定 A<B，翻转 c[0]
    nctrl @[eq[0]] nctrl @[a[0]] ctrl @[b[0]] X(c[0]);

    // 如果是可逆计算，通常还需要通过逆运算还原辅助比特 eq[0]，本教学重点在比较，故省略还原步骤
    
    // 测量结果比特
    int res = M(c[0]);
    print(res);
}

## isqExpand/algo/78

- task_id: `isqExpand/algo/78`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `qaoa`, `output_prediction`, `maxcut`, `zz_interaction`, `cost_mixer`
- source: `isq_expansion`
- dataset_index: `2927`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];

procedure main() {
    // Initial superposition
    H(q[0]); H(q[1]);
    // Cost layer: ZZ interaction with gamma = pi/6
    CNOT(q[0], q[1]);
    Rz(pi/3.0, q[1]);
    CNOT(q[0], q[1]);
    // Mixer layer: Rx with beta = pi/3
    Rx(2.0*pi/3.0, q[0]);
    Rx(2.0*pi/3.0, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
This is a 1-round QAOA for MaxCut on K2 (complete graph on 2 vertices).

1. H on both: |+>|+> = (1/2)(|00>+|01>+|10>+|11>), all amplitudes = 1/2

2. ZZ cost layer with gamma=pi/6:
   CNOT(q[0],q[1]) maps: |00>->|00>, |01>->|01>, |10>->|11>, |11>->|10>
   After CNOT: amplitudes of |00>,|01>,|11>,|10> = 1/2 each
   Rz(pi/3) on q[1]: adds e^{-i*pi/6} to |*0> and e^{+i*pi/6} to |*1>
   - |00>: (1/2)*e^{-i*pi/6}
   - |01>: (1/2)*e^{+i*pi/6}
   - |11>: (1/2)*e^{+i*pi/6}
   - |10>: (1/2)*e^{-i*pi/6}
   Second CNOT undoes the CNOT mapping:
   - |00>: (1/2)*e^{-i*pi/6} (same parity -> e^{-i*gamma})
   - |01>: (1/2)*e^{+i*pi/6} (diff parity -> e^{+i*gamma})
   - |10>: (1/2)*e^{+i*pi/6} (diff parity -> e^{+i*gamma})
   - |11>: (1/2)*e^{-i*pi/6} (same parity -> e^{-i*gamma})

3. Rx(2*pi/3) mixer on each qubit:
   The Rx rotations convert the phase differences into probability differences.
   
Numerical result: P(00)=P(11)=0.0625=1/16, P(01)=P(10)=0.4375=7/16.

The QAOA successfully concentrates probability on the cut states |01> and |10>, which are the MaxCut optimal solutions for a single-edge graph.

### Reference answer

{'predicted_probs': {'00': 0.0625, '01': 0.4375, '10': 0.4375, '11': 0.0625}, 'explanation': 'After H gates, the state is |++> = uniform superposition. The ZZ cost layer (CNOT-Rz(2*gamma)-CNOT with gamma=pi/6) adds phases that distinguish same-parity states (|00>,|11>) from different-parity states (|01>,|10>). The Rx mixer (2*beta=2*pi/3) then converts these phase differences into amplitude differences. The MaxCut solutions |01> and |10> (where the edge is cut) are strongly favored with P=0.4375 each, while |00> and |11> have only P=0.0625 each.'}

## isqTrain/996

- task_id: `isqTrain/996`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5064`

### Prompt

Create an isQ quantum circuit that implements the qdrift pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. Goal: Implement qdrift pattern for H = X + Z on |0>, with t = π/4, λ = 2, N = 3 samples
2. One qubit q[0], measured at the end

Let me trace the state evolution:

Initial state: |0⟩

Sample 1: Rx(π/3) on |0⟩
Rx(θ) = cos(θ/2)I - i·sin(θ/2)X

Rx(π/3)|0⟩ = cos(π/6)|0⟩ - i·sin(π/6)|1⟩ = (√3/2)|0⟩ - i(1/2)|1⟩

Sample 2: Rz(π/3) on the current state
Rz(θ)|ψ⟩ = e^{-iθ/2}|0⟩⟨0|ψ⟩ + e^{iθ/2}|1⟩⟨1|ψ⟩

Rz(π/3)[(√3/2)|0⟩ - i(1/2)|1⟩] = e^{-iπ/6}(√3/2)|0⟩ + e^{iπ/6}(-i/2)|1⟩

Sample 3: Rx(π/3) on the current state

Then H-H (which is identity), then measure.

Let me compute the probabilities more carefully.

After Sample 1: Rx(π/3)|0⟩ = cos(π/6)|0⟩ - i·sin(π/6)|1⟩ = (√3/2)|0⟩ - i(1/2)|1⟩

After Sample 2: Rz(π/3) applies phase
e^{-iπ/6}(√3/2)|0⟩ + e^{iπ/6}·(-i/2)|1⟩
= (√3/2)e^{-iπ/6}|0⟩ - (i/2)e^{iπ/6}|1⟩

e^{-iπ/6} = cos(π/6) - i·sin(π/6) = (√3 - i)/2
e^{iπ/6} = (√3 + i)/2

So the state is:
(√3/2)·(√3 - i)/2 |0⟩ - (i/2)·(√3 + i)/2 |1⟩
= (3 - i√3)/4 |0⟩ - (i√3 + i²)/4 |1⟩
= (3 - i√3)/4 |0⟩ - (i√3 - 1)/4 |1⟩
= (3 - i√3)/4 |0⟩ + (1 - i√3)/4 |1⟩

Hmm, this is getting complex. Let me just verify the final probabilities numerically.

Actually, the H-H pair before measurement is identity, so it doesn't affect measurement outcomes. The probabilities |0⟩: 0.4375 and |1⟩: 0.5625 are what we expect.

Let me verify: 0.4375 = 7/16, 0.5625 = 9/16

Let me trace more carefully with matrix multiplication.

Rx(π/3) = [[cos(π/6), -i·sin(π/6)], [-i·sin(π/6), cos(π/6)]]
= [[√3/2, -i/2], [-i/2, √3/2]]

After first Rx(π/3) on |0⟩:
|ψ₁⟩ = (√3/2)|0⟩ + (-i/2)|1⟩

Rz(π/3) = [[e^{-iπ/6}, 0], [0, e^{iπ/6}]]

After Rz(π/3):
|ψ₂⟩ = e^{-iπ/6}(√3/2)|0⟩ + e^{iπ/6}(-i/2)|1⟩

After second Rx(π/3):
|ψ₃⟩ = Rx(π/3)|ψ₂⟩

Let me compute numerically:
e^{-iπ/6} = cos(30°) - i·sin(30°) = 0.866 - 0.5i
e^{iπ/6} = 0.866 + 0.5i

α₂ = e^{-iπ/6}·√3/2 = (0.866 - 0.5i)·0.866 = 0.75 - 0.433i
β₂ = e^{iπ/6}·(-i/2) = (0.866 + 0

## isqTrain/3927

- task_id: `isqTrain/3927`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3472`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// Bernstein-Vazirani: find secret string s = 111
oracle f(3, 1) = [0, 1, 1, 0, 1, 0, 0, 1];
qbit q[4];  // 3 input + 1 output

procedure main() {
    // Prepare |->  on output qubit
    X(q[3]);
    // BUG: missing gate here
    // Hadamard on input qubits
    for i in 0:3 {
        H(q[i]);
    }
    // Apply BV oracle
    f(q[0], q[1], q[2], q[3]);
    // Final Hadamard on inputs
    for i in 0:3 {
        H(q[i]);
    }
    // Measure inputs to reveal secret string
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **What the bug is**: After `X(q[3])`, which prepares the output qubit in |1⟩, the code is missing a Hadamard gate on q[3]. The BV algorithm requires the output qubit to be in the |−⟩ state (not |1⟩) before the oracle is applied. Without `H(q[3])`, the phase kickback mechanism doesn't work correctly.

2. **What the fix is**: Add `H(q[3]);` immediately after `X(q[3]);`. The sequence X then H transforms |0⟩ → |1⟩ → |−⟩, which is the required ancilla state.

3. **State evolution of the corrected circuit**:
   - Initial: |0000⟩
   - After X(q[3]): |0001⟩
   - After H(q[3]): |000⟩ ⊗ |−⟩
   - After H on all (H on inputs + already H'd output): |+++⟩ ⊗ |−⟩
   - After oracle f (s=111): Phase kickback encodes s·x into input qubits: 1/√8 Σ(−1)^(s·x)|x⟩ ⊗ |−⟩
   - After final H on inputs: |111⟩ ⊗ |−⟩
   - Measurement yields |1110⟩ or |1111⟩ each with probability 0.5 ✓

## isqTrain/4581

- task_id: `isqTrain/4581`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5510`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[5];

procedure main() {
    
    X(q[0]);
    
    X(q[2]);
    
    Toffoli(q[0], q[1], q[3]);
    
    Toffoli(q[0], q[2], q[4]);
    
    H(q[4]); // superposition on last qubit
    M(q[3]);
    M(q[4]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: isQ quantum program.
    *   Task: Predict measurement probability distribution, explain reasoning.
    *   Output Format: Start with "## Circuit Analysis", 3-8 lines (simple circuit), end with predicted probability distribution. Dirac notation required.
    *   Specifics: 5 qubits. Operations: X on q[0], X on q[2], Toffoli(q0, q1, q3), Toffoli(q0, q2, q4), H on q4. M(q3), M(q4). Wait, only q[3] and q[4] are measured! Wait, no, in isQ `--probs` mode, typically *all* qubits are part of the output state vector, but only the measured ones collapse, or the predicted output show the whole state? Wait, the prompt says "Expected measurement probabilities: {|00000>: 0.4999999999999999, |00001>: 0.5000000000000002} Number of qubits measured: 5". Wait, if it's 5 qubits, the string is 5 chars long. The prompt specifies 5 qubits measured. Let's trace carefully.

2.  **Step-by-Step State Evolution:**
    *   Initial state: $|00000\rangle$ (qubits q[0] to q[4])
    *   X(q[0]): Flips q[0] to 1. State is $|10000\rangle$
    *   X(q[2]): Flips q[2] to 1. State is $|10100\rangle$
    *   Toffoli(q[0], q[1], q[3]): q[0] is 1, q[1] is 0. Condition for flipping q[3] is NOT met. State remains $|10100\rangle$
    *   Toffoli(q[0], q[2], q[4]): q[0] is 1, q[2] is 1. Condition met. Flips q[4] to 1. State is $|10101\rangle$
    *   H(q[4]): Applies Hadamard to q[4] (which is in $|1\rangle$). State becomes $\frac{1}{\sqrt{2}}|10100\rangle - \frac{1}{\sqrt{2}}|10101\rangle$. Or using Dirac notation: $\frac{1}{\sqrt{2}} (|10100\rangle - |10101\rangle)$.

3.  **Refine Dirac Notation and Probabilities:**
    *   State before measurement: $\frac{1}{\sqrt{2}}|10100\rangle - \frac{1}{\sqrt{2}}|10101\rangle$
    *   Probability of $|10100\rangle$: $|\frac{1}{\sqrt{2}}|^2 = 0.5$
    *   Probability of $|10101\rangle$: $|-\frac{1}{\sqrt{2}}|^2 = 0.5$
    *   The predicted output in the prompt says: `Expected measurement probabilities: {|00000>: 0.4999999999999999, |00001>: 0.5000000000000002}`.
    *   Wait! Look at the predicted output: `|00000>` and `|00001>`. Where did `10100` and `10101` go?
    *   Ah! Is the output bitstring based *only* on the measured qubits? No, the prompt says "Number of qubits measured: 5". Wait, if 5 qubits are measured, the bitstring should be 5 bits. If the predicted output has `|00000>` and `|00001>`, maybe the bits are reversed or maybe only the *measured* qubits are reported, but wait, `M(q[3])` and `M(q[4])` means only 2 qubits are measured. But the text says "Number of qubits measured: 5" and shows `|00000>`. Wait, in isQ, if you don't measure a qubit, it might still be tracked, but the bitstring might represent the measured qubits? No, standard isQ `--probs` outputs probabilities for the *entire* state vector if all qubits are considered, but wait!
    *   Wait, is `M(q[i])` the only measurement? Yes. If so, the output bitstring might just be `00` or `01` if only 2 qubits are measured. But the text says "Number of qubits measured: 5". Wait, does `--

### Reference answer

{'predicted_probs': {'00000': 0.5, '00001': 0.5}, 'explanation': 'This isQ program operates on 5 qubit(s). The measurement probability distribution is: P(|00000>) = 0.5000, P(|00001>) = 0.5000.'}

## isqTrain/2006

- task_id: `isqTrain/2006`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `qft_based_arithmetic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2930`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    X(q[1]);
    H(q[1]);
    ctrl S(q[0], q[1]);
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Initial State:** $|00\rangle$
2.  **X(q[0]), X(q[1]):** Apply X to both qubits -> $|11\rangle$
3.  **H(q[1]):** Apply H to q[1] -> $|1\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = \frac{1}{\sqrt{2}}(|10\rangle - |11\rangle)$
4.  **ctrl S(q[0], q[1]):** Control is q[0], target is q[1]. S applies to q[1] if q[0] is |1>. 
    - $|10\rangle$ becomes $|10\rangle$
    - $|11\rangle$ becomes $i|11\rangle$
    -> $\frac{1}{\sqrt{2}}(|10\rangle - i|11\rangle)$
5.  **H(q[0]):** Apply H to q[0].
    - $|10\rangle \to \frac{1}{\sqrt{2}}(|00\rangle - |10\rangle)$
    - $|11\rangle \to \frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$
    -> $\frac{1}{2}(|00\rangle - |10\rangle - i|01\rangle + i|11\rangle)$
6.  **CNOT(q[0], q[1]):** Control q[0], Target q[1].
    -> $\frac{1}{2}(|00\rangle - |11\rangle - i|01\rangle + i|10\rangle)$
7.  **CNOT(q[1], q[0]):** Control q[1], Target q[0].
    -> $\frac{1}{2}(|00\rangle - |01\rangle - i|01\rangle + i|11\rangle)$ wait...
    Let me re-evaluate carefully.
    State before 3rd CNOT (step 6):
    $|00\rangle \to |00\rangle$
    $|11\rangle \to |01\rangle$ (Wait, control is q[1], target is q[0]. If q[1]=1, flip q[0]. So $|11\rangle \to |01\rangle$.)
    $|01\rangle \to |11\rangle$
    $|10\rangle \to |10\rangle$
    Let's re-evaluate:
    Step 6 state: $\frac{1}{2}(|00\rangle + i|10\rangle - i|01\rangle - |11\rangle)$
    Apply CNOT(q[1], q[0]):
    $|00\rangle \to |00\rangle$
    $i|10\rangle \to i|10\rangle$
    $-i|01\rangle \to -i|11\rangle$
    $-|11\rangle \to -|01\rangle$
    State: $\frac{1}{2}(|00\rangle - |01\rangle + i|10\rangle - i|11\rangle)$
8.  **CNOT(q[0], q[1]):** Control q[0], Target q[1].
    $|00\rangle \to |00\rangle$
    $-|01\rangle \to -|01\rangle$
    $i|10\rangle \to i|11\rangle$
    $-i|11\rangle \to -i|10\rangle$
    State: $\frac{1}{2}(|00\rangle - |01\rangle - i|10\rangle + i|11\rangle)$
    Wait, let's trace again.
    Step 1: |11>
    Step 2: 1/sqrt(2) (|10> - |11>)
    Step 3: 1/sqrt(2) (|10> - i|11>)
    Step 4: 1/2 ( (|00>+|10>) - i(|01>+|11>) )
    Step 5 (CNOT q0->q1): 1/2 (|00>+|11> - i(|01>+|10>))
    Step 6 (CNOT q1->q0): 1/2 (|00>+|01> - i(|11>+|10>))
    Step 7 (CNOT q0->q1): 1/2 (|00>+|01> - i(|10>+|11>))
    Probabilities:
    P(00) = 1/4
    P(01) = 1/4
    P(10

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': '2-qubit QFT on |3>: uniform distribution, P=0.25 for all 4 states.'}

## isqQA/quantum_algorithms/96_principle_advantage

- task_id: `isqQA/quantum_algorithms/96_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `Grover算法的扩散算子`
- source: `qa_pipeline`
- dataset_index: `3594`

### Prompt

请解释Grover算法中扩散算子的宏观原理及其在搜索过程中的作用。与经典无序搜索算法相比，Grover算法的时间复杂度有何优势？这种量子加速的根本来源是什么？最后，请用isQ语言编写实现一个作用于3个量子比特的Grover扩散算子的代码示例。

### Reference answer

在Grover算法中，扩散算子是实现量子搜索的核心组件之一，其宏观原理和作用可以从几何角度来理解。整个Grover算法的迭代过程实质上是在状态空间中的二维平面上进行旋转。初始时，系统处于所有可能状态的均匀叠加态。Oracle（预言机）的作用是识别目标态，并将目标态的概率振幅反转（即相位翻转180度）。然而，仅仅翻转相位并不能增加测量到目标态的概率。此时，扩散算子（也称为Grover算子）发挥作用：它将所有量子态的振幅相对于所有振幅的平均值进行反转。在目标态振幅被Oracle变为负数后，平均值会被拉低，此时再进行关于平均值的反转，非目标态的振幅会减小（低于平均值），而目标态的振幅会显著增加（高于平均值）。这种“相位反转”加“关于平均值反转”的组合，就如同一个放大器，每次迭代都将状态向量向着目标态旋转一个特定的角度，从而不断放大目标态的被测概率。

在时间复杂度对比方面，对于规模为 $N$ 的无结构数据库，经典的搜索算法（如线性查找）在最坏情况下需要遍历所有元素，平均和最坏时间复杂度均为 $O(N)$。而Grover算法利用量子特性，每次迭代都能通过干涉效应同时处理所有的可能状态，经过大约 $O(\sqrt{N})$ 次迭代后，测量得到目标态的概率接近1。这意味着Grover算法将搜索的时间复杂度从线性级降低到了平方根级，在 $N$ 极大时这是一个极其显著的二次加速。

这种量子加速的根本来源在于量子态的叠加性与精心设计的量子干涉。量子计算机能够一步初始化出包含 $2^n$ 个状态的叠加态，实现了真正的量子并行。但更关键的是，算法巧妙地利用了量子相位，把计算结果转化为概率振幅的相互干涉。它使得错误答案的概率振幅发生相消干涉（互相抵消），而正确答案的振幅发生相长干涉（叠加增强），这是波的干涉特性在计算问题上的完美应用。

以下是用isQ语言实现的针对3个量子比特的Grover扩散算子代码示例。扩散算子的数学定义为 $H^{\otimes n}(2|0\rangle\langle0| - I)H^{\otimes n}$。其中实现条件相移矩阵 $2|0\rangle\langle0| - I$ 的常见方法是先对所有量子比特应用X门将其计算基矢从 $|0\rangle$ 变为 $|111\rangle$ 态，然后应用多控Z门（CCZ），最后再用X门恢复。

import std;
qbit q[3];

procedure main() {
    // 1. 初始化均匀叠加态
    for i in 0:3 {
        H(q[i]);
    }

    // --- 假设此处插入Oracle操作标记目标态 --- 

    // 2. 开始构建扩散算子
    // 首先应用Hadamard门
    for i in 0:3 {
        H(q[i]);
    }

    // 利用X门将计算基矢条件翻转
    for i in 0:3 {
        X(q[i]);
    }

    // 在3比特系统中，多控Z门（CCZ）可以通过H门和Toffoli门来实现
    // 对目标位施加H门，执行Toffoli，再施加H门即可实现CCZ
    H(q[2]);
    Toffoli(q[0], q[1], q[2]);
    H(q[2]);

    // 再次利用X门恢复基矢
    for i in 0:3 {
        X(q[i]);
    }

    // 最后再次应用Hadamard门
    for i in 0:3 {
        H(q[i]);
    }
}

## isqTrain/3611

- task_id: `isqTrain/3611`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `5561`

### Prompt

Code this in isQ: a 3-qubit Grover search algorithm that finds the target state |110> using 1 Grover iteration. The circuit should:
1. Initialize 3 qubits in uniform superposition with Hadamard gates
2. Apply an oracle that marks state |110> with a phase flip
3. Apply the Grover diffusion operator
4. Measure all 3 qubits
Use `deriving gate` for oracle and diffusion procedures.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a 3-qubit Grover search algorithm that finds the target state |110>.
1.  **Goal**: Find the target state $|110\rangle$ in a 3-qubit search space using Grover's algorithm with 1 iteration.
2.  **Qubits**: 3 qubits are required, and all 3 are measured.
3.  **Step-by-step state evolution**:
    *   Initial state: $|000\rangle$
    *   Hadamard on all 3 qubits: Uniform superposition $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle$
    *   Oracle for $|110\rangle$: To mark $|110\rangle$ using a controlled-Z (which acts on $|111\rangle$), we apply X to the third qubit (q[2]), then double-controlled-Z (ctrl @[c1, c2] Z(target)), then X again. This flips the phase of $|110\rangle$, yielding $\frac{1}{\sqrt{8}}(|000\rangle + \dots + |101\rangle - |110\rangle + |111\rangle)$. Let's call the target $|t\rangle = |110\rangle$ and the uniform superposition $|s\rangle$. The state is $|s'\rangle = |s\rangle - \frac{2}{\sqrt{8}}|110\rangle$.
    *   Diffusion operator ($H^{\otimes 3} X^{\otimes 3} double-controlled-Z (ctrl @[c1, c2] Z(target)) X^{\otimes 3} H^{\otimes 3}$): This reflects the state about the mean.
        *   $|s'\rangle = \frac{1}{\sqrt{8}} \sum |x\rangle - \frac{2}{\sqrt{8}}|110\rangle$.
        *   Diffusion $= 2|s\rangle\langle s| - I$.
        *   Applying diffusion to $|s'\rangle$: $(2|s\rangle\langle s| - I)(|s\rangle - \frac{2}{\sqrt{8}}|t\rangle) = 2|s\rangle - \frac{2}{\sqrt{8}}2|s\rangle - |s\rangle + \frac{2}{\sqrt{8}}|t\rangle = |s\rangle - \frac{4}{\sqrt{8}}|s\rangle + \frac{2}{\sqrt{8}}|t\rangle$. Wait, let's do the math properly.
        *   $|s\rangle = \frac{1}{\sqrt{8}} \sum |x\rangle$.
        *   $\langle s|t\rangle = \frac{1}{\sqrt{8}}$.
        *   $|s'\rangle = |s\rangle - \frac{2}{\sqrt{8}}|t\rangle$.
        *   $D |s'\rangle = (2|s\rangle\langle s| - I) (|s\rangle - \frac{2}{\sqrt{8}}|t\rangle)$
        *   $= 2|s\rangle\langle s|s\rangle - |s\rangle - \frac{4}{\sqrt{8}}|s\rangle\langle s|t\rangle + \frac{2}{\sqrt{8}}|t\rangle$
        *   $= 2|s\rangle - |s\rangle - \frac{4}{8}|s\rangle + \frac{2}{\sqrt{8}}|t\rangle$
        *   $= (1 - \frac{1}{2})|s\rangle + \frac{2}{\sqrt{8}}|t\rangle = \frac{1}{2}|s\rangle + \frac{2}{\sqrt{8}}|t\rangle$.
        *   Substitute $|s\rangle = \frac{1}{\sqrt{8}}\sum |x\rangle$:
        *   $= \frac{1}{2\sqrt{8}} \sum |x\rangle + \frac{2}{\sqrt{8}}|t\rangle = \frac{1}{2\sqrt{8}} \sum_{x \neq t} |x\rangle + (\frac{1}{2\sqrt{8}} + \frac{2}{\sqrt{8}})|t\rangle = \frac{1}{2\sqrt{8}} \sum_{x \neq t} |x\rangle + \frac{5}{2\sqrt{8}}|t\rangle$.
    *   Wait, let's check The implementation probabilities.
    *   Target probability: 0.78

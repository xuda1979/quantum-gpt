# ISQ training COT RAG corpus: quantum_algorithms shard 51

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3458

- task_id: `isqTrain/3458`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `interference`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `4875`

### Prompt

Implement the following in isQ: Bernstein-Vazirani for 5-bit secret string s=11111 in isQ.

All bits of s are 1, so the oracle applies CNOT from every input qubit to the ancilla.

Declare 5 input qubits and 1 ancilla. Measure input only.
Expected: |11111>.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Implement Bernstein-Vazirani to find 5-bit secret string s=11111 via phase kickback.

**Qubits**: 6 total (q[0..4] input, anc[0] phase oracle); measure input only.

**State evolution**:
1. Initialize |0⟩⁵|0⟩, apply X then H to ancilla: |0⟩⁵|−⟩
2. Apply H⊗⁵ to input: (1/√32)Σₓ|x⟩|−⟩
3. Oracle (CNOT each q[i]→anc): phase kickback yields (1/√32)Σₓ(-1)^(s·x)|x⟩|−⟩ where s·x = x₀⊕x₁⊕x₂⊕x₃⊕x₄
4. Apply H⊗⁵ to input: interferes to |s⟩|−⟩ = |11111⟩|−⟩

**Expected**: Measuring input yields |11111⟩ with probability 1.0, since H⊗⁵ on Σₓ(-1)^(s·x)|x⟩ collapses to exactly |s⟩.

## isqTrain/2043

- task_id: `isqTrain/2043`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1777`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    Rx(1.57079632679490, q[0]);
    Rx(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    Rx(-1.57079632679490, q[0]);
    Rx(-1.57079632679490, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the circuit**:
    *   Number of qubits: 2 ($q_0, q_1$)
    *   Initial state: $|00\rangle$
    *   `X(q[0])`: $\to |10\rangle$
    *   `CNOT(q[0], q[1])`: $\to |11\rangle$
    *   `Rz(\pi/8, q[1])` (0.392699... = $\pi/8$): $\to e^{-i\pi/16} |11\rangle$
    *   `CNOT(q[0], q[1])`: $\to e^{-i\pi/16} |10\rangle$
    *   `H(q[0]); H(q[1])`: $\to e^{-i\pi/16} |-\rangle_0 |-\rangle_1$
    *   `CNOT(q[0], q[1])`: $\to e^{-i\pi/16} |-\rangle_0 |-\rangle_1$ (Actually, H-CNOT-H on state gives something? Let's trace carefully.)
    
    Wait, let's track the exact state at each step for the first block:
    1. $|00\rangle$
    2. `X(q[0])` $\to |10\rangle$
    3. `CNOT(0, 1)` $\to |11\rangle$
    4. `Rz(\pi/8, 1)` $\to Rz_1(\pi/8)|11\rangle = e^{-i\pi/16}|11\rangle$
    5. `CNOT(0, 1)` $\to e^{-i\pi/16}|10\rangle$
    
    Next block:
    6. `H(q[0]); H(q[1])` $\to e^{-i\pi/16} (|-\rangle_0 \otimes |+\rangle_1)$
    Wait, $H|1\rangle = |-\rangle$. $H|0\rangle = |+\rangle$.
    So $|10\rangle \to |-\rangle \otimes |+\rangle$.
    7. `CNOT(0, 1)` on $|-\rangle|+\rangle$.
       $|-\rangle|+\rangle = \frac{1}{2}(|00\rangle - |10\rangle + |01\rangle - |11\rangle)$
       CNOT applies $X$ on 1 when 0 is 1.
       $\to \frac{1}{2}(|00\rangle - |11\rangle + |01\rangle - |10\rangle) = |-\rangle|-\rangle$.
       State is $e^{-i\pi/16} |-\rangle|-\rangle$.
    8. `Rz(\pi/8, 1)` on $|-\rangle|-\rangle$:
       $Rz(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$
       $Rz(\pi/8)|-\rangle = Rz(\pi/8)\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = \frac{1}{\sqrt{2}}(e^{-i\pi/16}|0\rangle - e^{i\pi/16}|1\rangle) = e^{-i\pi/16} \frac{1}{\sqrt{2}}(|0\rangle - e^{i\pi/8}|1\rangle) = e^{-i\pi/16} |\psi\rangle$.
       Overall phase $e^{-i\pi/8}$.
       So state is $e^{-i\pi/8} |-\rangle_0 \otimes (e^{-i\pi/16} |\psi\rangle_1) = e^{-i3\pi/16} |-\rangle_0 \otimes |\psi\rangle_1$.
       Actually, let's ignore global phase, just keep qubit 1 relative phase: $|-\rangle |\psi\rangle$ where $|\psi\rangle = \frac{1}{\sqrt{2}}(|0\rangle - e^{i\pi/8}|1\rangle)$.
    9. `CNOT(0, 1)` on $|-\rangle|\psi\rangle$:
       $|-\rangle_0 \otimes (a|0\rangle_1 + b|1\rangle_1)$.
       $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
       So state

### Reference answer

{'predicted_probs': {'01': 0.1464, '10': 0.8536}, 'explanation': 'Heisenberg Trotter on |10>: P(|01>)~0.146, P(|10>)~0.854.'}

## isqTrain/2732

- task_id: `isqTrain/2732`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1950`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
oracle g(3, 1) = [0, 0, 1, 1, 1, 1, 0, 0];
qbit q[3], anc;
procedure main(){
    for i in 0:3{
        H(q[i]);
    }
    X(anc);
    H(anc);
    g(q[0], q[1], q[2], anc);
    for i in 0:3{
        H(q[i]);
        int a = M(q[i]);
        print a;
    }
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Explain the isQ quantum program, compute the final state before measurement, and predict the probability distribution.
    *   **Input Program:**
        
    *   **predicted output:** `## Circuit Analysis` followed by 3-15 lines of concise step-by-step reasoning, ending with the probability distribution.

2.  **Deconstruct the Circuit:**
    *   Initial state: $|0000\rangle$ (q[0], q[1], q[2], anc). Let's use standard ordering $|q_2 q_1 q_0 \text{anc}\rangle$ or $|q_0 q_1 q_2 \text{anc}\rangle$. Since it's just 4 qubits, let's trace the states carefully. Let's use $q_0, q_1, q_2$ for the main register and $a$ for ancilla.
    *   Apply $H$ to $q_0, q_1, q_2$: State becomes $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle \otimes |0\rangle_a$.
    *   Apply $X$ then $H$ to `anc`: State becomes $|1\rangle_a \to |-\rangle_a$. Overall state is $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle \otimes |-\rangle_a$.
    *   Apply oracle $g(q[0], q[1], q[2], anc)$:
        *   Oracle vector $[0, 0, 1, 1, 1, 1, 0, 0]$ indicates the function $f(x)$.
        *   If $f(x) = 0$, the oracle leaves the state unchanged (except maybe phase, but $f(x) \in \{0,1\}$ means the oracle does $(-1)^{f(x)}$ on the ancilla in the $|-\rangle$ state).
        *   $f(0)=0$, $f(1)=0$, $f(2)=1$, $f(3)=1$, $f(4)=1$, $f(5)=1$, $f(6)=0$, $f(7)=0$.
        *   The oracle applies a phase of $(-1)^{f(x)}$ to the main register.
        *   State becomes $\frac{1}{\sqrt{8}} ( |0\rangle + |1\rangle - |2\rangle - |3\rangle - |4\rangle - |5\rangle + |6\rangle + |7\rangle ) \otimes |-\rangle_a$.
        *   Wait, let's map indices to standard binary:
            *   $x=0$ (000): $+1$
            *   $x=1$ (001): $+1$
            *   $x=2$ (010): $-1$
            *   $x=3$ (011): $-1$
            *   $x=4$ (100): $-1$
            *   $x=5$ (101): $-1$
            *   $x=6$ (110): $+1$
            *   $x=7$ (111): $+1$
    *   Apply $H$ to $q_0, q_1, q_2$ again:
        *   This is the standard Deutsch-Jozsa inverse Fourier Transform step.
        *   We need to find the resulting state.
        *   Let's analyze the phase function. It's a balanced function.
        *   Actually, we can find $y$ such that the state is $|y\rangle$.
        *   The state is $\frac{1}{\sqrt{8}} \sum_x (-1)^{f(x)} |x\rangle$.
        *   After $H^{\otimes 3}$, the state is $\frac{1}{8} \sum_y \sum_x (-1)^{x \cdot y + f(x)} |y\rangle$.

### Reference answer

{'predicted_probs': {'110': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3044

- task_id: `isqTrain/3044`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_inv`, `measurement_order`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `995`

### Prompt

Write isQ code for the following quantum task: applies CNOT and then its inverse (inv CNOT) to demonstrate gate reversal. The qubits should return to their pre-CNOT state.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `inv` syntax to reverse the CNOT.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply CNOT then its inverse to verify that `inv CNOT` perfectly reverses the operation, returning qubits to their pre-CNOT state.
Two qubits are used, both measured.

State evolution:
1. **|00⟩** — initial state
2. **X(q[0])** → |10⟩
3. **H(q[0])** → (|00⟩ − |10⟩)/√2 = |−0⟩
4. **CNOT(q[0], q[1])** → (|00⟩ − |11⟩)/√2 (entangled Bell-like state)
5. **inv CNOT(q[0], q[1])** → (|00⟩ − |10⟩)/√2 = |−0⟩ (CNOT is self-inverse, so inv reverses it exactly)
6. **H(q[0])** → |10⟩

The final state is |10⟩, so measurement yields {|10⟩: 1.0}.

## isqTrain/3538

- task_id: `isqTrain/3538`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `ancilla_usage`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `573`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```
import std;

qbit q[5];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[3]);
    CNOT(q[0], q[4]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit initializes 5 qubits in |0>. An X gate is applied to q[0], followed by a sequence of CNOT gates with q[0] as the control and q[1] through q[4] as targets.
2. **State Evolution:**
   - Initial state: |00000>
   - `X(q[0])` flips q[0] to |1>, resulting in state |10000>.
   - `CNOT(q[0], q[1])` flips q[1] to |1>, giving |11000>.
   - `CNOT(q[0], q[2])` flips q[2] to |1>, giving |11100>.
   - `CNOT(q[0], q[3])` flips q[3] to |1>, giving |11110>.
   - `CNOT(q[0], q[4])` flips q[4] to |1>, giving |11111>.
3. **Final State:** The system is in the deterministic state |11111>.
4. **Predicted Distribution:** The measurement will always yield the basis state where all qubits are 1. With `q[0]` as the highest bit and `q[4]` as the lowest, the measured bitstring is '11111' (index 31).

**Probabilities:**
- 31: 1.0 (100%)

### Reference answer

{'predicted_probs': {'11111': 1.0}, 'explanation': 'The output is |11111> with probability 1.0'}

## isqExpand/algo/156

- task_id: `isqExpand/algo/156`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `shor_algorithm`, `quantum_phase_estimation`, `order_finding`, `modular_arithmetic`, `continued_fraction`, `integer_factorization`
- source: `qa_pipeline`
- dataset_index: `3558`

### Prompt

解释Shor算法分解N=15的过程：选择a=11，如何通过量子相位估计找到周期r？

### Chain-of-thought reasoning

首先计算a=11模15的阶：11^1=11(mod 15), 11^2=121=1(mod 15)，所以r=2。Shor算法的核心是量子相位估计求阶。构造酉算子U|y⟩=|11y mod 15⟩，需要4个工作比特表示0-14。使用t=8个计数比特做QPE。初始工作比特设为|1⟩，这是U的周期态叠加。由于r=2，|1⟩=(1/r)Σ|u_s⟩，测量计数比特以等概率得到相位φ=s/r。若s=1，φ=1/2，对应测量值128。连分数展开128/256=1/2得r=2。后处理：gcd(11^1-1,15)=5，gcd(11^1+1,15)=3，得到因子分解15=3×5。注意若s=0（测量值为0），需重新运行算法。

### Reference answer

Shor算法分解N=15，选择a=11的完整过程如下：

**第一步：经典预处理**
选定N=15，随机选择a=11，满足gcd(11, 15)=1。
目标是找到最小的正整数r（阶），使得 11^r ≡ 1 (mod 15)。

**第二步：构造量子Oracle**
定义酉变换 U|y⟩ = |11y mod 15⟩，作用于4个工作量子比特（因为⌈log₂15⌉=4）。
U的幂次：
- U|1⟩ = |11⟩
- U²|1⟩ = |11² mod 15⟩ = |121 mod 15⟩ = |1⟩
因此周期 r = 2。

**第三步：量子相位估计（QPE）**
使用t=8个计数量子比特（精度需求），4个工作比特初始化为|1⟩（即|0001⟩）。

QPE电路结构：
1. 对8个计数比特各施加H门，创建均匀叠加
2. 对第k个计数比特施加受控-U^(2^k)操作
3. 对计数比特施加逆量子傅里叶变换（IQFT）
4. 测量计数比特

U的特征值结构：|u_s⟩对应的特征值为exp(2πis/r)，s=0,...,r-1。
初始态|1⟩ = (1/2)(|u_0⟩ + |u_1⟩)（因为r=2），测量以等概率得到s=0或s=1。

**第四步：读出相位并求周期**
若测得s=1，则相位φ = s/r = 1/2。
8比特测量的十进制值为 m = φ × 2^8 = 128（二进制10000000）。

通过连分数展开：φ = 128/256 = 1/2 → r = 2。

**第五步：经典后处理求因子**
已知r=2（偶数），计算：
- gcd(11^(r/2) - 1, 15) = gcd(11-1, 15) = gcd(10, 15) = 5
- gcd(11^(r/2) + 1, 15) = gcd(11+1, 15) = gcd(12, 15) = 3

验证：15 = 3 × 5 ✓

**关键量子资源**：总共需要8+4=12个量子比特，受控-U操作需要实现模乘法门电路，这是Shor算法中最消耗资源的部分。

## isqTrain/953

- task_id: `isqTrain/953`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `hamiltonian_simulation`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2482`

### Prompt

帮我写一个isQ程序：implements the pauli_evolution pattern with modified rotation parameters (num_pi2s_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement Pauli-Z evolution with a modified rotation angle Rz(π/3) (changed from π/2 to π/3) on a superposition state
2. One qubit (q[0]) is used and measured
3. State evolution:
   - |0> → H → |+> = (|0>+|1>)/√2
   - Rz(π/3) applies phase: (e^(-iπ/6)|0> + e^(iπ/6)|1>)/√2
   - Second H converts phase to amplitude: cos(π/6)|0

## isqTrain/3888

- task_id: `isqTrain/3888`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3219`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// QPE with 2-bit precision for phase pi/2
// Unitary: Rz(theta) with eigenvalue e^{i*theta/2} on |1>
qbit q[3];

procedure main() {
    // Prepare eigenstate |1> on target qubit
    X(q[2]);
    // Hadamard on precision qubits
    H(q[0]); H(q[1]);
    // Controlled unitary applications
    ctrl Rx(2.0 * 3.14159265358979 * 2.0 / 4.0 * 1.0, q[0], q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 2.0 / 4.0 * 2.0, q[1], q[2]);
    // Inverse QFT on precision register
    // For 2 qubits: SWAP, then H + controlled-Rz†
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    H(q[1]);
    // Measure precision qubits
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze this code carefully.

The task is 2-bit Quantum Phase Estimation (QPE) for phase π/2.

The unitary is Rz(θ) and we're looking at the eigenstate |1⟩. Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]], so on |1⟩, the eigenvalue is e^{iθ/2}.

For phase π/2, we need e^{iθ/2} = e^{iπ/2}, so θ = π.

Wait, let me re-read the code. The comment says "phase pi/2" and the unitary is Rz with eigenvalue e^{iθ/2} on |1⟩.

Looking at the controlled unitary applications:
- `ctrl Rz(2.0 * pi * 2.0 / 4.0 * 1.0, q[0], q[2])` → Rz(pi) applied once
- `ctrl Rz(2.0 * pi * 2.0 / 4.0 * 2.0, q[1], q[2])` → Rz(2*pi) applied once... wait that's Rz(2pi) which is trivial up to global phase.

Hmm, let me reconsider. The formula `2.0 * pi * 2.0 / 4.0` simplifies to `pi`. So:
- First: Rz(pi * 1.0) = Rz(pi) — applied once
- Second: Rz(pi * 2.0) = Rz(2pi) — applied once... but wait, this is supposed to be 2 applications of the unitary (2^1 times), so it should be Rz(2*pi) = Rz(2pi).

But Rz(2pi) on |1⟩ gives eigenvalue e^{i*2pi/2} = e^{i*pi} = -1.

And Rz(pi) on |1⟩ gives eigenvalue e^{i*pi/2} = e^{i*pi/2} = i.

So the phase is π/2 (from Rz(π) giving eigenvalue i = e^{iπ/2}).

Wait, but then the second controlled operation should apply the unitary twice. If the unitary is Rz(π), then applying it twice gives Rz(2π), and the eigenvalue for that is e^{i*2π/2} = e^{iπ} = -1.

In QPE with phase φ = 1/4 (binary 0.01 in 2 bits), we'd expect measurement result 01.

The predicted output {|101⟩: 0.853553, |111⟩: 0.146447}. The qubit q[2] is the target (always |1⟩), and q[0], q[1] are precision qubits. With measurement bitstring where earlier measured = higher bit: M(q[0]) is higher bit, M(q[1]) is lower bit.

So 101 means q[0]=1, q[1]=0, q[2]=1 → precision register reads 10 (binary) = 2.
And 111 means q[0]=1, q[1]=1, q[2]=1 → precision register reads 11 (binary) = 3.

Phase 10 (binary) = 2/4 = 1/2, so φ = 1/2. That means the eigenvalue is e^{2πi * 1/2} = e^{πi} = -1.

Hmm wait, that doesn't match phase π/2 = 1/4 of full rotation. Let me reconsider.

Actually, QPE estimates the phase φ where eigenvalue = e^{2πiφ}. If φ = 1/4, the 2-bit estimate would be 01, giving measurement 01x. But The predicted output 10x with probability ~85% and 11x with ~15%.

This means the actual phase being estimated is φ = 1/2 (since 10 in binary = 2, 2/4 = 0.5). 

Let me reconsider. With Rz(π) on |1⟩: eigenvalue = e^{iπ/2}. So φ = (π/2)/(2π) = 1/4.

For 2-bit QPE with φ = 1/4 = 0.01 in binary:
- The ideal measurement would be 01.

But expected is 10. So something else is going on.

Wait, maybe I need to reconsider what unitary is being applied. Let me look at the corrected code again:

Correct code uses `ctrl Rz(2.0 * pi

## isqTrain/3015

- task_id: `isqTrain/3015`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2940`

### Prompt

Help me write isQ code that creates a 3-qubit GHZ state and then applies an X gate to qubit 1.

Requirements:
- Declare `qbit q[3];` at global scope.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a 3-qubit GHZ state and apply an X gate to qubit 1, yielding a superposition of |010⟩ and |101⟩.

Three qubits q[0], q[1], q[2] are declared globally and all are measured.

State evolution:
1. |000⟩ — initial state
2. H(q[0]) → (|000⟩ + |100⟩)/√2
3. CNOT(q[0], q[1]) → (|000⟩ + |110⟩)/√2
4. CNOT(q[1], q[2]) → (|000⟩ + |111⟩)/√2 — standard GHZ state
5. X(q[1]) → (|010⟩ + |101⟩)/√2

Measurement probabilities: {|010⟩: 0.5, |101⟩: 0.5} — equal superposition of the two basis states, each with amplitude 1/√2 giving probability |1/√2|² = 0.5.

## isqTrain/3619

- task_id: `isqTrain/3619`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `5486`

### Prompt

I need an isQ program to a 4-qubit Grover search for target state |0101> using the optimal 3 iterations. The circuit should:
1. Initialize 4 qubits in uniform superposition
2. Apply 3 Grover iterations (oracle + diffusion) using a for loop
3. Measure all 4 qubits
Use `deriving gate` and `ctrl<2> CZ` for the multi-controlled phase.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement 4-qubit Grover search to find target state |0101> with optimal 3 iterations.

**Qubits:** 4 qubits (q[0..3]), all measured at the end.

**State evolution:**
1. **Initialization:** |0000> → H⊗4 → (1/4)Σ|x> (equal superposition over 16 states)
2. **Oracle for |0101>:** X(q[0]) and X(q[2]) transform |0101> to |0000>; `ctrl<2> CZ` applies -1 phase to |0000>; X gates restore — result: only |0101> picks up π phase
3. **Diffusion:** H⊗4 → X⊗4 maps mean state to |1111>; `ctrl<2> CZ` adds π phase to |1111>; X⊗4 → H⊗4 reflects amplitudes about the mean, amplifying |0101>
4. **Three iterations** rotate the state vector toward |0101> by ~2·arcsin(1/4) per iteration ≈ 3×29.0° ≈ 87°, reaching amplitude ≈ 0.981

**Expected probabilities:** |0101> ≈ 96.3% (amplitude ~0.981), all other 15 states ≈ 0.24% each (~0.049²), consistent with near-optimal Grover amplification for N=16 with R=3 iterations.

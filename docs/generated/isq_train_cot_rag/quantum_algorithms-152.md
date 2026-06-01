# ISQ training COT RAG corpus: quantum_algorithms shard 152

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3457

- task_id: `isqTrain/3457`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `interference`, `ancilla_usage`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3164`

### Prompt

I need an isQ program to Bernstein-Vazirani for 4-bit secret string s=1101 in isQ.

Declare 4 input qubits and 1 ancilla. Measure input only.
Expected: |1101>.

### Chain-of-thought reasoning

## Reasoning
Goal: Identify the 4-bit secret string s=1101 via the Bernstein-Vazirani algorithm using a phase oracle.

Qubits: 4 input qubits (measured) + 1 ancilla (unmeasured).

State evolution:
1. Initialize |0000>|0>, apply X then H to ancilla → |0000>|->
2. Apply H to all 4 inputs → (1/4)Σ_x|x>|->
3. Oracle for s=1101: CNOT from q[0], q[1], q[3] to ancilla encodes s·x as phase → (1/4)Σ_x (-1)^(s·x)|x>|-> where s=1101
4. Apply H⊗4 to input register: H⊗4 converts the phase encoding back to computational basis → |1101>|->
5. Measure input qubits → always yields 1101

Result: {|1101>: 1.0} since H⊗4 perfectly decodes the phase pattern into the secret string.

## isqTrain/811

- task_id: `isqTrain/811`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `99`

### Prompt

Help me write isQ code that implements the quadratic_form pattern. Include explicit identity operations in the circuit (X-X pair before M(q[1])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
The circuit evaluates a 1-bit quadratic form f(x) = x² mod 2 = x, measuring the result on q[1] after applying and then cancelling identity X gates.

**State evolution:**
1. Initial: |00⟩
2. H(q[0]): (|00⟩ + |10⟩)/√2
3. CNOT(q[0],q[1]): (|00⟩ + |11⟩)/√2 (copies x to result)
4. X(q[1]): (|01⟩ + |10⟩)/√2
5. X(q[1]): (|00⟩ + |11⟩)/√2 (cancels previous X — identity pair)
6. M(q[1]): Measures q[1] from Bell state

**Expected probabilities:** The final state (|00⟩ + |11⟩)/√2 yields P(|0⟩) = 0.5, P(|1⟩) = 0.5 since both |00⟩ and |11⟩ have equal amplitude and q[1]=0 in |00⟩, q[1]=1 in |11⟩.

## isqQA/quantum_algorithms/114_principle_advantage

- task_id: `isqQA/quantum_algorithms/114_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `principle_advantage`, `algorithm`, `HHL算法原理`
- source: `qa_pipeline`
- dataset_index: `3373`

### Prompt

请详细解释HHL（Harrow-Hassidim-Lloyd）算法求解线性方程组 $Ax=b$ 的宏观物理与数学原理，并分析其相较于经典算法在时间复杂度上的具体对比结果。量子指数级加速的根源究竟在哪里？这种加速在实际应用中伴随着哪些重要的限制条件？

### Reference answer

HHL算法是量子线性系统求解的里程碑，其宏观原理是通过量子相位估计和受控旋转等操作，巧妙地将经典矩阵的求逆过程转化为量子态的概率幅缩放。算法的核心流程可分解为四步：首先，将经典向量 $b$ 编码到量子态 $|b\rangle$ 中；其次，使用量子相位估计（QPE）提取厄米矩阵 $A$ 的特征值，将其叠加在特征值寄存器上；接着，引入辅助比特并通过受控旋转，将特征值的倒数 $1/\lambda$ 映射到辅助比特的振幅上；最后，通过逆量子相位估计解除纠缠。测量辅助比特，若得到目标结果，系统寄存器就会坍缩为方程的解 $|x\rangle \propto A^{-1}|b\rangle$。

在时间复杂度对比上，假设方程维度为 $N$，矩阵稀疏度为 $s$，条件数为 $\kappa$，精度为 $\epsilon$。经典最优算法（如共轭梯度法）的时间复杂度为 $O(N s \kappa \log(1/\epsilon))$。而HHL算法的时间复杂度约为 $O(\log(N) s^2 \kappa^2 / \epsilon)$。量子加速的根源在于希尔伯特空间的指数级表征能力与量子并行性。仅用 $\log(N)$ 个量子比特就能表征 $N$ 维向量，且QPE与受控旋转能够同时处理 $N$ 个特征值分量，从而在系统维度 $N$ 上实现了指数级加速。

然而，这种加速伴随三大限制：一是复杂度随条件数 $\kappa$ 呈平方级恶化，处理病态矩阵非常吃力；二是在误差 $\epsilon$ 上呈多项式级减速；三是量子态无法被完全读取，只能用于提取 $|x\rangle$ 的某些物理期望值。

以下是使用isQ语言编写的HHL算法结构示意代码，展示了核心的受控旋转与纠缠解除逻辑：

```isq
import std;

qbit ancilla[1];
qbit clock[2]; // 相位估计寄存器
qbit system[2]; // 存储向量 b 和 x

procedure main() {
    // 1. 状态准备：制备量子态 |b>
    H(system[0]);
    H(system[1]);
    
    // 2. 量子相位估计 (QPE) 提取 A 的特征值
    H(clock[0]);
    H(clock[1]);
    
    // 受控哈密顿量模拟 exp(-i*A*t) 的简化表达
    // ctrl @[clock[0]] Rz(0.5, system[0]);
    // ctrl @[clock[1]] Rz(0.25, system[1]);
    
    // 逆QFT以将相位转入基态幅角
    H(clock[1]);
    
    // 3. 受控旋转：提取特征值倒数 1/lambda 到 ancilla
    H(ancilla[0]);
    // 实际旋转角度由特征值 lambda 决定: Ry(arcsin(C/lambda))
    // ctrl @[clock[0]] Ry(pi/4, ancilla[0]);
    
    // 4. 逆相位估计 (IQPE)：解除 clock 与 system 的纠缠
    // 执行 QFT
    H(clock[1]);
    // 受控哈密顿量模拟的逆操作
    // inv ctrl @[clock[1]] Rz(0.25, system[1]);
    // inv ctrl @[clock[0]] Rz(0.5, system[0]);
    H(clock[0]);
    H(clock[1]);
    
    // 5. 测量辅助比特
    int r = M(ancilla[0]);
    
    // 若测得 1，则 system 态坍缩为 |x> ∝ A^{-1}|b>
    if (r == 1) {
        // 成功提取解
    }
}
```

## isqTrain/4090

- task_id: `isqTrain/4090`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3813`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[4];

unit grover_oracle(qbit q[4]) {
    X(q[0]);
    X(q[1]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[1]);
    X(q[0]);
} deriving gate

unit grover_diffusion(qbit q[4]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    for i in 0:3 {
        grover_oracle(q);
        grover_diffusion(q);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ quantum circuit implementing Grover's algorithm.
    *   Qubits: 4 (`q[0]`, `q[1]`, `q[2]`, `q[3]`).
    *   Goal: Predict the measurement output, provide probability distribution, and explain the circuit.
    *   Format: "## Circuit Analysis", 3-15 lines (or a bit more if complex, but be concise), NO code blocks, end with predicted probabilities.

2.  **Analyze the Circuit:**
    *   Initialization: `H(q[0]); H(q[1]); H(q[2]); H(q[3]);` -> Equal superposition $|+\rangle^{\otimes 4} = \frac{1}{4} \sum_{x=0}^{15} |x\rangle$. State amplitude is $1/4 = 0.25$.
    *   Oracle: `grover_oracle`
        *   `X(q[0]); X(q[1]);` -> Flips first two qubits.
        *   `ctrl<2> CZ(q[0], q[1], q[2], q[3]);` -> Wait, `ctrl<2>` means 2 controls. `CZ` usually takes 2 qubits (control, target). So `ctrl<2> CZ(q[0], q[1], q[2], q[3])` means controls are `q[0], q[1]` and `CZ` target is... wait. `CZ` already takes 2. If it's `ctrl<2> CZ`, that means 2 controls + 2 targets for CZ? Or maybe controls are `q[0]`, `q[1]` and `CZ` acts on `q[2]`, `q[3]`?
        *   Wait, standard Grover oracle applies a -1 phase to the target state.
        *   Target state identification: `X(q[0]); X(q[1])` before `ctrl<2> CZ` means the target state is $|00\rangle$ for `q[0], q[1]`. Since it's `ctrl<2> CZ(q[0], q[1], q[2], q[3])`, the CZ gate applies a Z to one of the others if the first two are 1? But wait, a multi-controlled Z on 4 qubits applies a phase of -1 to $|1111\rangle$. With `X` on `q[0], q[1]`, the condition becomes $|q_3 q_2 q_1 q_0\rangle = |x x 0 0\rangle$. Wait, let's trace carefully.
        *   Actually, let's look at `ctrl<2> CZ(q[0], q[1], q[2], q[3])`. In isQ, `ctrl<2>` means 2 control qubits. `CZ(c, t)` is a 2-qubit gate. So `ctrl<2> CZ` means a 4-qubit gate. The first 2 qubits are controls. The next 2 are arguments for `CZ`. If `q[0]` and `q[1]` are in state $|1\rangle$, `CZ(q[2], q[3])` is applied. `CZ` applies -1 phase if *both* its inputs are 1? No, `CZ` applies a Z gate to the target, which means it applies -1 phase if the target is $|1\rangle$ AND the control is $|1\rangle$. Wait, `CZ(c, t)` applies Z to `t` if `c` is 1. Z on $|1\rangle$ is $-|1\rangle$. So `CZ` applies -1 phase when BOTH qubits are 1.
        *   Therefore, `ctrl<2> CZ(q[0], q[1], q[2], q[3])` applies a -1 phase if `q[0]=1, q[1]=1, q[2]=1, q[3]=1`.
        *   Let's re-read: `X(q[0]); X(q[1])` before, and `X(q[0]); X(q[1])` after. This means the oracle actually flips the phase of the state where $q_0=0, q_1=0$ and $q_2=1, q_3=1$. So the target state is $|1100\rangle$ (assuming q[3]q[2]q[1]q[0] bitstring, wait... $q_3q_

### Reference answer

Deterministic output: state |0011> with probability ~0.96

## isqTrain/2847

- task_id: `isqTrain/2847`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3575`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```isq
import std;
qbit q[2];
// entangled state with X on target
procedure main() {
    H(q[0]);
    // CNOT(q[0], q[1]); // BUG: missing CNOT
    X(q[1]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The `CNOT(q[0], q[1])` gate is commented out, removing the entanglement between the two qubits. Without CNOT, the circuit produces a product state (|01⟩ + |11⟩)/√2 instead of the intended entangled state.

2. **Fix**: Uncomment the `CNOT(q[0], q[1])` line to restore the Bell state preparation.

3. **State evolution of corrected circuit**:
   - |00⟩ → H(q[0]) → (|00⟩ + |10⟩)/√2
   - CNOT(q[0], q[1]) → (|00⟩ + |11⟩)/√2 (Bell state |Φ+⟩)
   - X(q[1]) → (|01⟩ + |10⟩)/√2
   - Measurement yields {|01⟩: 0.5, |10⟩: 0.5} ✓

## isqTrain/1256

- task_id: `isqTrain/1256`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1192`

### Prompt

Create an isQ quantum circuit that implements the error_correction_syndrome pattern. Include explicit identity operations in the circuit (H-H pair before M(syndrome[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
This circuit implements 3-qubit bit-flip code syndrome extraction: encoding |1⟩_L = |111⟩, introducing an X error on data[1], then detecting it via parity-check measurements on syndrome qubits.

**State evolution** (5 qubits: data[0-2], syndrome[0-1]):
- |00000⟩ → X(data[0]) → |10000⟩
- → CNOT(data[0],data[1]) → |11000⟩ → CNOT(data[0],data[2]) →

## isqTrain/59

- task_id: `isqTrain/59`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `578`

### Prompt

Create an isQ quantum circuit that implements the phase_kickback pattern but with a different initial state preparation (flip q[[1]] -> q[0]).

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program that implements the phase_kickback pattern with a different initial state preparation.

Let me trace through The implementation:

1. Initialize q[0] and q[1] to |00⟩
2. X(q[0]) → |10⟩ (flip q[0])
3. H(q[1]) → |10⟩ ⊗ (|0⟩+|1⟩)/√2 = (|10⟩+|11⟩)/√2
4. H(q[0]) → H on the first qubit of (|10⟩+|11⟩)/√2
   - |10⟩ → (|00⟩-|10⟩)/√2
   - |11⟩ → (|01⟩-|11⟩)/√2
   - So we get (|00⟩-|10⟩+|01⟩-|11⟩)/2

Wait, let me reconsider. The comments say:
- target in |->
- control in |+>

But the code does:
1. X(q[0])
2. H(q[1]) - comment says "Apply Hadamard gate for superposition"
3. H(q[0]) - comment says "control in |+>"

Wait, looking more carefully:
- X(q[0]) flips q[0]
- H(q[1]) puts q[1] in |+⟩ state
- H(q[0]) puts q[0] in... let me trace

Initial: |00⟩

After X(q[0]): |10⟩

After H(q[1]): |10⟩ ⊗ H|0⟩ = |1⟩ ⊗ |+⟩ = |1⟩ ⊗ (|0⟩+|1⟩)/√2 = (|10⟩+|11⟩)/√2

After H(q[0]): H on q[0]
H|1⟩ = |−⟩ = (|0⟩−|1⟩)/√2

So we get |−⟩ ⊗ |+⟩ = (|0⟩−|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2
= (|00⟩+|01⟩−|10⟩−|11⟩)/2

Now CNOT(q[0], q[1]) with q[0] as control and q[1] as target:

State: (|00⟩+|01⟩−|10⟩−|11⟩)/2

CNOT flips q[1] when q[0] is |1⟩:
- |00⟩ → |00⟩
- |01⟩ → |01⟩
- |10⟩ → |11⟩
- |11⟩ → |10⟩

So: (|00⟩+|01⟩−|11⟩−|10⟩)/2 = (|00⟩+|01⟩−|10⟩−|11⟩)/2

Wait that's the same? Let me redo:
- |00⟩ stays |00⟩
- |01⟩ stays |01⟩
- |10⟩ becomes |11⟩
- |11⟩ becomes |10⟩

So: (|00⟩+|01⟩−|11⟩−|10⟩)/2

This is the same as before... Hmm, that doesn't seem right for phase kickback.

Let me reconsider the circuit order:

Actually, looking at the code again:

So the order is:
1. X(q[0])
2. H(q[1])
3. H(q[0])
4. CNOT(q[0], q[1])
5. H(q[0])

Let me trace again:
Initial: |00⟩

After X(q[0]): |10⟩

After H(q[1]): q[1] was |0⟩, so H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2
State: |1⟩ ⊗ (|0⟩+|1⟩)/√2 = (|10⟩+|11⟩)/√2

After H(q[0]): H on q[0]
H|1⟩ = |−⟩ = (|0⟩−|1⟩)/√2
State: (|0⟩−|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 = (|00⟩+|01⟩−|10⟩−|11⟩)/2

After CNOT(q[0], q[1]): CNOT with q[0] control, q[1] target
- |00⟩ → |00⟩
- |01⟩ → |01⟩
- |10⟩ → |11⟩

## isqTrain/1201

- task_id: `isqTrain/1201`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1561`

### Prompt

实现以下量子计算任务（使用isQ）：implements the qaoa pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The goal is to implement a QAOA circuit for MaxCut on a 2-node graph with p=1, using an alternative gate decomposition where CNOT is replaced with H-CZ-H.

Let me trace through the circuit:

1. Initial state: |00⟩
2. After H(q[0]), H(q[1]): |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

Now for the cost layer, instead of CNOT(q[0], q[1]) - Rz(q[1]) - CNOT(q[0], q[1]), we use:
- H(q[1])
- CZ(q[0], q[1])
- H(q[1])
- Rz(-γ, q[1]) where γ = π/4
- H(q[1])
- CZ(q[0], q[1])
- H(q[1])

The decomposition CNOT(c, t) = H(t) - CZ(c, t) - H(t) is a well-known identity. So H-CZ-H = CNOT.

Let me verify: 
- CZ = diag(1, 1, 1, -1)
- (I ⊗ H) CZ (I ⊗ H) = CNOT

Yes, this is correct.

So the circuit is equivalent to:
1. H(q[0]), H(q[1]) → |++⟩
2. CNOT(q[0], q[1]) 
3. Rz(-π/4, q[1])
4. CNOT(q[0], q[1])
5. Rx(π/4, q[0])
6. Rx(π/4, q[1])

This is the standard QAOA p=1 circuit for MaxCut on 2 nodes with γ = π/4 and β = π/8.

The cost Hamiltonian is C = (1 - Z₀Z₁)/2, and the ZZ interaction is implemented by the CNOT-Rz-CNOT sequence.

Let me trace the state evolution more carefully:

After H(q[0]), H(q[1]): |ψ⟩ = |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

After CNOT(q[0], q[1]): |ψ⟩ = (|00⟩ + |01⟩ + |11⟩ + |10⟩)/2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

Wait, CNOT maps:
|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

So |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 → (|00⟩ + |01⟩ + |11⟩ + |10⟩)/2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 = |++⟩

Hmm, that's the same state. That's because CNOT on |++⟩ gives |++⟩ (since |+⟩|+⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2 and CNOT just rearranges the last two terms).

After Rz(-π/4, q[1]):
Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2})
Rz(-π/4) = diag(e^{iπ/8}, e^{-iπ/8})

So:
|00⟩ → e^{iπ/8}|00⟩
|01⟩ → e^{-iπ/8}|01⟩
|10⟩ → e^{iπ/8}|10⟩
|11⟩ → e^{-iπ/8}|11⟩

|ψ⟩ = (e^{iπ/8}|00⟩ + e^{-iπ/8}|01⟩ + e^{iπ/8}|10⟩ + e^{-iπ/8}|11⟩)/2

After CNOT(q[0], q[1]):
|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

|ψ⟩ = (e^{iπ/8}|00⟩ + e^{-iπ/8}|01⟩ + e^{-iπ/8}|10⟩ + e^{iπ/8}|11⟩)/2

Now applying Rx(π/4, q[0]) and Rx(π/4, q[1]):

Rx(θ) = cos(θ/2)I - i·sin(θ/2)X = [[cos(θ/2), -i·sin(θ/2)], [-i·sin(θ/2), cos(θ/2

## isqTrain/4582

- task_id: `isqTrain/4582`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1498`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[5];

procedure main() {
    
    X(q[4]);  // target different qubit
    
    X(q[2]);
    
    Toffoli(q[0], q[1], q[3]);
    
    Toffoli(q[0], q[2], q[4]);
    
    M(q[3]);
    M(q[4]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict probability distribution of an isQ quantum program.
    *   Input Program: 5-qubit program with X gates and Toffoli gates.
    *   Output Format: "## Circuit Analysis" section, step-by-step reasoning, final probability distribution. Dirac notation. Concise (3-15 lines).
    *   Target: q[3] and q[4] measured, but wait, the prompt mentions "Number of qubits measured: 5" and "Expected measurement probabilities: {|00001>: 1.0}". Let's trace carefully.

2.  **Analyze the Circuit:**
    *   Initial state: |00000> (q[0] to q[4])
    *   `X(q[4])`: State becomes |00001> (q[4] is flipped)
    *   `X(q[2])`: State becomes |00101> (q[2] is flipped)
    *   `Toffoli(q[0], q[1], q[3])`: Controls are q[0]=0, q[1]=0. Target is q[3]. Since controls are not 11, nothing happens. State remains |00101>.
    *   `Toffoli(q[0], q[2], q[4])`: Controls are q[0]=0, q[2]=1. Target is q[4]. Since controls are not 11, nothing happens. State remains |00101>.
    *   Measurements: `M(q[3])` and `M(q[4])`.

3.  **Refine State and Probabilities:**
    *   Wait, the prompt says "Expected measurement probabilities: {|00001>: 1.0}". Let me check the bitstring encoding. In isQ, typically a 5-qubit measurement without explicit bit combination is implicitly measured as q[4]q[3]q[2]q[1]q[0] or similar. However, the prompt says `Number of qubits measured: 5` and `{|00001>: 1.0}`.
    *   Let's check the state: |00101> (q[4]q[3]q[2]q[1]q[0]).
    *   q[4] = 0? No, `X(q[4])` means q[4] is 1.
    *   q[2] = 1, `X(q[2])`.
    *   So state is |q[4]=1, q[3]=0, q[2]=1, q[1]=0, q[0]=0> which is |10100> in q[4]..q[0] or |00101> in q[0]..q[4].
    *   Wait, if the predicted output is `{|00001>: 1.0}`, that implies the bitstring is read right-to-left (q[0] is highest bit) or maybe `|q[0]q[1]q[2]q[3]q[4]>`?
    *   Let's look at standard isQ bit ordering. Often, earlier measured qubits are higher bits.
    *   The prompt's predicted output says `{|00001>: 1.0}`. Let's re-read the `X(q[4])` and `X(q[2])`.
    *   If state is |10100> in q[0]..q[4], then it's `10100`.
    *   If `|00001>` is expected, then maybe q[4]=1 is the rightmost bit. So bitstring = q[0]q[1]q[2]q[3]q[4] = 00001. But q[2] was also flipped!
    *   Wait! `|00001>` in binary is decimal 1. If bitstring is q[4]q[3]q[2]q[1]q[0], then |00001> means q[0]=1. But we did `X(q[4])` and `X(q[2])`. This would mean q[4]=1, q[2]=1 -> bitstring `00101` (binary 5).
    *   Why does the prompt say `{|00001>: 1.0}`? Ah, look at the "circuit implementation" in the prompt! "Expected measurement probabilities: {|00001>: 1.0}". Is it a mistake in the prompt's reference, or did I misread?
    *   Let's re-read the circuit:
        *   `X(q[4])`
        *   `X(q[2])`
        *   Toffoli(0, 1, 3)

### Reference answer

{'predicted_probs': {'00001': 1.0}, 'explanation': 'This isQ program operates on 5 qubit(s). The measurement probability distribution is: P(|00001>) = 1.0000.'}

## isqTrain/3649

- task_id: `isqTrain/3649`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `4112`

### Prompt

I need an isQ program to the 4-qubit inverse QFT on input |0000>. Apply bit-reversal, then inverse controlled-Rz rotations and Hadamard gates in reverse order. Measure all qubits.

### Chain-of-thought reasoning

Looking at this problem, I need to analyze the provided isQ code and explain what it does. Let me trace through the circuit.

The code implements an inverse QFT on 4 qubits, but the input preparation section uses some swap (three-CNOT decomposition) gates (implemented as 3 CNOTs) and a Hadamard gate.

Let me trace the state evolution:

1. Initial state: |0000>

2. CNOT(q[0], q[3]) → |0000> (control is |0>, so no change)

3. CNOT(q[3], q[0]) → |0000> (control is |0>, so no change)

4. CNOT(q[0], q[3]) → |0000> (control is |0>, so no change)

Wait, these three CNOTs look like a swap operation (three-CNOT decomposition), but since the qubits are both |0>, nothing changes.

5. CNOT(q[1], q[2]) → |0000>

6. CNOT(q[2], q[1]) → |0000>

7. CNOT(q[1], q[2]) → |0000>

Again, another swap (three-CNOT decomposition) that does nothing because both qubits are |0>.

8. H(q[3]) → |0001> → (1/√2)(|0000> + |0001>)

Wait, let me be careful about the qubit ordering. q[3] is the last qubit. H applied to q[3]:
|0000> → (1/√2)(|0000> + |0001>)

9. ctrl Rz(-2π/4, q[3], q[2]): This applies Rz(-π/2) to q[2] controlled on q[3].

The Rz(-π/2) = Rz(-2π/4) applies a phase of e^(-iπ/4) to |0> and e^(iπ/4) to |1>.

Actually, Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]

So Rz(-π/2) = [[e^(iπ/4), 0], [0, e^(-iπ/4)]]

When q[3] = |1>, this rotation is applied to q[2].

State: (1/√2)(|0000> + e^(iπ/4)|0_2 0_1>_|1>_3)

Wait, I need to be more careful. The state is (1/√2)(|0_3 0_2 0_1 0_0> + |1_3 0_2 0_1 0_0>)

Hmm, the qubit ordering in the ket notation can be confusing. Let me use a consistent ordering where q[0] is the rightmost bit.

State after H(q[3]): (1/√2)(|0000> + |0001>) where the rightmost bit is q[0].

Wait, actually in the bitstring |q[3]q[2]q[1]q[0]>, H(q[3]) would give (1/√2)(|0000> + |1000>).

Let me use the convention that |abcd> means q[3]=a, q[2]=b, q[1]=c, q[0]=d.

After H(q[3]): (1/√2)(|0000> + |1000>)

9. ctrl Rz(-π/2, q[3], q[2]): When q[3]=|1>, apply Rz(-π/2) to q[2].

Since q[2] is |0>, Rz doesn't change it (it just adds a global phase to the |1> component of q[2], but q[2] is |0>).

State remains: (1/√2)(|0000> + |1000>)

10. H(q[2]): Apply H to q[2].
State: (1/√2)(1/√2)(|0000> + |0100>) + 1/√2)(|1000> + |1100>))
= (1/2)(|0000> + |0100> + |1000> + |1100>)

11. ctrl Rz(-2π/8, q[3], q[1]) = ctrl Rz(-π/4, q[3], q[1]): When q[3]=|1>, apply Rz(-π/4) to q[1].
Since q[1] is |0> in all components, this doesn't change anything.
State: (1/2)(|0000> + |

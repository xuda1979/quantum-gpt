# ISQ training COT RAG corpus: quantum_algorithms shard 16

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1183

- task_id: `isqTrain/1183`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `410`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

// Forrelation circuit: H-f-H-g-H structure
qbit q[2];

procedure main() {
    // First H layer
    H(q[0]); H(q[1]);
    // Phase oracle f: T on q[0], S on q[1]
    T(q[0]);
    S(q[1]);
    // Middle H layer (Fourier transform)
    H(q[0]); H(q[1]);
    // Phase oracle g: S on q[0], T on q[1]
    S(q[0]);
    T(q[1]);
    // Final H layer
    H(q[0]); H(q[1]);
    // Measure to sample from Forrelation distribution
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

The user wants to analyze an isQ program and predict the probability distribution of measurement outcomes.
The circuit operates on 2 qubits, let's call them $q_0$ and $q_1$.
Initial state: $|00\rangle$
1. `H(q[0]); H(q[1]);`
State becomes $|++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.

2. `T(q[0]); S(q[1]);`
Apply $T \otimes S$.
State becomes $\frac{1}{2}(|00\rangle + e^{i\pi/4}|01\rangle + e^{i\pi/4}|10\rangle + e^{i3\pi/4}|11\rangle)$.
Wait, $T$ adds $e^{i\pi/4}$ to $|1\rangle$, $S$ adds $i = e^{i\pi/2}$ to $|1\rangle$.

3. `H(q[0]); H(q[1]);`
Apply $H \otimes H$.
Let's calculate the state for each term:
$H|00\rangle = |++\rangle$
$H(e^{i\pi/4}|01\rangle) = e^{i\pi/4}|+-\rangle$
$H(e^{i\pi/4}|10\rangle) = e^{i\pi/4}|-+\rangle$
$H(e^{i3\pi/4}|11\rangle) = e^{i3\pi/4}|--\rangle$
Sum = $\frac{1}{2}(|++\rangle + e^{i\pi/4}|+-\rangle + e^{i\pi/4}|-+\rangle + e^{i3\pi/4}|--\rangle)$
Since $|\pm\rangle = \frac{1}{\sqrt{2}}(|0\rangle \pm |1\rangle)$, we can expand this back to the computational basis.
Let's do it systematically.
$H \otimes H$ maps:
$|00\rangle \to \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
$|01\rangle \to \frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$
$|10\rangle \to \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$
$|11\rangle \to \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$

So the state after $H \otimes H$ is:
$\frac{1}{4} [ (1 + e^{i\pi/4} + e^{i\pi/4} + e^{i3\pi/4})|00\rangle + (1 - e^{i\pi/4} + e^{i\pi/4} - e^{i3\pi/4})|01\rangle + (1 + e^{i\pi/4} - e^{i\pi/4} - e^{i3\pi/4})|10\rangle + (1 - e^{i\pi/4} - e^{i\pi/4} + e^{i3\pi/4})|11\rangle ]$
Let $e^{i\pi/4} = \omega$. $e^{i3\pi/4} = \omega^3$.
$|00\rangle$ coeff: $1 + \omega + \omega + \omega^3 = 1 + 2\omega + \omega^3$.
$|01\rangle$ coeff: $1 - \omega^3$.
$|10\rangle$ coeff: $1 - \omega^3$.
$|11\rangle$ coeff: $1 - 2\omega + \omega^3$.

Wait, $e^{i\pi/4} = \frac{1+i}{\sqrt{2}}$.
$\omega = \frac{1+i}{\sqrt{2}}$.
$\omega^3 = \frac{-1+i}{\sqrt{2}}$.
$1 - \omega^3 = 1 - \frac{-1+i}{\sqrt{2}} = 1 + \frac{1-i}{\sqrt{2}}$.
$1 - \omega^3$ magnitude squared:
$|1 + \frac{1-i}{\sqrt{2}}|^2 = (1 + \frac{1}{\sqrt{2}})^2 + (-

### Reference answer

{'predicted_probs': {'0': 0.7285533905932737, '1': 0.125, '2': 0.12500000000000006, '3': 0.02144660940672625}, 'explanation': 'Parametric variant of isqEval/445. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3476

- task_id: `isqTrain/3476`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `interference`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `4587`

### Prompt

Implement a quantum circuit in isQ: Bernstein-Vazirani for 4-bit secret string s=0110 in isQ.
CNOT from q[1] and q[2] to ancilla.
Declare 4 qubits + 1 ancilla. Measure input only.
Expected: |0110>.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to identify the 4-bit secret string $s=0110$ using the Bernstein-Vazirani algorithm.
2. The circuit requires 5 qubits (4 input `q`, 1 ancilla `anc`), with only the 4 input qubits measured.
3. Initialization applies $X$ and $H$ to the ancilla, and $H$ to inputs, creating the state $\frac{1}{4}\sum_{x=0}^{15} |x\rangle |-\rangle$.
4. The oracle applies CNOTs from `q[1]` and `q[2]` to the ancilla, inducing a phase kickback of $(-1)^{x \cdot s}$, evolving the state to $\frac{1}{4}\sum_{x} (-1)^{x \cdot s} |x\rangle |-\rangle$.
5. Applying a final $H^{\otimes 4}$ to the input register interferes the phases perfectly, collapsing the superposition

## isqQA/quantum_algorithms/117_principle_advantage

- task_id: `isqQA/quantum_algorithms/117_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `振幅放大原理`
- source: `qa_pipeline`
- dataset_index: `1541`

### Prompt

在量子计算中，振幅放大算法（Amplitude Amplification，如Grover算法的核心）是如何实现相对于经典搜索算法的二次级加速的？请从其宏观原理出发，解释其时间复杂度的对比优势，并深入剖析量子加速的根本来源。最后，请使用isQ语言编写一段代码，展示如何在2量子比特系统中寻找目标态 |11⟩ 的单次振幅放大过程。

### Reference answer

振幅放大算法是量子计算中最经典的算法之一，它从宏观原理、时间复杂度到物理本质都展示了量子计算的独特魅力。

**宏观原理：**
振幅放大的核心思想是通过反复进行“相位翻转”和“关于均值的反转”操作，将目标解的概率振幅不断放大，同时压低非目标解的振幅。整个过程可以抽象为一个二维子空间（由目标态和均匀叠加态张成）中的旋转操作。设初始状态为所有可能态的均匀叠加 $|\psi\rangle = \frac{1}{\sqrt{N}} \sum_{x=0}^{N-1} |x\rangle$，目标态为 $|t\rangle$。我们定义一个投影算子，将状态分解为 $|\psi\rangle = \sin(\theta)|t\rangle + \cos(\theta)|t^\perp\rangle$，其中 $\sin(\theta) = \frac{1}{\sqrt{N}}$。每次振幅放大迭代包含两步：首先利用Oracle $U_f$ 对目标态的相位进行翻转；然后应用扩散算子 $U_s = 2|\psi\rangle\langle\psi| - I$。这两步结合等效于在上述二维空间中将状态向量向目标态 $|t\rangle$ 旋转了 $2\theta$ 的角度。

**时间复杂度对比与加速来源：**
对于一个规模为 $N$ 的无结构搜索问题，经典算法只能逐个检查，最坏和平均情况下的时间复杂度均为 $O(N)$。而在量子振幅放大算法中，经过 $k$ 次迭代后，系统状态与目标态的夹角变为 $(2k+1)\theta$。为了最大化测量到目标态的概率，我们需要旋转至接近 $\frac{\pi}{2}$，即 $(2k+1)\theta \approx \frac{\pi}{2}$。由于 $\theta \approx \frac{1}{\sqrt{N}}$，由此可推导出所需的迭代次数 $k \approx \frac{\pi}{4}\sqrt{N}$。因此，量子算法的时间复杂度骤降至 $O(\sqrt{N})$。
量子加速的根本来源并非简单的“并行计算”，而是量子态的**相干叠加**与**干涉效应**。经典概率计算中，概率总是非负的，只能通过累加进行穷举；而量子振幅是复数，Oracle的相位翻转使得目标态与非目标态产生相对相位差，随后的扩散算子则利用了类似多缝干涉的物理机制，发生相长干涉（放大目标振幅）和相消干涉（压缩非目标振幅），从而实现了比经典随机游走快指数级的收敛速度。

**isQ代码实现：**
下面是一个使用isQ语言实现的2量子比特振幅放大程序。在2比特情况下 $N=4$，初始角 $\theta = \arcsin(1/2) = \frac{\pi}{6}$，旋转一次角度增加 $\frac{\pi}{3}$，总角度为 $\frac{\pi}{2}$，因此只需1次迭代即可100%测得目标态 $|11\rangle$。

```isq
import std;

qbit q[2];

// 定义Oracle，目标态为 |11>
// 在计算基下，|11> 的相位翻转可通过 CZ 门实现
gate Oracle() {
    CZ(q[0], q[1]);
}

// 定义扩散算子
// 作用于 |psi> = H |00> 上，相当于对 |00> 进行相位翻转再 surrounded by H
gate Diffusion() {
    H(q[0]);
    H(q[1]);
    X(q[0]);
    X(q[1]);
    // 使用 CZ 门等效于对 |11> 翻转，配合前面的 X 门即实现对 |00> 的相位翻转
    CZ(q[0], q[1]);
    X(q[0]);
    X(q[1]);
    H(q[0]);
    H(q[1]);
}

procedure main() {
    // 步骤1：制备均匀叠加态
    H(q[0]);
    H(q[1]);
    
    // 步骤2：执行一次振幅放大迭代
    Oracle();
    Diffusion();
    
    // 步骤3：测量量子比特
    // 此时测量结果将100%为 11 (即十进制的3)
    int r0 = M(q[0]);
    int r1 = M(q[1]);
}
```

通过上述理论与代码的结合，我们可以清晰地看到振幅放大如何巧妙利用量子力学的波函数特性，突破了经典搜索算法的算力瓶颈。

## isqTrain/3062

- task_id: `isqTrain/3062`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `4885`

### Prompt

Implement a quantum circuit in isQ: initializes 3 qubits to the state |111> using X gates and measures all.

Requirements:
- Declare `qbit q[3];` at global scope.
- Apply X to qubits that should be |1>.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the 3-qubit state |111⟩ from the default |000⟩ and measure all qubits.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Start: |000⟩
   - X(q[0]): flips q[0] from |0⟩ to |1⟩ → |100⟩
   - X(q[1]): flips q[1] from |0⟩ to |1⟩ → |110⟩
   - X(q[2]): flips q[2] from |0⟩ to |1⟩ → |111⟩
4. **Expected probabilities**: The final state is the computational basis state |111⟩, so measurement yields |111⟩ with probability 1.0. In the output array (indexed by bitstring), index 7 (binary 111) equals 1.0.

## isqTrain/3723

- task_id: `isqTrain/3723`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `444`

### Prompt

Implement a quantum circuit in isQ: QAOA (p=1) for MaxCut on a 4-node square graph with edges [(0, 1), (1, 2), (2, 3), (0, 3)], gamma=0.785, beta=0.393. Use CNOT-Rz-CNOT for cost unitary and Rx for mixer.

### Chain-of-thought reasoning

Let me analyze this QAOA circuit for MaxCut on a 4-node square graph.

1. Goal: Implement QAOA (p=1) for MaxCut on a 4-node square graph with edges [(0,1), (1,2), (2,3), (0,3)], using gamma=0.785, beta=0.393.

2. Qubits: 4 qubits (q[0], q[1], q[2], q[3]), all measured.

3. Step-by-step evolution:

**Initial state:** |0000>

**Superposition (Hadamard on all):** 
H⊗4 |0000⟩ = 1/4 Σ_{x∈{0,1}^4} |x⟩ = |++++⟩

This creates an equal superposition over all 16 basis states.

**Cost unitary:**
For each edge (i,j), we apply: CNOT(i,j) · Rz(2γ, j) · CNOT(i,j)

This implements exp(-iγ Z_i Z_j) for each edge.

For the square graph with edges [(0,1), (1,2), (2,3), (0,3)]:
- The cost Hamiltonian is: C = Z_0Z_1 + Z_1Z_2 + Z_2Z_3 + Z_0Z_3

The cost unitary U_C(γ) = exp(-iγ C) = exp(-iγ(Z_0Z_1 + Z_1Z_2 + Z_2Z_3 + Z_0Z_3))

Since all terms commute (they're all Z-Z interactions), this can be decomposed as a product of individual terms.

For a computational basis state |x⟩ = |x_0 x_1 x_2 x_3⟩:
C|x⟩ = (Z_0Z_1 + Z_1Z_2 + Z_2Z_3 + Z_0Z_3)|x⟩ = C(x)|x⟩

where C(x) = (-1)^{x_0⊕x_1} + (-1)^{x_1⊕x_2} + (-1)^{x_2⊕x_3} + (-1)^{x_0⊕x_3}

For the MaxCut problem, C(x) counts the number of cut edges (edges where endpoints have different values).

**Mixer unitary:**
U_B(β) = exp(-iβ X⊗4) = Rx(2β)⊗4

This applies Rx(2×0.393) = Rx(0.786) to each qubit.

**Final state evolution:**
Starting from |ψ_0⟩ = |++++⟩

After cost unitary:
|ψ_1⟩ = U_C(γ)|ψ_0⟩ = 1/4 Σ_x exp(-iγ C(x))|x⟩

After mixer:
|ψ_f⟩ = U_B(β)|ψ_1⟩

The measurement probabilities are obtained from |⟨x|ψ_f⟩|².

Let me compute the predicted output for the output states:

For the MaxCut on a 4-node cycle:
- MaxCut solutions: |0101⟩, |1010⟩ (cut value 4)
- Other high cuts: |0011⟩, |0110⟩, |1001⟩, |1100⟩ (cut value 2)
- Low cuts: |0000⟩, |1111⟩ (cut value 0)
- Odd parity states like |0001⟩, etc. (cut value 1 or 3)

Wait, let me recalculate. For a square graph with edges [(0,1), (1,2), (2,3), (0,3)]:
- |0101⟩: cuts = {0-1: yes, 1-2: no, 2-3: yes, 0-3: no} = 2 cuts
- |1010⟩: cuts = {0-1: yes, 1-2: no, 2-3: yes, 0-3: no} = 2 cuts
- |0110⟩: cuts = {0-1: yes, 1-2: no, 2-3: no, 0-3: yes} = 2 cuts
- |1001⟩: cuts = {0-1: yes, 1-2: no, 2-3: no, 0-3: yes} = 2 cuts

Actually, the maximum cut for a 4-cycle is 4 (all edges cut), but that's impossible since we need exactly 2 nodes on each side.

Let me reconsider. For a bipartition (S, V\S) of a 4-cycle:

## isqTrain/104

- task_id: `isqTrain/104`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `409`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    // State to teleport: |1>
    X(q[0]);
    // EPR pair
    H(q[1]); CNOT(q[1], q[2]);
    // Alice's operations
    CNOT(q[0], q[1]);
    H(q[0]);
    // Bob's operations (using quantum control instead of classical)
    CNOT(q[1], q[2]);
    ctrl my_z(q[0], q[2]);
    
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Step 1: Understand the circuit.
qubits: q[0], q[1], q[2]. Initial state: |000>.
X(q[0]) -> |100>
H(q[1]) -> |1+0> = (1/sqrt(2))(|100> + |110>)
CNOT(q[1], q[2]) -> (1/sqrt(2))(|100> + |111>)  (EPR pair created)
CNOT(q[0], q[1]) -> (1/sqrt(2))(|100> + |011>)
Wait, |100> CNOT on q[0], q[1] becomes |110>. Wait, no.
Let's trace carefully:
Initial: |000>
X(q[0]): |100>
H(q[1]): 1/sqrt(2)(|100> + |110>)
CNOT(q[1], q[2]): 1/sqrt(2)(|100> + |111>)
CNOT(q[0], q[1]): 1/sqrt(2)(|110> + |011>)
H(q[0]):
Apply H to q[0].
|110> -> |+10> = 1/sqrt(2)(|010> + |110>)
|011> -> |-11> = 1/sqrt(2)(|011> - |111>)
Wait, |0> -> |+>, |1> -> |->
So |110> -> 1/sqrt(2)(|010> + |110>)
|011> -> 1/sqrt(2)(|011> - |111>)
Overall state before Bob's operations:
1/2 (|010> + |110> + |011> - |111>)
Bob's operations:
CNOT(q[1], q[2]):
If q[1] is 0, q[2] flips? No, CNOT(c, t) flips t if c=1.
So q[2] flips if q[1] is 1.
|010> -> |010>
|110> -> |111>
|011> -> |010>  Wait!
Let's check CNOT(q[1], q[2]) on the state 1/2 (|010> + |111> + |010> - |101>)
Wait, I need to re-evaluate CNOT(q[1], q[2]).
State is 1/2(|0, 1, 0> + |1, 1, 0> + |0, 1, 1> - |1, 1, 1>)
CNOT(q[1], q[2]) applies to q[1] (control), q[2] (target).
For each basis state:
|010>: control q[1]=1, target q[2]=0 -> flips q[2] -> |011>
|110>: control q[1]=1, target q[2]=0 -> flips q[2] -> |111>
|011>: control q[1]=1, target q[2]=1 -> flips q[2] -> |010>
|111>: control q[1]=1, target q[2]=1 -> flips q[2] -> |101>
So state becomes:
1/2 (|011> + |111> + |010> - |101>)
Next operation: ctrl my_z(q[0], q[2])
my_z applies Z to the target. Here it's controlled by q[0], and targets q[2].
Wait, `ctrl my_z(q[0], q[2]);` means q[0] is the control, and q[2] is the argument to my_z.
So if q[0] is 1, apply Z to q[2].
Z on |0> is |0>, Z on |1> is -|1>.
So if q[0]=1, flip the phase of |...1>.
In our state 1/2 (|011> + |111> + |010> - |101>)
States with q[0]=1 are |111> and |101>.
Apply CZ:
|111> -> -|111>
|101> -> -|101>
So state becomes:
1/2 (|011> - |111> + |010> + |101>)
Let's re-verify the predicted output.
The predicted output: {|001>: 0.25, |011>: 0.25, |101>: 0.25000000000000006, |111>: 0.25000000000000006}
Wait! My calculated state has |010> and |011>. But the expected has |001> and |101>.
Let me re-read the circuit.
"Bob's operations (using quantum control instead of classical)

### Reference answer

{'predicted_probs': {'1': 0.25, '3': 0.25, '5': 0.25000000000000006, '7': 0.25000000000000006}, 'explanation': 'Parametric variant of isqHumanEval/34. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3431

- task_id: `isqTrain/3431`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3785`

### Prompt

帮我写一个isQ程序：Grover's algorithm in isQ for 3 qubits, searching for |101>.

For 3 qubits (N=8), the optimal number of iterations is ~2.

Oracle for |101>: flip q[1] (the 0 bit) with X, apply doubly-controlled Z (ctrl ctrl Z), then flip q[1] back.

Diffusion: H-X on all, multi-controlled Z, X-H on all.
Multi-controlled Z on 3 qubits: ctrl ctrl Z(q[0], q[1], q[2]).

Perform 2 Grover iterations. Declare 3 qubits, measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Grover's search on 3 qubits to find marked state |101⟩, using 2 iterations (optimal for N=8).
Qubits: 3 global qubits q[0], q[1], q[2]; all measured at the end.

State evolution (initial |000⟩):
1. H(q[0,1,2]) → |+⟩⊗³ = (1/√8)Σ_x |x⟩, uniform superposition over all 8 basis states.
2. **Iteration 1 Oracle**: X(q[1]) flips the 0-bit in |101⟩, making target |111⟩; ctrl ctrl Z applies Z when all three are |1⟩ (phase flip on |111⟩); X(q[1]) restores. Result: |101⟩ → −|101⟩, others unchanged.
3. **Iteration 1 Diffusion**: H-X on all maps |s⟩ → |0⟩⊗³, ctrl ctrl Z flips |000⟩ phase, X-H restores. This reflects about the mean, amplifying |101⟩ amplitude. After iteration 1: amplitude of |101⟩ ≈ 0.75, others ≈ −0.125.
4. **Iteration 2**: Oracle re-flips |101⟩ phase; diffusion again reflects about mean, further amplifying |101⟩. After iteration 2: amplitude of |101⟩ ≈ 0.972, others ≈ 0.034.
5. M(q[0,1,2]) measures with P(|101⟩) ≈ 0.945, P(others) ≈ 0.0078 each.

The two Grover iterations optimally rotate the state vector toward |101⟩, yielding ~94.5% success probability.

## isqTrain/3662

- task_id: `isqTrain/3662`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `2294`

### Prompt

Write an isQ program that 3-bit quantum phase estimation for phase angle 5*pi/4 (in multiples of 2π/8). Use 3 precision qubits, controlled-Rz rotations, and a 3-qubit inverse QFT. Measure all 4 qubits (3 precision + 1 eigenstate).

### Chain-of-thought reasoning

Let me analyze this quantum phase estimation circuit step by step.

The goal is to implement 3-bit quantum phase estimation for a phase angle of 5π/4, which in multiples of 2π/8 equals 5.

We have 4 qubits:
- q[0], q[1], q[2]: precision qubits (3 bits)
- q[3]: eigenstate qubit

Step 1: Initialize eigenstate
- Start with |0000⟩
- X(q[3]) → |0001⟩ (the eigenstate qubit is prepared in |1⟩)

Step 2: Hadamard on precision qubits
- H(q[0]), H(q[1]), H(q[2]) → |+⟩|+⟩|+⟩|1⟩ = (1/√8)Σ|x⟩|1⟩ for x ∈ {0,1,2,3,4,5,6,7}

Step 3: Controlled-U^(2^k) operations
The unitary U is Rz(2π × 5/8) which applies phase e^(i×5π/4) to |1⟩ state.

When applied controlled by q[0] (2^0 = 1):
- ctrl Rz(2π × 5/8 × 1, q[0], q[3])
- This applies phase e^(i×5π/4) to |1⟩_0|1⟩_3

When applied controlled by q[1] (2^1 = 2):
- ctrl Rz(2π × 5/8 × 2, q[1], q[3])
- This applies phase e^(i×5π/2) to |1⟩_1|1⟩_3

When applied controlled by q[2] (2^2 = 4):
- ctrl Rz(2π × 5/8 × 4, q[2], q[3])
- This applies phase e^(i×5π) = e^(iπ) = -1 to |1⟩_2|1⟩_3

After these operations, the state becomes:
(1/√8) Σ|x⟩|1⟩ × e^(2πi × 5x/8)

This is because each precision qubit contributes a phase factor based on its bit value.

Let me denote the phase angle as φ = 5π/4 = 5/8 × 2π.

The state after controlled operations is:
(1/√8) Σ_{x=0}^{7} e^(2πi × 5x/8)|x⟩|1⟩

Step 4: Inverse QFT on precision qubits

The inverse QFT transforms:
(1/√8) Σ_x e^(2πiφx/8)|x⟩ → |φ̃⟩

For φ = 5/8, the ideal result would be |5⟩ = |101⟩.

However, 5 in binary is 101, so we should measure 101 on the precision qubits.

Wait, let me reconsider the predicted output given: {|0011>: 0.25, |0101>: 0.125, |0111>: 0.125, |1101>: 0.426777, |1111>: 0.073223}

The bitstring is indexed with earlier measured qubit = higher bit. So if we measure q[0], q[1], q[2], q[3] in that order:
- |0011⟩ means q[0]=0, q[1]=0, q[2]=1, q[3]=1
- |0101⟩ means q[0]=0, q[1]=1, q[2]=0, q[3]=1
- |1101⟩ means q[0]=1, q[1]=1, q[2]=0, q[3]=1
- |1111⟩ means q[0]=1, q[1]=1, q[2]=1, q[3]=1

q[3] should always be 1 (the eigenstate).

For the precision qubits, the predicted output from iQFT should give us |101⟩ (binary for 5).

But wait, in QPE the qubits are ordered differently. Let me think about this more carefully.

Actually, in the standard QPE:
- q[0] is the least significant precision qubit (2^0)
- q[2] is the most significant precision qubit (2^2)

After iQFT, the state should be approximately |5⟩ where:
- q[0] (2^0) = 1
- q[1] (2^1) = 0
- q[2] (2^2)

## isqTrain/3616

- task_id: `isqTrain/3616`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `5446`

### Prompt

帮我写一个isQ程序：a 3-qubit Grover search for target state |111> using 2 Grover iterations for higher amplification. The circuit:
1. Initialize 3 qubits in superposition
2. Apply oracle+diffusion twice
3. Measure all qubits
Use `deriving gate` for oracle and diffusion procedures.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement 3-qubit Grover search targeting |111⟩ with 2 iterations for amplified success probability.
Three qubits are used, all measured at the end.
State evolution: |000⟩ → H⊗³ → (1/√8)Σ|x⟩ (equal superposition). Oracle applies ctrl CZ, flipping phase of |111⟩. Diffusion (H⊗³ → X⊗³ → ctrl CZ → X⊗³ → H⊗³) reflects amplitudes about the mean.
After iteration 1: |111⟩ amplitude grows to ~0.97, others shrink to ~-0.097. After iteration 2: amplitude of |111⟩ reaches sin²(5θ/2) where θ = 2arcsin(1/√8), giving probability 0.9453.
Expected: |111⟩ ≈ 94.5%, all others ≈ 0.78% each.

## isqTrain/19

- task_id: `isqTrain/19`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4795`

### Prompt

Write isQ code for the following quantum task: implements the qft_subcircuit pattern with modified rotation parameters (pi4_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit implements a modified QFT (Quantum Fourier Transform) on 3 qubits with rotation parameters adjusted from pi/4 to pi/3.

Initial state: |000⟩ (all qubits in |0⟩)

1. After X(q[2]): |100⟩ (binary order: q[0] is rightmost bit, but actually in isQ, q[0] is the first qubit)

Wait, let me be careful about the bit ordering. In isQ, when we measure q[0], q[1], q[2], the measurement result is interpreted as q[0] being the highest bit (most significant).

Actually, looking at the measurement probabilities, they are indexed by measurement bitstring where "earlier measured qubit = higher bit". So if we measure q[0] first, it's the highest bit.

So the state |q[0], q[1], q[2]⟩ where q[0] is the MSB.

Initial state: |000⟩
After X(q[2]): |001⟩ (q[2] flipped)

Now qft3(q[0], q[1], q[2]) is called where a=q[0], b=q[1], c=q[2].

Starting state: |001⟩ (which is |q[0]=0, q[1]=0, q[2]=1⟩)

Step 1: H(a) = H(q[0])
|001⟩ → (|0⟩+|1⟩)/√2 ⊗ |01⟩ = (|001⟩ + |101⟩)/√2

Step 2: ctrl Rz(pi/2.0, b, a) = controlled-Rz with control b=q[1], target a=q[0]
Since q[1] = |0⟩, this does nothing to a.
State: (|001⟩ + |101⟩)/√2

Wait, that's wrong. Let me reconsider. In isQ, `ctrl Rz(theta, control, target)` applies Rz(theta) to target when control is |1⟩.

So `ctrl Rz(pi/2.0, b, a)` means: if b=q[1] is |1⟩, apply Rz(pi/2) to a=q[0].

Since q[1] is |0⟩ in both |001⟩ and |101⟩, nothing happens.

State: (|001⟩ + |101⟩)/√2

Step 3: ctrl Rz(pi/3.0, c, a) = if c=q[2] is |1⟩, apply Rz(pi/3) to a=q[0].
In |001⟩ and |101⟩, q[2]=1, so we apply Rz(pi/3) to q[0].

Rz(pi/3) |0⟩ = e^{-iπ/6}|0⟩ = e^{-iπ/6}|0⟩
Rz(pi/3) |1⟩ = e^{iπ/6}|1⟩

State: (e^{-iπ/6}|001⟩ + e^{iπ/6}|101⟩)/√2

Step 4: H(b) = H(q[1])
H|0⟩ = (|0⟩+|1⟩)/√2
State: (e^{-iπ/6}(|001⟩+|011⟩) + e^{iπ/6}(|101⟩+|111⟩))/2

Step 5: ctrl Rz(pi/2.0, c, b) = if c=q[2] is |1⟩, apply Rz(pi/2) to b=q[1].
In all terms, q[2]=1, so apply Rz(pi/2) to q[1].

Rz(pi/2)|0⟩ = e^{-iπ/4}|0⟩
Rz(pi/2)|1⟩ = e^{iπ/4}|1⟩

State: (e^{-iπ/6}(e^{-iπ/4}|001⟩+e^{iπ/4}|011⟩) + e^{iπ/6}(e^{-iπ/4}|101⟩+e^{iπ/4}|111⟩))/2
= (e^{-i(π/6+π/4)}|001⟩ + e^{-iπ/6+iπ/4}|011⟩ + e^{iπ/6-iπ/4}|101⟩ + e^{i(π/6+π/4)}|111⟩)/2
= (e^{-i5π/12}|001⟩ + e^{iπ/12}|011⟩ + e^{-iπ/12}|101⟩ + e^{i5π/12}|111⟩)/2

Step 6: H(c) = H(q[

# ISQ training COT RAG corpus: quantum_algorithms shard 111

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4088

- task_id: `isqTrain/4088`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3075`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[3];

unit grover_oracle(qbit q[3]) {
    ctrl CZ(q[0], q[1], q[2]);
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
    grover_oracle(q);
    grover_diffusion(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement output of an isQ circuit.
    *   Format: "## Circuit Analysis", 3-8 lines for simple circuits, up to 15 for complex ones. Use Dirac notation.
    *   Specific circuit: Grover's algorithm with 2 iterations on 3 qubits.
    *   Target: The marked state for the Grover oracle.

2.  **Analyze the Circuit:**
    *   3 qubits, $N=8$ states.
    *   Initial state: $|000\rangle$.
    *   Hadamards on all qubits: $|+\rangle^{\otimes 3} = \frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle$.
    *   Oracle (`ctrl CZ(q[0], q[1], q[2])`): Applies Z to all three qubits controlled on all three being in $|1\rangle$. Wait, `ctrl CZ(q[0], q[1], q[2])` in isQ means... ah, `CZ` takes 2 arguments normally. Let's look at `ctrl CZ(q[0], q[1], q[2])`. Actually, wait. A CZ gate normally takes 2 qubits. If written as `ctrl CZ(q[0], q[1], q[2])`, it means a controlled-CZ, i.e., a Toffoli-like gate but doing Z instead of X, or perhaps a multi-controlled Z. Actually, a multi-controlled Z on $n$ qubits flips the phase of the $|1...1\rangle$ state. Here, it's `ctrl CZ(q[0], q[1], q[2])`, which means if $q_0=1$ and $q_1=1$, apply CZ to $q_2$? Wait, CZ is symmetric. If $q_2=1$ and $q_0=1, q_1=1$, the whole state is $|111\rangle$ and its phase is flipped. So the oracle marks the state $|111\rangle$. Let's double check standard isQ `ctrl` syntax. `ctrl CZ(q[0], q[1], q[2])` means $q_0, q_1$ are controls for a CZ on $q_2$? No, `CZ` is a 2-qubit gate. Standard double-controlled-Z (ctrl @[c1, c2] Z(target))? Yes, `ctrl CZ` on 3 qubits is a Controlled-Controlled-Z gate. This applies a Z to the 2-qubit subspace? No, Z acts on one qubit. CZ applies Z to one qubit. double-controlled-Z (ctrl @[c1, c2] Z(target)) applies Z to the target qubit. Since Z on $|1\rangle$ gives $-|1\rangle$ and Z on $|0\rangle$ gives $|0\rangle$, applying Z to a qubit when controls are $|1\rangle$ effectively flips the sign of the $|1...1\rangle$ state.
    *   Therefore, the marked state is $|111\rangle$.
    *   Let's check the optimal number of iterations for $N=8$. Optimal iterations $k \approx \frac{\pi}{4} \sqrt{N/2} = \frac{\pi}{4} \sqrt{4} = \frac{\pi}{2} \approx 1.57$.
    *   The circuit applies 2 iterations (`grover_oracle` then `grover_diffusion` twice).
    *   Wait, is it exactly $|111\rangle$? Let's trace carefully.
    *   Wait, Grover diffusion for $|111\rangle$ using double-controlled-Z (ctrl @[c1, c2] Z(target)) works by flipping the phase of $|000\rangle$, which is equivalent to the standard diffusion operator $H^{\otimes n} (2|0\rangle\langle0| - I) H^{\otimes n}$.
    *   With $k=2$ iterations on $N=8$, the angle $\theta = \arcsin(1/\sqrt{8}) \approx 20.7^\circ$. $2\theta \approx 41.4^\circ$.
    *   Initial amplitude of $|111\rangle$ is $\sin(\theta) \approx 0.3535$.
    *   After 1 iteration: $\sin(2\theta) \approx \sin(41.4^\circ) \approx 0.661$.
    *   After 2 iterations: $\sin(3\theta) \approx \sin(62.1^\circ) \approx 0.884$.
    *   Wait, $k=2$ iterations might not peak exactly, but $|111\r

### Reference answer

Deterministic output: state |111> with probability ~0.95

## isqQA/quantum_algorithms/86_comparison

- task_id: `isqQA/quantum_algorithms/86_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `comparison`, `algorithm`, `Deutsch算法原理`
- source: `qa_pipeline`
- dataset_index: `3577`

### Prompt

在量子计算中，Deutsch算法被公认为是展示量子并行性的最基础例子。请对比分析Deutsch算法与经典计算方法在判断单比特函数是否为常数函数时的查询复杂度和计算过程。并探讨这种量子算法的优缺点及其在实际问题中的适用场景。

### Reference answer

<think
首先分析经典计算方法的推导过程：给定一个未知的黑盒函数 $f: \{0,1\} \to \{0,1\}$，经典算法需要分别查询 $f(0)$ 和 $f(1)$ 的值，即进行2次查询。然后判断 $f(0) \oplus f(1)$，若结果为0则是常数函数，为1则是平衡函数。因此经典确定性查询复杂度为 $O(2)$。

接着分析量子Deutsch算法的推导：准备两个量子比特，初态为 $|01\rangle$。对两个比特分别施加Hadamard门，状态演变为 $|+\rangle |-\rangle = \frac{1}{2}(|0\rangle + |1\rangle)(|0\rangle - |1\rangle)$。将该叠加态输入量子黑盒 $U_f$，其作用为 $U_f|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle$。由于第二比特处于 $|0\rangle - |1\rangle$ 的态，根据相位反冲效应，第一比特会获得 $(-1)^{f(x)}$ 的相位。此时状态变为 $\frac{1}{\sqrt{2}}((-1)^{f(0)}|0\rangle + (-1)^{f(1)}|1\rangle) \otimes | -\rangle$。提取前面的系数，第一比特的状态可以重写为 $\pm \frac{1}{\sqrt{2}}(|0\rangle + (-1)^{f(0) \oplus f(1)}|1\rangle)$。最后对第一比特再次施加Hadamard门。如果 $f(0) \oplus f(1) = 0$（常数函数），态变为 $|0\rangle$；如果为1（平衡函数），态变为 $|1\rangle$。因此，只需测量第一比特即可得出结论，整个过程中量子黑盒仅被调用了1次，查询复杂度降为 $O(1)$。

下面编写isQ代码来验证这一过程，假设黑盒函数为常数函数 $f(x)=1$：}

在评估未知黑盒函数 $f: \{0,1\} \to \{0,1\}$ 是否为常数函数（即 $f(0)=f(1)$）或平衡函数（即 $f(0) \neq f(1)$）时，经典计算与量子计算展现出了截然不同的查询机制。

**经典计算方法的局限**
在经典计算模型中，一个确定性的算法必须分别计算 $f(0)$ 和 $f(1)$ 的具体数值。第一次查询得出 $f(0)$，第二次查询得出 $f(1)$，然后通过异或操作 $f(0) \oplus f(1)$ 来得出结论。这意味着经典确定性算法的查询复杂度为 $O(2)$。由于经典比特在同一时刻只能处于单一状态（0或1），它无法在单次操作中同时探测函数的两个输入，这构成了经典信息处理的根本瓶颈。

**量子Deutsch算法的突破**
Deutsch算法巧妙地利用了量子叠加和干涉效应。通过将输入量子比特制备为 $|0\rangle$ 和 $|1\rangle$ 的叠加态（$|+\rangle$），量子计算机能够在单次查询中同时将两个输入传递给黑盒。借助于量子黑盒的相位反冲特性，函数的结果被编码为相对相位，随后通过Hadamard门的干涉作用，将相位差转化为可测量的概率幅差异。最终，只需1次黑盒查询并测量即可得出结论。

以下是使用isQ语言实现的Deutsch算法代码示例，这里我们假设黑盒函数是一个常数函数 $f(x)=1$：

```isq
import std;

qbit q[2];

procedure main() {
    // 初始化第一比特为|0>，第二比特为|1>
    X(q[1]);
    
    // 施加Hadamard门创建叠加态
    for i in 0:2 {
        H(q[i]);
    }
    
    // 模拟黑盒操作 U_f，对于常数函数 f(x)=1
    // 此时作用相当于对第二比特施加 X 门
    X(q[1]);
    
    // 再次对第一比特施加Hadamard门产生干涉
    H(q[0]);
    
    // 测量第一比特
    // 对于 f(x)=1 (常数函数)，测量结果理论上必然为 0
    int r = M(q[0]);
    if (r == 0) {
        // 判定为常数函数
    }
}
```

**优缺点与适用场景对比**
Deutsch算法的优点在于它从理论上首次证明了量子计算可以在特定问题上实现相对于经典计算的指数级加速（从2次查询降为1次）。这打破了计算复杂度的经典下界。

然而，它的缺点也十分明显：适用场景极度受限。Deutsch算法只能处理输入长度 $n=1$ 的布尔函数，而在现实世界中，我们需要评估的通常是 $n$ 很大时的函数。因此，Deutsch算法在实际工程应用中几乎没有直接的用武之地，它的价值纯粹在于**理论启蒙和教学演示**，为后续解决更复杂问题（如多比特的Deutsch-Jozsa算法、Grover搜索算法）奠定了量子并行性与干涉设计的核心思想基础。

## isqTrain/3443

- task_id: `isqTrain/3443`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `hamiltonian_simulation`
- source: `isq_train_cot`
- dataset_index: `3532`

### Prompt

I need an isQ program to single-layer QAOA for MaxCut on a triangle (3 nodes, 3 edges) in isQ.

Edges: (0,1), (0,2), (1,2). Use gamma=0.5, beta=0.4.

For each edge, apply the ZZ interaction:
  CNOT(qi, qj), Rz(gamma, qj), CNOT(qi, qj)

Then the mixer: Rx(2*beta) on each qubit.
Declare 3 qubits, measure all.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a single-layer QAOA for MaxCut on a triangle graph.

Let me trace through the circuit:

1. Initialize 3 qubits to |000⟩
2. Apply H to all: creates |+++⟩ = equal superposition of all 8 states
3. Problem unitary (ZZ interactions with γ=0.5):
   - For each edge (i,j), apply CNOT(i,j) Rz(γ,j) CNOT(i,j), which implements exp(-iγZ_i Z_j/2) or equivalently applies a phase based on ZZ

Actually, let me think more carefully. The CNOT-Rz-CNOT sequence applies a controlled-Z-rotation, which gives exp(-iγ/2) when the two qubits have different values (|01⟩ or |10⟩).

Wait, let me reconsider. CNOT(i,j) Rz(γ,j) CNOT(i,j):
- When control is |0⟩, target is unchanged by CNOT, so Rz acts normally
- When control is |1⟩, target is flipped, Rz acts on flipped state, then flipped back

The net effect is: this implements a ZZ rotation, specifically exp(-iγ Z_i⊗Z_j / 2) up to a global phase.

For MaxCut, the cost Hamiltonian is H_C = Σ_{(i,j)} (I - Z_i Z_j)/2, so edges crossing the cut contribute +1. The phase unitary applies exp(-iγ H_C), which gives different phases to different computational basis states.

Let me trace the state evolution more carefully.

After H gates: |ψ₁⟩ = |+++⟩

The ZZ interaction for edge (i,j) with parameter γ applies:
- Phase factor based on Z_i Z_j eigenvalue
- When Z_i Z_j = +1 (same partition): factor e^{-iγ}
- When Z_i Z_j = -1 (different partition): factor e^{iγ}

Wait, I need to be more careful. The CNOT-Rz-CNOT sequence:
CNOT → Rz(γ) → CNOT

Rz(γ) = [[e^{-iγ/2}, 0], [0, e^{iγ/2}]]

Let me work out what this does to |00⟩, |01⟩, |10⟩, |11⟩:

|00⟩ → CNOT → |00⟩ → Rz(γ) on target → e^{-iγ/2}|00⟩ → CNOT → e^{-iγ/2}|00⟩
|01⟩ → CNOT → |01⟩ → Rz(γ) on target → e^{iγ/2}|01⟩ → CNOT → e^{iγ/2}|01⟩
|10⟩ → CNOT → |11⟩ → Rz(γ) on target → e^{iγ/2}|11⟩ → CNOT → e^{iγ/2}|10⟩
|11⟩ → CNOT → |10⟩ → Rz(γ) on target → e^{-iγ/2}|10⟩ → CNOT → e^{-iγ/2}|11⟩

So the phases are:
- |00⟩: e^{-iγ/2}
- |01⟩: e^{iγ/2}
- |10⟩: e^{iγ/2}
- |11⟩: e^{-iγ/2}

This is indeed a ZZ interaction: e^{-iγ/2} when Z⊗Z = +1, e^{iγ/2} when Z⊗Z = -1.

So the phase is e^{-iγ·Z_iZ_j/2}.

For the QAOA, the cost Hamiltonian is C = Σ_{edges} (1 - Z_iZ_j)/2, and we apply e^{-iγC}.

But actually, the CNOT-Rz-CNOT applies exp(-iγ Z_iZ_j/2), not exp(-iγ (1-Z_iZ_j)/2).

Let me just compute numerically. With γ = 0.5:

After the problem unitary on all three edges, each basis state picks up a phase based on how many edges have different values.

For state |abc⟩ where a, b, c ∈ {0, 1}:
- Edge (0,1) contributes: if a⊕b = 0 (same), phase e^{-iγ/2}; if a⊕b = 1 (different), phase e^{iγ/2}
- Edge (0,2) contributes: if a⊕c = 0, phase e^{-iγ/2}; if a⊕c = 1, phase e^{iγ/2}
- Edge (1,2) contributes: if b⊕c = 0, phase e^{-iγ/2}; if b⊕c

## isqTrain/3525

- task_id: `isqTrain/3525`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1166`

### Prompt

What does this isQ program output when measured?

```
import std;

qbit q[2];

procedure main() {
    H(q[0]); H(q[1]);

    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);

    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Role: Quantum computing expert.
    *   Task: Predict output probability distribution of an isQ program.
    *   Format: Concise, precise step-by-step reasoning using Dirac notation.
    *   Length: 3-8 lines (simple) to 15 lines (complex).
    *   Start with "## Circuit Analysis", no code blocks, end with predicted distribution.

2.  **Analyze the isQ Program:**
    *   2 qubits: `q[0]`, `q[1]`. Initial state $|00\rangle$.
    *   Block 1: `H(q[0]); H(q[1])` -> Apply $H \otimes H$.
    *   Block 2: `X(q[0]); X(q[1]); CZ(q[0], q[1]); X(q[0]); X(q[1])` -> This is $X \otimes X \cdot CZ \cdot X \otimes X$. Notice that $XZX = -Z$. For CZ, applying $X$ on both sides effectively applies $CZ$ but with a phase change or applies $XZX$ logic. Wait, let's trace it exactly.
        *   $CZ = |0\rangle\langle0| \otimes I + |1\rangle\langle1| \otimes Z$.
        *   $X \otimes X \cdot CZ \cdot X \otimes X = X \otimes X (|0\rangle\langle0| \otimes I + |1\rangle\langle1| \otimes Z) X \otimes X$.
        *   $X |0\rangle\langle0| X = |1\rangle\langle1|$, $X |1\rangle\langle1| X = |0\rangle\langle0|$.
        *   So $X \otimes X \cdot CZ \cdot X \otimes X = |1\rangle\langle1| \otimes X I X + |0\rangle\langle0| \otimes X Z X$.
        *   $X I X = I$, $X Z X = -Z$.
        *   Result: $|1\rangle\langle1| \otimes I - |0\rangle\langle0| \otimes Z$. This is actually $CZ$ with an extra $Z$ phase? No, let's just compute the state directly.

3.  **State Evolution Step-by-Step:**
    *   Initial: $|00\rangle$
    *   After $H \otimes H$: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) = |++\rangle$.
    *   Apply `X(q[0]); X(q[1])`: $\frac{1}{2}(|11\rangle + |10\rangle + |01\rangle + |00\rangle) = |++\rangle$. (State doesn't change in terms of superposition amplitudes).
    *   Apply `CZ(q[0], q[1])`: Flips phase of $|11\rangle$.
        *   State: $\frac{1}{2}(|11\rangle - |10\rangle - |01\rangle + |00\rangle)$.
    *   Apply `X(q[0]); X(q[1])`: Swaps amplitudes back.
        *   $|11\rangle \leftrightarrow |00\rangle$
        *   $|10\rangle \leftrightarrow |01\rangle$
        *   State: $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$. Notice this is $|--\rangle$ up to a global phase? Wait.
        *   Let's check $|--\rangle = (|0\rangle - |1\rangle)/\sqrt{2} \otimes (|0\rangle - |1\rangle)/\sqrt{2} = \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$. Yes! The state is $|--\rangle$.
        *   Wait, is it just an $H$ gate? $H |0\rangle = |+\rangle$, $H |1\rangle = |-\rangle$.
        *   Notice that $X \otimes X \cdot CZ \cdot X \otimes X |++\rangle = |--\rangle$?
        *   Wait, $H_{2} (X \otimes X \cdot CZ \cdot X \otimes X) H_{2} |00\rangle$.
        *   Let's re-evaluate:

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'The output is |00> with probability 1.0'}

## isqTrain/812

- task_id: `isqTrain/812`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2794`

### Prompt

Write isQ code for the following quantum task: implements the quadratic_form pattern. Include explicit identity operations in the circuit (H-H pair before M(q[1])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement a 1-bit quadratic form f(x) = x² mod 2 = x, with an H-H identity pair to demonstrate gate cancellation.

**Qubits:** 2 qubits (q[0] for input x, q[1] for result); only q[1] is measured.

**State evolution:**
1. |00⟩ → H(q[0]) → (|00⟩ + |10⟩)/√2
2. CNOT(q[0], q[1]) → (|00⟩ + |11⟩)/√2 (copies x to result since x² = x mod 2)
3. H(q[1]) → (|00⟩ + |01⟩ - |10⟩ + |11⟩)/2
4. H(q[1]) → (|00⟩ + |11⟩)/√2 (H² = I, gate cancellation restores previous state)
5. M(q[1]) → measure q[1]

**Expected probabilities:** From (|00⟩ + |11⟩)/√2, measuring q[1] yields |0⟩ with prob 0.5 and |1⟩ with prob 0.5.

## isqTrain/3802

- task_id: `isqTrain/3802`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `5546`

### Prompt

用isQ实现4-bit Bernstein-Vazirani to find secret s=0101. Use oracle keyword, for loops for Hadamard. Measure all 5 qubits.

### Chain-of-thought reasoning

Step 1: Understand the Goal
The task is to generate a concise reasoning section for a 4-bit Bernstein-Vazirani quantum circuit in isQ, targeting the secret string $s = 0101$. The circuit uses an oracle, Hadamard gates via for loops, and measures 5 qubits.

Step 2: Identify the Circuit Components
- **Qubits**: 5 qubits total. $q[0]$ to $q[3]$ are input qubits, $q[4]$ is the output/ancilla qubit.
- **Initialization**:
  - Inputs ($q[0]$ to $q[3]$) start in $|0\rangle$.
  - Output ($q[4]$) is initialized to $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$ using $X$ and $H$.
- **Superposition**: Apply $H$ to $q[0]$ through $q[3]$. Wait, the prompt says "for i in 0:4 { H(q[i]); }", which applies $H$ to $q[0], q[1], q[2], q[3]$.
- **Oracle**: `oracle f(4, 1) = [0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0];`
  - This oracle encodes $f(x) = x \cdot s \pmod 2$ where $s = 0101$.
  - The oracle acts as $|x\rangle|y\rangle \to |x\rangle|y \oplus f(x)\rangle$.
- **Interference**: Apply $H$ to $q[0]$ through $q[3]$ again.
- **Measurement**: Measure all 5 qubits.

Step 3: Trace the Quantum State Evolution
1. **Initial state**: $|00000\rangle$.
2. **Prepare ancilla**:
   - $X(q[4])$ flips the 5th qubit: $|00001\rangle$.
   - $H(q[4])$ puts it in $|-\rangle$: $|0000\rangle \otimes |-\rangle$.
3. **Hadamard on inputs**:
   - `for i in 0:4 { H(q[i]); }` applies $H$ to the first 4 qubits.
   - State becomes $\frac{1}{4} \sum_{x \in \{0,1\}^4} |x\rangle \otimes |-\rangle$.
4. **Apply Oracle**:
   - The oracle computes $f(x) = x \cdot s$ into the phase because $|-\rangle \xrightarrow{\text{Z}} (-1)|-\rangle$ if $f(x)=1$.
   - State becomes $\frac{1}{4} \sum_{x} (-1)^{x \cdot s} |x\rangle \otimes |-\rangle$.
5. **Hadamard on inputs**:
   - Applying $H^{\otimes 4}$ on the input qubits maps the state $\sum_x (-1)^{x \cdot s} |x\rangle$ to $|s\rangle$.
   - State is $|0101\rangle \otimes |-\rangle$.
6. **Measurement**:
   - Measuring all 5 qubits collapses $|0101\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
   - Input qubits ($q[0]$ to $q[3]$) deterministically yield `0101` (in the order of measurement $q[0], q[1], q[2], q[3]$). Note: In isQ bitstring mapping, $q[0]$ is usually the most significant bit or vice versa depending on convention. Let's stick to standard notation.
   - Output qubit ($q[4]$) is in $|-\rangle$, yielding 0 with 50% probability and 1 with 50% probability.
   - Expected probabilities: $|01010\rangle: 0.5$, $|01011\rangle: 0.5$. (assuming $q[0]$ is MSB and $q[4]$ is LSB).

Step 4: Format the Output
- Start with "## Reasoning".
- Goal: Find 4-bit secret string $s=0101$ using Bernstein-Vazirani with 5 qubits.
- Evolution steps:
  1. Start at $|00000\rangle$; $X, H$ on $q[4]$ yields $

## isqQA/quantum_algorithms/108_principle_advantage

- task_id: `isqQA/quantum_algorithms/108_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `量子相位估计QPE原理`
- source: `qa_pipeline`
- dataset_index: `2433`

### Prompt

请详细解释量子相位估计（QPE）算法的宏观原理，并将其与经典傅里叶变换的时间复杂度进行对比，深入剖析其实现指数级量子加速的核心物理机制。此外，请使用isQ语言编写一段代码，演示如何估计酉算子S门作用于其本征态时的本征相位。

### Reference answer

宏观原理：
量子相位估计（Quantum Phase Estimation, QPE）算法的核心目标是寻找一个已知酉算子 $U$ 的本征值相位。假设 $U$ 作用在其本征态 $|\psi\rangle$ 上满足 $U|\psi\rangle = e^{2\pi i \phi}|\psi\rangle$，其中 $0 \le \phi < 1$ 为未知的相位。QPE通过两个寄存器来实现：第一个是包含 $n$ 个量子比特的控制寄存器（初始化为 $|0\rangle^{\otimes n}$），第二个是包含本征态 $|\psi\rangle$ 的目标寄存器。
算法主要分三步：
1. 对控制寄存器中的所有量子比特施加Hadamard门，使其进入等权叠加态。
2. 依次以控制寄存器中的第 $k$ 个量子比特为控制位，对目标寄存器施加受控酉算子 $U^{2^k}$。由于量子并行性，这一步在态空间中完成了相位信息的编码，控制寄存器的状态变为 $\frac{1}{2^{n/2}} \sum_{k=0}^{2^n-1} e^{2\pi i \phi k} |k\rangle$。
3. 对控制寄存器施加逆量子傅里叶变换（IQFT），将叠加态中包含的相位信息转化为可测量的二进制整数态。最后通过测量控制寄存器，即可高概率获得相位 $\phi$ 的 $n$ 位二进制估计。

时间复杂度对比与量子加速来源：
在经典计算中，如果我们想要提取一个 $2^n \times 2^n$ 矩阵的特征值（或相位），需要构造 $2^n$ 维的向量并进行快速傅里叶变换（FFT），其时间复杂度为 $O(N \log N)$，其中 $N = 2^n$，即复杂度为 $O(n 2^n)$。而在量子QPE算法中，由于量子态的天然张量积结构，$n$ 个量子比特即可表示 $2^n$ 维的向量。算法主要消耗在于 $n$ 个受控酉门 $U^{2^k}$ 的调用以及 $O(n^2)$ 数量的量子门来实现逆量子傅里叶变换。如果视 $U$ 的调用复杂度为 $O(1)$，则整体时间复杂度仅为 $O(n^2)$。
其指数级加速的核心来源主要有两点：
1. 量子叠加与演化并行性：在受控酉门操作阶段，$2^n$ 个不同幂次的 $U$ 被同时作用于量子态上，只需 $n$ 次物理操作即可完成对庞大希尔伯特空间的遍历。
2. 量子干涉机制：逆量子傅里叶变换利用了量子干涉效应，将隐藏在相对相位（特征值）中的代数信息精准地转化为计算基态上的概率幅分布，从而以极高的概率直接提取出结果，避免了经典算法中高昂的采样和搜索开销。

以下是一个用isQ语言编写的代码示例，用于估计S门（$S|1\rangle = e^{i\pi/2}|1\rangle$）作用于本征态 $|1\rangle$ 时的相位。已知相位 $\phi = 1/4 = 0.01_2$，使用2个量子比特进行估计，预期测量结果将为二进制01。

```isQ
import std;

qbit q[2]; // 控制寄存器，用于相位估计
qbit e[1]; // 目标寄存器，存储本征态

procedure main() {
    // 初始化目标寄存器为本征态 |1>
    X(e[0]);

    // 对控制寄存器施加Hadamard门，生成叠加态
    for i in 0:2 {
        H(q[i]);
    }

    // 依次施加受控U门
    // q[0] 控制 U^(2^0) = S^1
    ctrl @[q[0]] S(e[0]);
    // q[1] 控制 U^(2^1) = S^2 = Z
    ctrl @[q[1]] Z(e[0]);

    // 施加逆量子傅里叶变换 (IQFT)
    H(q[0]);
    // 受控相位旋转的逆操作，相当于逆受控S门
    inv ctrl @[q[1]] S(q[0]);
    H(q[1]);

    // 测量控制寄存器，预期输出为 q[1]=0, q[0]=1 (即二进制01)
    for i in 0:2 {
        M(q[i]);
    }
}
```

## isqTrain/1106

- task_id: `isqTrain/1106`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1327`

### Prompt

Write isQ code for the following quantum task: implements a variant of the simon_algorithm pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The implementation is for Simon's algorithm with period s=11 (binary). Let me analyze the circuit:

1. The circuit has input qubits q[0], q[1] and output qubits out[0], out[1], plus q[2] which is not operated on
2. H gates create superposition on q[0], q[1]
3. Oracle f maps inputs to outputs based on x[0] XOR x[1]
4. Hadamard on input qubits again
5. Measure all 3 qubits (q[0], q[1], q[2])

Wait, but the prompt says "q[2] -> q[3]" which suggests a 4-qubit register. Let me re-read.

The prompt says "implements a variant of the simon_algorithm pattern using q[2] -> q[3]" and "The circuit should use an expanded qubit register compared to the base version."

But The circuit should q[3] (indices 0,1,2) and out[2]. The measurement probabilities are {|000>: 0.5, |110>: 0.5}.

Let me trace through:
1. Initial state: |0000⟩ (q[0], q[1], q[2], out[0], out[1])
   Actually it's |00000⟩ for q[0], q[1], q[2], out[0], out[1]

2. After H(q[0]), H(q[1]): (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 ⊗ |0⟩ ⊗ |00⟩ on (q[0],q[1], q[2], out)

3. After oracle f: The oracle computes f(x) into out register
   f(00)=00, f(01)=01, f(10)=01, f(11)=00
   So: (|00⟩|00⟩ + |01⟩|01⟩ + |10⟩|01⟩ + |11⟩|00⟩)/2 ⊗ |0⟩

4. After H(q[0]), H(q[1]) on input register:
   H⊗2 on |00⟩ gives (|00⟩+|01⟩+|10⟩+|11⟩)/2
   H⊗2 on |01⟩ gives (|00⟩-|01⟩+|10⟩-|11⟩)/2
   H⊗2 on |10⟩ gives (|00⟩+|01⟩-|10⟩-|11⟩)/2
   H⊗2 on |11⟩ gives (|00⟩-|01⟩-|10⟩+|11⟩)/2

   Combining:
   |00⟩|00⟩: coefficient from |00⟩→1/2, from |11⟩→1/2, total 1/2+1/2=1 → (1/2)(|00⟩+|11⟩) terms sum to 1
   Wait let me be more careful.

   The state after oracle is:
   (1/2)(|00⟩|00⟩ + |01⟩|01⟩ + |10⟩|01⟩ + |11⟩|00⟩)

   Now apply H⊗2 to the first register:
   |00⟩ → (1/2)(|00⟩+|01⟩+|10⟩+|11⟩)
   |01⟩ → (1/2)(|00⟩-|01⟩+|10⟩-|11⟩)
   |10⟩ → (1/2)(|00⟩+|01⟩-|10⟩-|11⟩)
   |11⟩ → (1/2)(|00⟩-|01⟩-|10⟩+|11⟩)

   Combining with |00⟩ output:
   |00⟩|00⟩ contributes: (1/4)(|00⟩+|01⟩+|10⟩+|11⟩)
   |11⟩|00⟩ contributes: (1/4)(|00⟩-|01⟩-|10⟩+|11⟩)
   
   Combining with |01⟩ output:
   |01⟩|01⟩ contributes: (1/4)(|00⟩-|01⟩+|10⟩-|11⟩)
   |10⟩|01⟩ contributes: (1/4)(|00⟩+|01⟩-|10⟩-|11⟩)

   Total for |00⟩ output: (1/4)(2|00⟩ + 0|01⟩ + 0|10⟩ + 2|11⟩) = (1/2)(|00⟩+|11⟩)|00⟩
   Total for |01⟩ output: (1/4)(2|00⟩ + 0|01⟩ + 0|10⟩ - 2|11

## isqTrain/4113

- task_id: `isqTrain/4113`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `4098`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[3];

procedure main() {

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

Let me analyze this circuit step by step.

Initial state: |000⟩ (q[0], q[1], q[2])

Step 1: CNOT(q[0], q[2])
Control: q[0], Target: q[2]
|000⟩ → |000⟩ (no change since q[0] = 0)

Step 2: CNOT(q[2], q[0])
Control: q[2], Target: q[0]
|000⟩ → |000⟩ (no change since q[2] = 0)

Step 3: CNOT(q[0], q[2])
Control: q[0], Target: q[2]
|000⟩ → |000⟩ (no change since q[0] = 0)

So after the first three CNOTs, state is still |000⟩.

Step 4: H(q[2])
|000⟩ → |00+⟩ = |000⟩/√2 + |001⟩/√2

Step 5: ctrl Rz(-2.0 * π / 4.0, q[2], q[1])
This is Rz(-π/2) controlled by q[2] on q[1].
When q[2] = |1⟩, apply Rz(-π/2) to q[1].

Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2})
Rz(-π/2) = diag(e^{iπ/4}, e^{-iπ/4})

State: (|000⟩ + |001⟩)/√2
When q[2] = 0: |00⟩, q[1] unchanged
When q[2] = 1: |01⟩, apply Rz(-π/2) to q[1]

But q[1] = |0⟩, so Rz(-π/2)|0⟩ = e^{iπ/4}|0⟩

State: (|000⟩ + e^{iπ/4}|001⟩)/√2

Step 6: H(q[1])
H on q[1]:
|0⟩ → (|0⟩ + |1⟩)/√2
|1⟩ → (|0⟩ - |1⟩)/√2

State: (|0+0⟩ + e^{iπ/4}|0+1⟩)/√2
= (|000⟩ + |010⟩ + e^{iπ/4}(|001⟩ - |011⟩))/2

Wait, let me be more careful. The state is:
(|000⟩ + e^{iπ/4}|001⟩)/√2

Applying H(q[1]):
(|0⟩(|0⟩+|1⟩)/√2 · |0⟩ + e^{iπ/4}|0⟩(|0⟩-|1⟩)/√2 · |1⟩)/√2

Hmm, let me use the ordering q[0], q[1], q[2]:

State before H(q[1]): (|000⟩ + e^{iπ/4}|001⟩)/√2

In terms of q[0]q[1]q[2]:
|000⟩ = |0⟩₀|0⟩₁|0⟩₂
|001⟩ = |0⟩₀|0⟩₁|1⟩₂

H(q[1]) acts on q[1]:
|0⟩₁ → (|0⟩₁ + |1⟩₁)/√2

So:
|000⟩ → (|000⟩ + |010⟩)/√2
|001⟩ → (|001⟩ + |011⟩)/√2

State: ((|000⟩ + |010⟩) + e^{iπ/4}(|001⟩ + |011⟩))/(√2·√2)
= (|000⟩ + |010⟩ + e^{iπ/4}|001⟩ + e^{iπ/4}|011⟩)/2

Step 7: ctrl Rz(-2.0 * π / 8.0, q[2], q[0])
This is Rz(-π/4) controlled by q[2] on q[0].
When q[2] = |1⟩, apply Rz(-π/4) to q[0].

Rz(-π/4) on |0⟩: e^{iπ/8}|0⟩

Terms with q[2] = 1: e^{iπ/4}|001⟩ and e^{iπ/4}|011⟩

After controlled Rz(-π/4) on q[0]:
State: (|000⟩ + |010⟩ + e^{iπ/4}·e^{iπ/8}|001⟩ + e^{iπ/4}·e^{iπ/8}|011⟩

### Reference answer

Uniform distribution across 8 states

## isqTrain/1081

- task_id: `isqTrain/1081`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2430`

### Prompt

Help me write isQ code that implements a variant of the deutsch_jozsa pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The task asks me to write a variant of Deutsch-Jozsa using q[2] -> q[3] with an expanded qubit register. Let me analyze The implementation and generate reasoning.

Analyzing the circuit requirements:
- It uses 3 input qubits (q[0], q[1], q[2]) and 1 ancilla (anc[0])
- The oracle is f(x) = x[0] XOR x[1] - a balanced function on 2 bits
- The circuit applies H to q[0] and q[1] (but not q[2] initially), applies the oracle, then H again
- Measurements are on q[0], q[1], q[2]

Wait, looking more carefully at The implementation:
- q[2] is in the register but only H is applied to q[0] and q[1]
- The oracle uses f(q, anc) which applies to the q register
- After the oracle, H is applied to q[0] and q[1]
- All three qubits q[0], q[1], q[2] are measured

Since q[2] starts in |0⟩, no H is applied to it before the oracle, and the oracle f(x) = x[0] XOR x[1] doesn't directly involve q[2]... Actually, looking at the oracle definition, it takes bool x[2] as input, so it only acts on 2 qubits.

Wait, the oracle signature is `oracle bool[1] f(bool x[2])` - this means it takes 2 input bits and returns 1 output bit. When called as `f(q, anc)`, it would use q[0] and q[1] as inputs and anc[0] as output.

So q[2] remains in |0⟩ throughout, and at measurement it's just |0⟩.

Let me trace through:
1. Initial state: |000⟩|1⟩ (q[0], q[1], q[2], anc[0])
2. X(anc[0]): |000⟩|1⟩
3. H(anc[0]): |000⟩(|0⟩-|1⟩)/√2
4. H(q[0]), H(q[1]): (|00⟩+|01⟩+|10⟩+|11⟩)/2 ⊗ |0⟩ ⊗ (|0⟩-|1⟩)/√2
5. Oracle f(q, anc): This applies phase (-1)^f(x) to each |x⟩. f(00)=0, f(01)=1, f(10)=1, f(11)=0
   So: (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2 ⊗ |0⟩ ⊗ (|0⟩-|1⟩)/√2
6. H(q[0]), H(q[1]): The inverse Hadamard transform of the state above.
   
Let me compute H⊗2 applied to (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2:
= 1/2 * (H|0⟩H|0⟩ - H|0⟩H|1⟩ - H|1⟩H|0⟩ + H|1⟩H|1⟩)
= 1/2 * ((|0⟩+|1⟩)(|0⟩+|1⟩) - (|0⟩+|1⟩)(|0⟩-|1⟩) - (|0⟩-|1⟩)(|0⟩+|1⟩) + (|0⟩-|1⟩)(|0⟩-|1⟩))/2

Wait, let me be more careful. H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2, H|1⟩ = |-⟩ = (|0⟩-|1⟩)/√2.

Applying H⊗2 to (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2:

Actually, let me think about this differently. The state after the oracle is:
1/2 * (|00⟩ - |01⟩ - |10⟩ + |11⟩)

This can be written as (Z⊗Z)(H⊗2)|11⟩... hmm, that's getting complicated.

Let me just compute directly:
H⊗2|00⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2
H⊗2|01⟩ = (|00⟩-|01⟩+|10⟩-|11⟩)/2
H⊗2|10⟩ = (|00⟩+|01⟩-|10⟩-|11⟩)/2
H⊗2|11⟩ = (|00⟩-|01⟩-|10⟩+|11⟩)/

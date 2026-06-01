# ISQ training COT RAG corpus: quantum_algorithms shard 148

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2736

- task_id: `isqTrain/2736`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_if_else`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2948`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
bool m1, m2;
qbit q_1, q_2, q_3;
procedure Teleport(qbit qsrc, qbit qanc, qbit qdest) 
{
    H(qanc);
    CNOT(qanc, qdest);
    CNOT(qsrc, qanc);
    H(qsrc);
    m1 = M(qsrc);
    m2 = M(qanc);
    if (m2) { X(qdest); }
    if (m1) { Z(qdest); }
}
procedure main()
{
    X(q_1);
    Teleport(q_1, q_2, q_3);
    print M(q_3);
}
```

### Chain-of-thought reasoning

The user wants a step-by-step quantum state analysis for an isQ quantum program.
The program implements Quantum Teleportation.
Initial state: $|q_1, q_2, q_3\rangle = |000\rangle$.
Main procedure:
X(q_1) -> State becomes $|100\rangle$.
Teleport(q_1, q_2, q_3) is called.
Let's trace Teleport(qsrc=q_1, qanc=q_2, qdest=q_3).
Initial state before Teleport: $|100\rangle$.
H(q_2) -> State becomes $\frac{1}{\sqrt{2}}(|10\rangle + |11\rangle)|0\rangle = \frac{1}{\sqrt{2}}(|100\rangle + |110\rangle)$.
CNOT(q_2, q_3) -> State becomes $\frac{1}{\sqrt{2}}(|10\rangle|0\rangle + |11\rangle|1\rangle) = \frac{1}{\sqrt{2}}(|100\rangle + |111\rangle)$.
CNOT(q_1, q_2) -> State becomes $\frac{1}{\sqrt{2}}(|100\rangle + |011\rangle)$. Wait.
Let's write it in order q1, q2, q3.
$|100\rangle$: q1=1, q2=0. CNOT(1,2) makes q2=1. So $|110\rangle$.
$|111\rangle$: q1=1, q2=1. CNOT(1,2) makes q2=0. So $|101\rangle$.
So state is $\frac{1}{\sqrt{2}}(|110\rangle + |101\rangle)$.
H(q_1) -> Apply H to q1.
$H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
State becomes $\frac{1}{2} (|0\rangle - |1\rangle) \otimes |10\rangle + \frac{1}{2} (|0\rangle - |1\rangle) \otimes |01\rangle$
$= \frac{1}{2} (|010\rangle - |110\rangle + |001\rangle - |101\rangle)$.
Let's re-evaluate:
Initial: $|000\rangle$
X(q_1) $\to |100\rangle$
H(q_2) $\to \frac{1}{\sqrt{2}} (|100\rangle + |110\rangle)$
CNOT(q_2, q_3) $\to \frac{1}{\sqrt{2}} (|100\rangle + |111\rangle)$
CNOT(q_1, q_2) $\to \frac{1}{\sqrt{2}} (|110\rangle + |101\rangle)$
H(q_1) $\to \frac{1}{2} (|010\rangle - |110\rangle + |001\rangle - |101\rangle)$.
Now, the measurements happen:
m1 = M(q_1)
m2 = M(q_2)
But wait, the program actually uses classical measurements to conditionally apply gates.
Wait, the program measures q1 and q2, which collapses the state of q3.
The prompt asks for "the final quantum state before measurement" and "probability distribution over all computational basis states".
Wait, since there are measurements `m1 = M(qsrc); m2 = M(qanc);` inside the procedure, we need to consider the state *before* these measurements if we are computing the final state before measurement over all qubits. Wait, the prompt asks "final quantum state before measurement". But there are intermediate measurements!
Wait, in OpenQASM / isQ, `M(q)` collapses the state. "final quantum state before measurement" could mean the final state of the quantum registers right before the implicit measurement at the end of the circuit, or the state right before the first measurement.
Wait, the predicted output distribution is given as `{'001': 0.25, '010': 0.25, '101': 0.25, '110': 0.25}`.
Wait, why these values?
Let's see:
State before M(q_1) and M(q_2) is $\frac{1}{2}(|001\rangle + |010\rangle - |101\rangle - |110\rangle)$.
The probabilities of measuring the computational basis states for ALL qubits at this point would be:
$|001\rangle \to 0.25$
$|010\rangle \to 0.25$
$|101\rangle \to 0.25$
$|

### Reference answer

{'predicted_probs': {'001': 0.25, '010': 0.25, '101': 0.25, '110': 0.25}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3791

- task_id: `isqTrain/3791`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `1060`

### Prompt

Implement a quantum circuit in isQ: Deutsch-Jozsa for a constant-1 oracle on 2 inputs. The measurement of input qubits should yield |00>.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Generate reasoning for a given isQ quantum program (Deutsch-Jozsa with constant-1 oracle).
    *   **Format:** "## Reasoning" followed by a concise step-by-step explanation.
    *   **Constraints:** 3-15 lines, use Dirac notation, NO isQ code blocks.
    *   **Input:** Prompt, circuit implementation, Expected Probabilities.

2.  **Analyze the circuit implementation:**
    *   Goal: Implement Deutsch-Jozsa algorithm for a 2-input constant-1 oracle.
    *   Qubits: `q[0]`, `q[1]` (inputs), `q[2]` (output). Total 3 qubits.
    *   Initialization: `|000>`
    *   Operations:
        *   `X(q[2])`, `H(q[2])` -> Output qubit in `|-> = (|0> - |1>)/sqrt(2)`
        *   `H(q[0])`, `H(q[1])` -> Input qubits in `|+>|+>`
        *   `f(q[0], q[1], q[2])` -> Constant-1 oracle. The oracle applies `U_f|x>|y> = |x>|y \oplus f(x)>`. Here $f(x) = 1$, so $y \oplus 1 = \text{NOT}(y)$. It flips the output qubit, but wait: phase kickback!
            Actually, `oracle f(2, 1) = [1, 1, 1, 1];` in isQ represents a permutation or diagonal phase matrix. Wait, standard isQ oracle syntax for `f(n, m)` with array of size $2^n$ usually defines a classical function mapping $n$ bits to $m$ bits. But the array has 4 elements `[1, 1, 1, 1]` mapping to $m=1$ bit? Ah, actually `[1, 1, 1, 1]` means $f(00)=1, f(01)=1, f(10)=1, f(11)=1$.
            Wait, in isQ, `oracle f(n, m) = [...]` defines a diagonal unitary $(-1)^{f(x)}$ acting on the input qubits, or does it map to an output qubit? The code uses `f(q[0], q[1], q[2])`, so it takes 3 qubits. The first 2 are inputs, the last 1 is output. The oracle performs $|x, y\rangle \to |x, y \oplus f(x)\rangle$. Since $f(x)=1$ for all $x$, it flips `q[2]` (acts as `X(q[2])`).
            Wait! If `q[2]` is in `|->`, applying `X` to it multiplies by -1.
            So $|x\rangle|-\rangle \to -|x\rangle|-\rangle$.
        *   `H(q[0])`, `H(q[1])` -> Apply Hadamard to inputs.
            Since $|x\rangle \to -|x\rangle$, the state is $-|++\rangle|-\rangle$.
            $H \otimes H (-|++\rangle) = -|00\rangle$.
        *   So the input qubits are exactly in $|00\rangle$.
        *   `q[2]` is still in `|-\rangle`, so measuring it yields 0 with prob 0.5, and 1 with prob 0.5.
    *   Measurements: `M(q[0])`, `M(q[1])`, `M(q[2])` applied in this order.
    *   predicted output bitstrings:
        *   `q[0]` = 0, `q[1]` = 0, `q[2]` = 0 or 1.
        *   Wait, the prompt says "Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}".
        *   Wait, earlier measured qubit = higher bit. `M(q[0])` is first, so it's the highest bit. Bitstring is `q[0]q[1]q[2]`.
        *   Since `q[0]=0`, `q[1]=0`, and `q[2]` is 0 or 1 with 50/50, the bitstrings are `000` and `001`.

3.  **Drafting the Reasoning:**
    *   *Goal*: Implement Deutsch-Jozsa

## isqTrain/3725

- task_id: `isqTrain/3725`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5173`

### Prompt

I need an isQ program to QAOA (p=1) for MaxCut on a 4-node complete graph with edges [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], gamma=0.785, beta=0.393. Use CNOT-Rz-CNOT for cost unitary and Rx for mixer.

### Chain-of-thought reasoning

Let me analyze this QAOA circuit step by step.

1. Goal: Implement QAOA (p=1) for MaxCut on a 4-node complete graph K4.

2. Qubits: 4 qubits (q[0] to q[3]), all measured.

3. State evolution:
- Initial state: |0000>
- After H on all qubits: |++++> = (1/4) * Σ_{x∈{0,1}^4} |x> (equal superposition over all 16 states)

Now for the cost unitary with gamma = 0.785:
- For each edge (i,j), we apply CNOT(i,j), Rz(2*gamma, j), CNOT(i,j)
- This effectively applies a phase of e^{-i*gamma} when both qubits are in the same state

For K4 (complete graph), each vertex is connected to 3 others.

Let me think about this more carefully. The cost Hamiltonian for MaxCut is:
H_C = Σ_{(i,j)∈E} Z_i Z_j

The unitary U_C = e^{-iγ H_C}

For each edge (i,j), the operation e^{-iγ Z_i Z_j} applies a phase:
- e^{-iγ} when Z_i = Z_j (both same)
- e^{iγ} when Z_i ≠ Z_j

The CNOT-Rz-CNOT sequence implements this controlled phase.

Actually, let me reconsider. The CNOT-Rz(2γ)-CNOT on edge (i,j):
- CNOT(i,j): flips j if i=1
- Rz(2γ) on j: applies phase e^{-iγ} to |0>_j and e^{iγ} to |1>_j
- CNOT(i,j): flips j back

The net effect is:
- When |00>: stays |00>, gets phase e^{-iγ}
- When |01>: stays |01>, gets phase e^{iγ}
- When |10>: becomes |11>, gets phase e^{iγ}, becomes |10> → phase e^{iγ}
- When |11>: becomes |10>, gets phase e^{-iγ}, becomes |11> → phase e^{-iγ}

So the phase is e^{-iγ} when qubits are same, e^{iγ} when different.
This gives e^{-iγ Z_i Z_j} when we account for the overall phase.

For the complete graph K4 with 6 edges, the cost unitary applies phases based on how many edges are "cut" (have endpoints in different partitions).

For a bitstring x, the number of edges NOT cut is related to how many pairs are in the same partition.

Actually, let me think about what The resulting probabilities should be. The problem states all 16 states have equal probability 0.0625 = 1/16.

Let me verify this. After H on all qubits, we have equal superposition.
The cost unitary only adds phases, not amplitude changes.
The mixer Rx(2β) applies a rotation around X axis.

Hmm, let me compute more carefully. With γ = 0.785 ≈ π/4 and β = 0.393 ≈ π/8.

Actually, the equal probability result is interesting. Let me think about why this happens.

After H gates: |ψ⟩ = 1/4 Σ|x⟩

After cost unitary: |ψ⟩ = 1/4 Σ_x e^{iφ(x)} |x⟩ where φ(x) depends on the number of edges cut.

For MaxCut on K4:
- |0000⟩: 0 edges cut → phase from 6 edges where both same
- |1111⟩: 0 edges cut → same as above
- States with 1 in one partition and 3 in other (like |0111⟩, |1000⟩, etc.): 3 edges cut
- States with 2 in each partition (like |0011⟩, |0101⟩, etc.): 4 edges cut

For each edge, if endpoints are same, phase = -2γ, if different, phase = +2γ.

Actually, let me reconsider the phase accumulation. Each edge contributes:
- Phase of -γ (from Rz parameter 2γ, and the gate is Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}))

Wait, Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

So Rz(2γ) = [[e^{-iγ}, 0], [0, e^{iγ}]]

With γ = 0.785 ≈ π/4:
- e^{-iγ} ≈ e^{-i

## isqTrain/2829

- task_id: `isqTrain/2829`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4011`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```isq
import std;
qbit q[5];
// Create a 5-qubit GHZ state
procedure main() {
    // H(q[0]); // BUG: missing Hadamard
    for i in 1:5 {
        CNOT(q[i-1], q[i]);
    }
    for i in 0:5 {
        M(q[i]);
    }
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The Hadamard gate `H(q[0])` is commented out, leaving all qubits in |0⟩. With no superposition, every CNOT sees a |0⟩ control and does nothing, yielding deterministic |00000⟩ instead of a GHZ state.
2. **Fix**: Uncomment `H(q[0])` to restore superposition on the first qubit before entangling via CNOTs.
3. **State evolution (corrected)**:
   - Start: |00000⟩
   - H(q[0]): (|00000⟩ + |10000⟩)/√2
   - CNOT(q[0],q[1]): (|00000⟩ + |11000⟩)/√2
   - CNOT(q[1],q[2]): (|00000⟩ + |11100⟩)/√2
   - CNOT(q[2],q[3]): (|00000⟩ + |11110⟩)/√2
   - CNOT(q[3],q[4]): (|00000⟩ + |11111⟩)/√2
   - Measurement yields P(|00000⟩) = 0.5, P(|11111⟩) = 0.5. ✓

## isqTrain/2924

- task_id: `isqTrain/2924`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3744`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    X(q[1]);
    ctrl Rz(0.392699, q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ code**:
    *   `qbit q[2]` (2 qubits, `q[0]` and `q[1]`, initial state |00>)
    *   `H(q[0])`: Hadamard on `q[0]`. State becomes (|00> + |10>) / sqrt(2).
    *   `X(q[1])`: Pauli-X on `q[1]`. State becomes (|01> + |11>) / sqrt(2).
    *   `ctrl Rz(0.392699, q[0], q[1])`: Wait, the isQ syntax for controlled gate is usually `ctrl @q[0] Rz(theta, q[1])` or `ctrl Rz(theta, q[0], q[1])` (standard custom? Ah, wait, `ctrl Rz(theta, q[0], q[1])` means q[0] controls Rz(theta) on q[1]? In isQ `ctrl` modifier or similar? Let me check `ctrl Rz(theta, q[0], q[1])`. The syntax `ctrl Rz(0.392699, q[0], q[1])` is slightly non-standard for isQ but probably means CNOT-like control. Actually, `ctrl Rz(theta, q[0], q[1])` might be interpreted as `q[0]` is control, `q[1]` is target. Let's assume `q[0]` controls `Rz(theta)` on `q[1]`. Wait, standard isQ syntax for 2-qubit ctrl gate is `ctrl Rz(theta, q[1])` with `@q[0]` or similar, but maybe `ctrl Rz(theta, q[0], q[1])` is a known alias? Actually, in isQ `ctrl` takes target qubits, and control is specified by `@`. But if it's written `ctrl Rz(0.392699, q[0], q[1])`, this might be parsed as `q[0]` controls `q[1]`? Or maybe it's a typo in my understanding of isQ docs? "ctrl Rz(0.392699, q[0], q[1])" - I will assume `q[0]` is the control and `q[1]` is the target for the Rz gate. This makes sense. Wait, Rz gate is [[1,0],[0,e^(i*phi)]]. Controlled-Rz on |11> applies e^(i*phi). State was (|01> + |11>)/sqrt(2). Applying CRz: |01> + e^(i*0.392699)|11> over sqrt(2). Note: 0.392699 is approx pi/8.
    *   `H(q[0])`: Hadamard on `q[0]`.
        Let's trace state: |0>(|1>) / sqrt(2) + e^(i*pi/8) |1>(|1>) / sqrt(2)
        Apply H to q[0]:
        = (1/2)(|0> + |1>)|1> + (e^(i*pi/8)/2)(|0> - |1>)|1>
        = (1/2 + e^(i*pi/8)/2)|01> + (1/2 - e^(i*pi/8)/2)|11>.
    *   Calculate probabilities:
        P(01) = |1/2 + e^(i*pi/8)/2|^2 = 1/4 + 1/4 + 2/4 cos(pi/8) = 1/2 (1 + cos(pi/8)).
        P(11) = |1/2 - e^(i*pi/8)/2|^2 = 1/4 + 1/4 - 2/4 cos(pi/8) = 1/2 (1 - cos(pi/8)).
    *   Let's check the given expected measurement probabilities: `{'01': 0.9903926441862724, '11': 0.00960735581372758}`.
    *   Wait. `1/2 (1 + cos(pi/8))` = 1/2 (1 + 0.9238795) = 0.9619...
    *   The given expected probability for `01` is `0.99039264`.
    *   Wait, `cos(pi/8)` is `0.923879`. But `0.990392` is `

### Reference answer

{'predicted_probs': {'01': 0.9903926441862724, '11': 0.00960735581372758}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/96_math_derivation

- task_id: `isqQA/quantum_algorithms/96_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `math_derivation`, `algorithm`, `Grover算法的扩散算子`
- source: `qa_pipeline`
- dataset_index: `1227`

### Prompt

在Grover量子搜索算法中，扩散算子（Diffusion Operator，又称反射算子）是实现状态幅度放大的核心机制。请从量子态演化的角度，严密推导扩散算子 $U_s = 2|s\rangle\langle s| - I$ 的数学形式，证明它如何将当前的量子态绕均匀叠加态 $|s\rangle$ 进行几何反射。随后，请基于该推导，使用isQ语言编写一段作用于4个量子比特的完整代码，要求在代码中人为构造一个非均匀的相位翻转初态，并应用扩散算子进行一次完整的幅度放大操作，最后测量所有比特的概率分布以验证其反射特性。

### Reference answer

<think>
推理分为数学推导与代码构建两步。

在数学推导上，先将任意量子态分解为均匀叠加态 $|s\rangle$ 的平行和垂直分量。将算子 $U_s = 2|s\rangle\langle s| - I$ 作用于该态，可发现平行分量保持不变而垂直分量发生反号，严密证明了其关于 $|s\rangle$ 的几何反射特性。利用Hadamard门性质，该算子可进一步转换为关于零态的反射：$H^{\otimes n}(2|0\rangle\langle 0| - I)H^{\otimes n}$。

在代码构建上（针对4比特）：1. 初始化并用H门制备均匀叠加态；2. 施加特定量子门（如Z门）人为翻转某些计算基态的相位，模拟Oracle构造非均匀初态；3. 实现扩散算子：对全部比特作用H门后，利用X门和多控Z门实现关于 $|0000\rangle$ 的反射，然后再作用H门；4. 测量全部比特，输出概率分布以验证振幅被放大的反射效果。
</think>

在Grover算法中，扩散算子 $U_s$ 的核心作用是在 Hilbert 空间中对量子态进行关于均匀叠加态 $|s\rangle$ 的反射操作，从而实现目标态概率振幅的放大。

一、 严密数学推导与量子态演化
假设我们在 $N=2^n$ 维的 Hilbert 空间中操作，首先通过 Hadamard 门制备均匀叠加态：
$|s\rangle = \frac{1}{\sqrt{N}} \sum_{x=0}^{N-1} |x\rangle$

假设经过 Oracle 相位翻转后，当前的量子态为 $|\psi\rangle$。我们可以将 $|\psi\rangle$ 分解为平行于 $|s\rangle$ 的分量和垂直于 $|s\rangle$ 的分量：
$|\psi\rangle = \alpha|s\rangle + \beta|s^\perp\rangle$
其中，$\alpha = \langle s|\psi\rangle$，$|s^\perp\rangle$ 是满足 $\langle s|s^\perp\rangle = 0$ 的正交态。

现在，我们将扩散算子 $U_s = 2|s\rangle\langle s| - I$ 作用于态 $|\psi\rangle$ 上：
$U_s|\psi\rangle = (2|s\rangle\langle s| - I)(\alpha|s\rangle + \beta|s^\perp\rangle)$
展开此式，利用 $\langle s|s\rangle = 1$ 和 $\langle s|s^\perp\rangle = 0$ 的性质，可得：
$U_s|\psi\rangle = 2\alpha|s\rangle\langle s|s\rangle + 2\beta|s\rangle\langle s|s^\perp\rangle - \alpha|s\rangle - \beta|s^\perp\rangle$
$U_s|\psi\rangle = 2\alpha|s\rangle - \alpha|s\rangle - \beta|s^\perp\rangle = \alpha|s\rangle - \beta|s^\perp\rangle$

数学结论表明，平行于 $|s\rangle$ 的分量保持不变，而垂直于 $|s\rangle$ 的分量被反转了符号。在几何上，这等价于将量子态 $|\psi\rangle$ 关于向量 $|s\rangle$ 进行了一次镜像反射。

在实际量子线路中，通常不直接实现 $U_s$，而是利用恒等式 $U_s = H^{\otimes n} U_0 H^{\otimes n}$ 进行转化，其中 $U_0 = 2|0\rangle\langle 0| - I$。算子 $U_0$ 的作用是保持 $|0\rangle^{\otimes n}$ 态不变，而给其他所有计算基态赋予 $-1$ 的相位。这在物理实现上可以通过对所有量子比特应用 X 门（翻转 $|0\rangle$ 和 $|1\rangle$），执行多控相位门，然后再用 X 门翻转回来来等效替代。

二、 isQ代码实现
以下代码展示了在4量子比特系统下，如何通过构建一个非均匀状态（利用多控X和Z门翻转特定子集的相位），并应用上述推导出的扩散算子线路，最终通过测量观察概率幅度的演化。

import std;
qbit q[4];

procedure main() {
    // 1. 制备均匀叠加态 |s>
    for i in 0:4 {
        H(q[i]);
    }

    // 2. 模拟 Oracle 作用：人为制造非均匀状态
    // 我们翻转子集中态的相位以作区分，例如使用多控门在 |1111> 态打上负号相位
    // 相当于目标态被 Oracle 标记，幅度由正变负
    ctrl @[q[0], q[1], q[2]] Z(q[3]);

    // 3. 执行扩散算子 U_s = 2|s><s| - I
    // 步骤 A: 应用 H 门
    for i in 0:4 {
        H(q[i]);
    }

    // 步骤 B: 实现条件相移算子 2|0><0| - I
    // 对所有比特应用 X 门，将 |0000> 映射为 |1111>
    for i in 0:4 {
        X(q[i]);
    }

    // 对 |1111> 态执行相位翻转，等效于对原来的 |0000> 执行相位翻转
    ctrl @[q[0], q[1], q[2]] Z(q[3]);

    // 再次对所有比特应用 X 门恢复原基矢
    for i in 0:4 {
        X(q[i]);
    }

    // 步骤 C: 再次应用 H 门
    for i in 0:4 {
        H(q[i]);
    }

    // 4. 测量所有比特以验证振幅放大
    // 此时，原先被标记的 |1111> 及其附近状态的幅度将被反向放大
    for i in 0:4 {
        M(q[i]);
    }
}

## isqTrain/1096

- task_id: `isqTrain/1096`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1217`

### Prompt

Create an isQ quantum circuit that implements a variant of the bernstein_vazirani pattern using anc[1] -> anc[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement Bernstein-Vazirani to find hidden string s=101 using anc[1] as the phase-kickback ancilla, with an expanded ancilla register anc[0..3] where unused qubits stay in |0⟩.
2. **Qubits**: 3 input qubits (q[0..2]) + 4 ancilla (anc[0..3]); only q[0..2] are measured.
3. **State evolution**:
   - Init: |000⟩|0000⟩
   - X(anc[1]); H(anc[1]): |000⟩|0−00⟩ (anc[1] in |−⟩ = (|0⟩−|1⟩)/√2)
   - H(q[0..2]): |+++⟩|0−00⟩ = (1/√8)Σ_x |x⟩|0−00⟩
   - Oracle f(q,anc[1]) encodes s·x via CNOTs on q[0],q[2]→anc[1], inducing phase kickback: (1/√8)Σ_x (-1)^(s·x)|x⟩|0−00⟩
   - H(q[0..2]): decodes to |s⟩|0−00⟩ = |101⟩|0−00⟩
4. **Expected probabilities**: Measuring q[0..2] yields |101⟩ with probability 1.0; ancilla qubits anc[0], anc[2], anc[3] remain in |0⟩ unentangled and unmeasured.

## isqTrain/1254

- task_id: `isqTrain/1254`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `638`

### Prompt

Write an isQ program that implements a variant of the error_correction_syndrome pattern using syndrome[2] -> syndrome[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement 3-qubit bit-flip code syndrome detection with an expanded syndrome register (4 qubits), encoding logical |1⟩ and detecting a bit-flip error on data[1].

2. **Qubits**: 7 total — `data[3]` for logical encoding, `syndrome[4]` for parity checks. All 4 syndrome qubits are measured, yielding predicted output `|1100⟩`.

3. **State evolution**:
   - Init: `|000⟩|0000⟩`
   - `X(data[0])`: `|100⟩|0000⟩`
   - `CNOT(d[

## isqExpand/algo/58

- task_id: `isqExpand/algo/58`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `mid_circuit_measurement`, `phase_manipulation`, `ancilla_usage`
- source: `isq_expansion_qa`
- dataset_index: `866`

### Prompt

什么是门隐形传态（Gate Teleportation）？请解释其基本原理，说明它在容错量子计算中的作用，并给出一个使用isQ实现T门传态的示例。

### Chain-of-thought reasoning

## 推理
目标：解释门隐形传态（Gate Teleportation）的原理和应用。

关键点：
1. 门隐形传态将门操作转化为资源态消耗问题。
2. 对于T门：预先制备 magic state |T> = T|+> = (|0>+e^{i*pi/4}|1>)/sqrt(2)。
3. 电路：CNOT(data, ancilla) -> 测量data -> 条件S修正。
4. 在容错量子计算中，Clifford门可以横向实现，T门通过门隐形传态+magic state蒸馏实现。
5. isQ示例需要mid-circuit measurement和条件S门。

### Reference answer

## 门隐形传态（Gate Teleportation）

### 基本概念

门隐形传态是一种利用预先制备的特殊辅助态（magic state）和标准隐形传态协议来实现非Clifford门的技术。其核心思想是：**将门操作转化为状态制备问题**。

### 为什么需要门隐形传态？

在容错量子计算中：
- Clifford门（H, S, CNOT）可以通过量子纠错码横向（transversally）实现。
- 非Clifford门（如T门）不能横向实现，直接实现成本极高。
- 门隐形传态将T门的实现分为：
  1. 离线制备 magic state |T> = T|+> = (|0> + e^{i*pi/4}|1>)/sqrt(2)
  2. 在线消耗 magic state + Clifford操作 + 测量

### T门传态协议

1. 在辅助比特上制备 magic state: T|+>。
2. 将数据比特与辅助比特进行CNOT纠缠。
3. 测量数据比特。
4. 如果测量结果为1，对辅助比特应用S修正门。
5. 辅助比特现在持有 T|psi>。

### isQ 示例

```isq
import std;
qbit q[2];

procedure main() {
    // q[0]: data qubit in |+>
    // q[1]: ancilla with magic state T|+>
    H(q[0]);           // data = |+>
    H(q[1]);
    T(q[1]);           // ancilla = T|+>

    // Gate teleportation circuit
    CNOT(q[0], q[1]);
    int m = M(q[0]);

    // Correction: if m==1, apply S
    if (m == 1) {
        S(q[1]);
    }

    // q[1] now holds T applied to original data state
    M(q[1]);
}
```

### 在容错量子计算中的作用

- 将非Clifford门的实现成本从在线计算转移到离线的 magic state 蒸馏。
- 是实现通用容错量子计算的关键技术之一。
- 与 magic state 蒸馏结合，可以以任意精度实现T门。

## isqTrain/1215

- task_id: `isqTrain/1215`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2800`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the quantum_volume pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants me to generate reasoning for an isQ program that implements a variant of quantum_volume using q[2] -> q[3].

Let me analyze The implementation:
- 3 qubits: q[0], q[1], q[2]
- The circuit applies rotations and CNOTs between q[0] and q[1]
- q[2] is never acted upon, so it stays in |0>
- All three qubits are measured

Expected probabilities:
- |000>: 0.6377359759582624
- |010>: 0.1122640240417365
- |100>: 0.21257865865275538
- |110>: 0.0374213413472457

So q[2] is always 0, and the probabilities for q[0], q[1] are:
- |00>: 0.6377359759582624
- |01>: 0.1122640240417365
- |10>: 0.21257865865275538
- |11>: 0.0374213413472457

Wait, the measurement order matters. In the --probs output, "earlier measured qubit = higher bit". So M(q[0]) is the highest bit, M(q[1]) is the next, M(q[2]) is the lowest bit.

So |000> means q[0]=0, q[1]=0, q[2]=0.

Let me trace through the circuit:

Initial state: |000>

After Ry(pi/3) on q[0]:
Ry(pi/3)|0> = cos(pi/6)|0> + sin(pi/6)|1> = (√3/2)|0> + (1/2)|1>

State: (√3/2)|000> + (1/2)|100>

After Ry(pi/5) on q[1]:
Ry(pi/5)|0> = cos(pi/10)|0> + sin(pi/10)|1>

State: (√3/2)(cos(pi/10)|000> + sin(pi/10)|010>) + (1/2)(cos(pi/10)|100> + sin(pi/10)|110>)

Let me compute:
cos(pi/6) = √3/2 ≈ 0.866
sin(pi/6) = 1/2 = 0.5
cos(pi/10) ≈ 0.951
sin(pi/10) ≈ 0.309

After CNOT(q[0], q[1]):
This flips q[1] when q[0] is |1>

State: (√3/2)(cos(pi/10)|000> + sin(pi/10)|010>) + (1/2)(cos(pi/10)|110> + sin(pi/10)|100>)

So now:
|000>: √3/2 * cos(pi/10)
|010>: √3/2 * sin(pi/10)
|100>: 1/2 * sin(pi/10)
|110>: 1/2 * cos(pi/10)

After Rz(pi/4) on q[0]:
This adds a phase to |1> of q[0]: |0> stays |0>, |1> becomes e^(i*pi/4)|1>

State: (√3/2)(cos(pi/10)|000> + sin(pi/10)|010>) + e^(i*pi/4)(1/2)(cos(pi/10)|110> + sin(pi/10)|100>)

After Rx(pi/6) on q[1]:
This rotates q[1] around X axis. For each basis state, q[1] gets Rx applied.

Rx(pi/6)|0> = cos(pi/12)|0> - i*sin(pi/12)|1>
Rx(pi/6)|1> = -i*sin(pi/12)|0> + cos(pi/12)|1>

Let me denote:
c12 = cos(pi/12) ≈ 0.966
s12 = sin(pi/12) ≈ 0.259

For the q[0]=0 part:
|00> -> c12|00> - i*s12|01>
|01> -> -i*s12|00> + c12|01>

So:
√3/2 * cos(pi/10) * (c12|000> - i*s12|001>) 
+ √3/2 * sin(pi/10) * (-i*s12|000> + c12|001>)
+ e^(i*pi/4) * 1/

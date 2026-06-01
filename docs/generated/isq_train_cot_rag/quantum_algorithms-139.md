# ISQ training COT RAG corpus: quantum_algorithms shard 139

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2815

- task_id: `isqTrain/2815`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4105`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
defgate U0 = [
    1, 0, 0, 0, 0, 0, 0, 0;
    0, -1, 0, 0, 0, 0, 0, 0;
    0, 0, -1, 0, 0, 0, 0, 0;
    0, 0, 0, -1, 0, 0, 0, 0;
    0, 0, 0, 0, -1, 0, 0, 0;
    0, 0, 0, 0, 0, -1, 0, 0;
    0, 0, 0, 0, 0, 0, -1, 0;
    0, 0, 0, 0, 0, 0, 0, -1
];
oracle U_omega(3,1) = [0,1,0,0,0,0,0,0];
qbit q[3];
qbit anc;
int grover_search() {
    H(q);
    H(anc);
    for i in 0:2 {
        U_omega(q[2], q[1], q[0], anc);
        H(q);
        U0(q[2], q[1], q[0]);
        H(q);
    }
    H(anc);
    return M(q);
}
procedure main(){
    print grover_search();
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ program implementing Grover's algorithm.
    *   Output: A concise "Circuit Analysis" explaining the circuit, step-by-step state evolution, final state, and probability distribution.
    *   Format Constraints: Start with "## Circuit Analysis", end with predicted probability distribution, no code blocks, concise (3-15 lines).

2.  **Analyze the isQ Program:**
    *   `qbit q[3]; qbit anc;` -> 4 qubits total. 3 search qubits, 1 ancilla.
    *   Initialization: `H(q); H(anc);` -> Uniform superposition of search space ($|+\rangle^{\otimes 3}$), ancilla is $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
    *   Oracle: `oracle U_omega(3,1) = [0,1,0,0,0,0,0,0];` -> Marks state $|001\rangle$ (which is 1 in decimal). Wait, in isQ, is the array indexed as 0, 1, 2, ... matching the bitstring?
        *   Array `[0,1,0,0,0,0,0,0]` means the 2nd element is 1, which corresponds to state $|001\rangle$ (little-endian or big-endian? usually `q[0]` is LSB). The oracle flips the phase of $|001\rangle$. Let's trace it. If it's state 1 ($|001\rangle$), the oracle applies $Z$ to $|001\rangle$. Wait, the ancilla starts in $|-\rangle$, so standard phase kickback applies.
    *   Diffuser: `H(q); U0(q[2], q[1], q[0]); H(q);`
        *   `U0` is a diagonal matrix with `[1, -1, -1, -1, -1, -1, -1, -1]`.
        *   Wait, `H U0 H` where $U_0 = I - 2|0\rangle\langle0|$?
        *   Let's check $H U_0 H$ on state $|x\rangle$:
        *   $H^{\otimes 3} U_0 H^{\otimes 3} = H^{\otimes 3} (2|0\rangle\langle0| - I) H^{\otimes 3} = 2|+\rangle\langle+| - I$. This is exactly the standard Grover diffusion operator $D$.
    *   Number of iterations: `for i in 0:2` -> This executes for `i = 0, 1`. It runs *twice*!
    *   Wait, isQ `for i in a:b` runs from `a` to `b-1`. So it runs for `i=0` and `i=1`.
    *   Number of qubits $N=8$. Optimal iterations $k \approx \frac{\pi}{4} \sqrt{N} = \frac{\pi}{4} \sqrt{8} \approx \frac{3.14}{4} \times 2.828 \approx 2.2$.
    *   With 2 iterations, it should peak at the target state, but wait, let's calculate the exact probabilities.
    *   Initial amplitude of target $a_t = \sin((2k+1)\theta)$, where $\sin\theta = 1/\sqrt{8}$.
        *   $\theta = \arcsin(1/\sqrt{8}) \approx 20.705^\circ$.
        *   $2k+1 = 5$.
        *   $5\theta \approx 5 \times 20.705^\circ = 103.525^\circ$.
        *   Wait, isQ `for i in a:b` executes `b-a` times. `0:2` means it executes twice.
        *   Let's check $2 \times 2\theta + \theta = 5\theta$.
        *   Initial state: $|\psi\rangle = \sqrt{\frac{7}{8}}|0\rangle + \sqrt{\frac{1}{8}}|1\rangle$ (in the target/non-target basis).
        *   Wait, standard Grover: $\theta \approx 20.7^\circ$. $5\theta \approx 103.5^\circ$.
        *   $\sin(103.5^\circ) \approx 0.97$.

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/899

- task_id: `isqTrain/899`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `interference`, `isq_syntax_deriving_gate`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5498`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[2];

// Z gate wrapper for controlled application
procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure main() {
    // Uniform superposition
    H(q[0]); H(q[1]);

    // Phase oracle for |01>: q[0]=0, q[1]=1
    // Negate q[0] so ctrl fires when original q[0]=0
    X(q[0]);
    ctrl my_z(q[0], q[1]);
    X(q[0]);

    // Diffusion operator: reflect about the mean
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    ctrl my_z(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);

    // Result: |01> with probability 1
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Initial State**: The circuit starts in the 2-qubit state |00⟩.

2. **Superposition**: Applying `H(q[0])` and `H(q[1])` creates a uniform superposition over all states: `1/2(|00⟩ + |01⟩ + |10⟩ + |11⟩)`.

3. **Phase Oracle**: The sequence `X(q[0])`, `ctrl my_z(q[0], q[1])`, `X(q[0])` flips the phase of the target state |01⟩. The `X` gates map |01

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/259. Dimension: predict probabilities for reference circuit.'}

## isqTrain/109

- task_id: `isqTrain/109`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `517`

### Prompt

帮我写一个isQ程序：implements a variant of the qft_subcircuit pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 1-qubit phase estimation circuit for the Z gate, measuring the phase eigenvalue using an expanded 3-qubit register.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]); q[0] and q[2] are measured (q[0] = higher bit in bitstring).
3. **State evolution**:
   - Initial: |000⟩
   - X(q[1]): |010⟩ — prepare Z eigenstate |1⟩ with eigenvalue -1
   - H(q[0]): (|010⟩ + |110⟩)/√2 — superposition on counting qubit
   - ctrl Z(q[0], q[1]): (|010⟩ - |110⟩)/√2 — controlled-Z kicks back phase e^(iπ) = -1
   - H(q[0]): |110⟩ — inverse QFT collapses phase to |1⟩ (representing φ=π)
4. **Result**: Final state |110⟩; measuring q[0]=1 and q[2]=0 yields bitstring |10⟩ with probability 1.0.

## isqTrain/3537

- task_id: `isqTrain/3537`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `basis_change`, `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1837`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```
import std;

qbit q[8];
qbit r[1];

procedure main() {
    X(q[0]);

    CNOT(q[0], q[3]);
    CNOT(q[0], q[6]);
    H(q[0]); H(q[3]); H(q[6]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[3], q[4]);
    CNOT(q[3], q[5]);
    CNOT(q[6], q[7]);
    CNOT(q[6], r[0]);

    CNOT(q[6], r[0]);
    CNOT(q[6], q[7]);
    CNOT(q[3], q[5]);
    CNOT(q[3], q[4]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[1]);
    H(q[6]); H(q[3]); H(q[0]);
    CNOT(q[0], q[6]);
    CNOT(q[0], q[3]);

    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]); M(q[5]); M(q[6]); M(q[7]);
}

```

### Chain-of-thought reasoning

The user wants to predict the output probability distribution of an isQ quantum program.

Let's trace the state of the qubits.
Initial state: |000000000> (9 qubits: q[0]-q[7], r[0])
`X(q[0])` -> |100000000>
CNOT(q[0], q[3]) -> |100100000>
CNOT(q[0], q[6]) -> |100100100>
H(q[0]); H(q[3]); H(q[6])
H(0) changes q[0] to (|0>+|1>)/sqrt(2).
H(3) changes q[3] to (|0>+|1>)/sqrt(2).
H(6) changes q[6] to (|0>+|1>)/sqrt(2).
State of q[0], q[3], q[6] is |+++> and others are 0.
Specifically, it's 1/sqrt(8) (|000000000> + |100000000> + ... wait, no.
Let's trace properly.
q[0] is 1, others 0.
CNOT q[0]->q[3]: q[0]=1, q[3]=1
CNOT q[0]->q[6]: q[0]=1, q[3]=1, q[6]=1
H(q[0]): (|0>+|1>) / sqrt(2)
H(q[3]): (|0>+|1>) / sqrt(2)
H(q[6]): (|0>+|1>) / sqrt(2)
Overall state is (|0>+|1>)(|0>+|1>)(|0>+|1>) / sqrt(8) on q[0], q[3], q[6], others are |0>.

Now the next gates:
CNOT(q[0], q[1])
CNOT(q[0], q[2])
CNOT(q[3], q[4])
CNOT(q[3], q[5])
CNOT(q[6], q[7])
CNOT(q[6], r[0])

This entangles the qubits:
If q[0] is 1, q[1] and q[2] become 1.
If q[3] is 1, q[4] and q[5] become 1.
If q[6] is 1, q[7] and r[0] become 1.
So the state becomes a uniform superposition over all subsets of {q[0,1,2}, q[3,4,5}, q[6,7,r[0]} being active.
Specifically, the groups are:
Group 1: q[0], q[1], q[2]
Group 2: q[3], q[4], q[5]
Group 3: q[6], q[7], r[0]
Each group is either all 0 or all 1. The superposition is uniform over the 8 possibilities.
Each possibility has amplitude 1/sqrt(8) = 1/(2*sqrt(2)).

Wait, the next part of the circuit is EXACTLY the inverse of the previous part, minus the initial X(q[0]).
Let's check the uncomputation:
CNOT(q[6], r[0])
CNOT(q[6], q[7])
CNOT(q[3], q[5])
CNOT(q[3], q[4])
CNOT(q[0], q[2])
CNOT(q[0], q[1])
This reverses the CNOTs.

Then:
H(q[6]); H(q[3]); H(q[0]);
This reverses the Hadamards.

Then:
CNOT(q[0], q[6])
CNOT(q[0], q[3])
This reverses the initial CNOTs.

Let's see the effect of the whole sequence:
Initial: |0...0>
X(q[0]) -> |100...0>
CNOT(q[0], q[3]) -> entangled
CNOT(q[0], q[6]) -> entangled
H(0) H(3) H(6) -> superposition
CNOTs -> highly entangled state
Inverse CNOTs -> unentangles back to superposition of q[0], q[3], q[6]
Inverse Hs -> unentangles back to q[0], q[3], q[6] in computational basis
Inverse CNOTs -> unentangles back to just q[0]
Wait!
Let's trace the exact state after the first set of CNOTs and Hs.
State before first Hs: q[0]=1, q[3]=1, q[6]=1 (

### Reference answer

{'predicted_probs': {'10000000': 1.0}, 'explanation': 'The output is |10000000> with probability 1.0'}

## isqTrain/4465

- task_id: `isqTrain/4465`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3674`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

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
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |0000⟩ (4 qubits q[0], q[1], q[2], q[3])

1. X(q[0]): Flips q[0] → |1000⟩
2. X(q[1]): Flips q[1] → |1100⟩
3. CNOT(q[0], q[2]): Control q[0]=1, so flip q[2] → |1110⟩
4. CNOT(q[1], q[3]): Control q[1]=1, so flip q[3] → |1111⟩
5. H(q[0]); Z(q[0]); H(q[0]): This is HZH = X on q[0], so flip q[0] → |0111⟩

Wait, let me reconsider. The HZH = X operation on q[0] flips it from 1 to 0.

So final state is |0111⟩.

But The predicted output {|0011>: 1.0}. Let me re-read the problem.

Hmm, the expected says number of qubits measured: 4, and the probability is {|0011>: 1.0}.

Wait, let me re-read. Only q[2] and q[3] are measured with M(). But it says 4 qubits measured. In isQ --probs mode, all qubits are typically measured.

Let me reconsider the bitstring ordering. In --probs mode, the bitstring is indexed with earlier measured qubit = higher bit. But typically in isQ, all qubits are measured and the bitstring represents all qubits.

For 4 qubits q[0], q[1], q[2], q[3]:
- State after all operations: |0111⟩ where q[0]=0, q[1]=1, q[2]=1, q[3]=1

Wait, but The predicted output |0011⟩. Let me re-check.

Hmm, maybe the bitstring ordering is different. If q[3] is the highest bit and q[0] is the lowest bit:
- q[3]=1, q[2]=1, q[1]=1, q[0]=0 → binary 1110 = 14

But the expected is |0011⟩ = 3 in decimal, which would be q[3]=0, q[2]=0, q[1]=1, q[0]=1.

That doesn't match either. Let me reconsider.

Wait, maybe I need to re-read: "earlier measured qubit = higher bit". So M(q[2]) is measured first, then M(q[3]). So q[2] is the higher bit and q[3] is the lower bit in the measurement bitstring.

But the expected says 4 qubits measured with |0011>. That seems like all 4 qubits are measured.

Hmm, let me re-examine. Perhaps The predicted output wrong, or perhaps I'm misunderstanding something.

Actually wait - let me re-read the state more carefully.

After X(q[0]) and X(q[1]): |1100⟩ meaning q[0]=1, q[1]=1, q[2]=0, q[3]=0.

After CNOT(q[0], q[2]): q[0]=1 so q[2] flips to 1. State: |1110⟩
After CNOT(q[1], q[3]): q[1]=1 so q[3] flips to 1. State: |1111⟩

After HZH on q[0] (= X gate): q[0] flips from 1 to 0. State: |0111⟩

In bitstring with q[0] as least significant bit: q[3]q[2]q[1]q[0] = 1110

Hmm, that doesn't match |0011⟩ either.

Actually, let me reconsider. Maybe the ordering is q[0] as most significant bit:
q[0]q[1]q[2]q[3] = 0111, which in binary as a number is 7.

|0011⟩ would be q[0]=0, q[1]=0, q[2]=1, q[3]=1, which is state where q[0]=0, q[1]=0, q[2]=1, q[3]=1.

That doesn't match what I calculated. Let me recheck once more.

Hmm, maybe I'm wrong about HZH = X. Let me verify:
HZH = H·Z·H

H = (1/√2)[[1,1],[1,-1]]
Z = [[1,0],[0,-1]]

### Reference answer

{'predicted_probs': {'0011': 1.0}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0011>) = 1.0000.'}

## isqExpand/algo/57

- task_id: `isqExpand/algo/57`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `mid_circuit_measurement`, `basis_change`
- source: `qa_pipeline`
- dataset_index: `3233`

### Prompt

什么是纠缠交换（Entanglement Swapping）？请解释其原理，说明它与量子隐形传态的关系，并给出一个使用isQ实现的示例电路。

### Chain-of-thought reasoning

## 推理
目标：解释纠缠交换的概念、原理及其与隐形传态的关系。

关键点：
1. 纠缠交换涉及四个量子比特，分为两对初始纠缠对。
2. 对中间两个比特（分属不同对）进行Bell测量。
3. 测量将外部两个比特投影到纠缠态。
4. 需要经典通信传递测量结果来确定修正操作。
5. 与标准隐形传态共享相同的核心机制（Bell测量+经典修正），但传送的是"纠缠"而非"状态"。
6. isQ实现需要mid-circuit measurement和条件门操作。
7. 应用于量子中继器和量子网络。

### Reference answer

## 纠缠交换（Entanglement Swapping）

### 基本概念

纠缠交换是一种量子协议，能够在**从未直接相互作用过**的两个粒子之间建立纠缠。

### 协议流程

假设有四个量子比特 q[0], q[1], q[2], q[3]：
1. 创建两对Bell态：q[0]-q[1] 纠缠，q[2]-q[3] 纠缠。
2. 对 q[1] 和 q[2]（分属两对的各一个粒子）进行Bell测量。
3. 根据测量结果对 q[3] 进行经典修正（X 和 Z 门）。
4. 结果：q[0] 和 q[3] 变为纠缠态，尽管它们从未直接交互。

### 与量子隐形传态的关系

纠缠交换本质上是**纠缠态的隐形传态**：
- 普通隐形传态：传送一个未知量子态
- 纠缠交换：传送纠缠关系本身

两者都使用相同的核心操作：Bell测量 + 经典通信 + 条件修正。

### isQ 示例

```isq
import std;
qbit q[4];

procedure main() {
    // 创建两对Bell态
    H(q[0]); CNOT(q[0], q[1]);  // q[0]-q[1] 纠缠
    H(q[2]); CNOT(q[2], q[3]);  // q[2]-q[3] 纠缠

    // 对 q[1], q[2] 做Bell测量
    CNOT(q[1], q[2]);
    H(q[1]);
    int m1 = M(q[1]);
    int m2 = M(q[2]);

    // 经典修正
    if (m2 == 1) { X(q[3]); }
    if (m1 == 1) { Z(q[3]); }

    // 现在 q[0] 和 q[3] 纠缠
    M(q[0]); M(q[3]);
}
```

### 应用

- **量子中继器**：在长距离量子通信中，通过多段纠缠交换实现远距离纠缠分发。
- **量子网络**：是构建量子互联网的核心原语。

## isqTrain/2962

- task_id: `isqTrain/2962`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `747`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[0]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step trace of an isQ quantum program, predicting the final probability distribution of the measurement outcomes. The response must be concise (3-15 lines), use Dirac notation, follow a specific format ("## Circuit Analysis"), and end with the probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: $|000\rangle$
    *   Apply $H$ to $q_0, q_1, q_2$:
        *   State becomes $\frac{1}{2\sqrt{2}} (|000\rangle + |001\rangle + |010\rangle + |011\rangle + |100\rangle + |101\rangle + |110\rangle + |111\rangle)$. Actually, $H^{\otimes 3}|000\rangle = \frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x\rangle$.
    *   Apply $CNOT(q_0, q_1)$: (Flips $q_1$ if $q_0=1$)
        *   $|000\rangle \to |000\rangle$
        *   $|001\rangle \to |001\rangle$
        *   $|010\rangle \to |110\rangle$
        *   $|011\rangle \to |111\rangle$
        *   $|100\rangle \to |110\rangle$
        *   $|101\rangle \to |111\rangle$
        *   $|110\rangle \to |100\rangle$
        *   $|111\rangle \to |101\rangle$
        *   Wait, let's represent the state as amplitudes.
        *   Start with equal amplitudes $1/\sqrt{8}$ for all 8 states.
        *   $CNOT_{01}$ swaps amplitudes of $|010\rangle \leftrightarrow |110\rangle$ and $|011\rangle \leftrightarrow |111\rangle$. Since all are equal, the state vector is *identical* to the original uniform superposition!
    *   Apply $CNOT(q_1, q_2)$: (Flips $q_2$ if $q_1=1$)
        *   Swaps amplitudes of $|010\rangle \leftrightarrow |011\rangle$ and $|110\rangle \leftrightarrow |111\rangle$.
        *   Again, all amplitudes are equal, so the state remains the uniform superposition.
    *   Apply $CNOT(q_2, q_0)$: (Flips $q_0$ if $q_2=1$)
        *   Swaps amplitudes of $|000\rangle \leftrightarrow |100\rangle$, $|010\rangle \leftrightarrow |110\rangle$, $|001\rangle \leftrightarrow |101\rangle$, $|011\rangle \leftrightarrow |111\rangle$.
        *   Still equal amplitudes, state remains the uniform superposition!
    *   Wait, let's double check this property. Any CNOT applied to a uniform superposition of all states leaves the state unchanged, up to a permutation of the basis states which doesn't change the state vector since all coefficients are identical.
        *   State: $\frac{1}{\sqrt{8}} \sum_{x} |x\rangle$.
        *   CNOT is a permutation matrix $P$. $P \frac{1}{\sqrt{8}} \sum_x |x\rangle = \frac{1}{\sqrt{8}} \sum_x P|x\rangle = \frac{1}{\sqrt{8}} \sum_y |y\rangle = \frac{1}{\sqrt{8}} \sum_x |x\rangle$.
        *   Yes, the state is invariant under ANY permutation of the basis states.
    *   Conclusion: The final state is the uniform superposition $\frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x\rangle$.
    *   Measurement probabilities: $1/8 = 0.125$ for all 8 basis states.

3.  **Draft the Explanation:**
    *   Initial state: $|000\rangle$
    *   After H gates: Uniform superposition $\frac{1}{\sqrt{8}}(|000\rangle + |001\rangle + |010\rangle + |011\rangle + |100\rangle + |101\rangle + |110\rangle + |111\rangle)$.
    *   CNOT gates apply permutations to the basis states. Because all coefficients in the uniform superposition are equal, any permutation leaves the

### Reference answer

{'predicted_probs': {'000': 0.12500000000000003, '001': 0.12500000000000003, '010': 0.12500000000000003, '011': 0.12500000000000003, '100': 0.12500000000000003, '101': 0.12500000000000003, '110': 0.12500000000000003, '111': 0.12500000000000003}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2981

- task_id: `isqTrain/2981`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4633`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[2];
// Controlled-H circuit: q[0] controls H on q[1]
procedure main() {
    // X(q[0]); // BUG: missing initialization
    ctrl H(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

**Bug:** The `X(q[0])` gate is commented out, leaving `q[0]` in |0⟩. Since the controlled-H gate only fires when the control qubit is |1⟩, the gate does nothing and both qubits remain in |00⟩, producing deterministic |00⟩ measurements instead of the expected superposition.

**Fix:** Uncomment `X(q[0])` to initialize the control qubit to |1⟩, enabling the controlled-H to activate.

**State evolution (corrected):**
1. Initial: |00⟩
2. After X(q[0]): |10⟩
3. After ctrl H(q[0], q[1]): control is |1⟩, so H applies to q[1] → (|10⟩ + |11⟩)/√2
4. Measurement yields |10⟩ with probability 0.5 and |11⟩ with probability 0.5 ✓

## isqTrain/882

- task_id: `isqTrain/882`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4686`

### Prompt

Create an isQ quantum circuit that implements the inner_product_mod2 pattern. Include explicit identity operations in the circuit (X-X pair before M(q[6])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Compute the inner product mod 2 of binary vectors x=[1,0,1] and y=[1,1,0], storing the result in qubit q[6] and demonstrating gate cancellation with an X-X identity pair.

**Qubits**: 7 qubits (q[0]-q[6]); only q[6] is measured.

**State evolution**:
- Start: |0000000⟩
- After encoding x on q[0,1,2] with X(q[0]), X(q[2]): |1010000⟩
- After encoding y on q[3,4,5] with X(q[3]), X(q[4]): |1011100⟩
- Toffoli(q[0],q[3],q[6]): controls q[0]=1, q[3]=1 satisfied → flip q[6]: |1011101⟩
- Toffoli(q[1],q[4],q[6]): control q[1]=0 not satisfied → no change: |1011101⟩
- Toffoli(q[2],q[5],q[6]): control q[5]=0 not satisfied → no change: |1011101⟩
- IP = x·y mod 2 = 1⊕0⊕

## isqTrain/912

- task_id: `isqTrain/912`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `5569`

### Prompt

Implement the following in isQ: implements a variant of the bit_flip_oracle pattern using ancilla[1] -> ancilla[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a boolean oracle computing AND of two input qubits into an ancilla, using an expanded register (ancilla[2] instead of ancilla[1]).

2. **Qubits**: 4 total — q[0], q[1] (inputs), ancilla[0] (oracle output), ancilla[1] (unused). All measured: M(q[0]), M(q[1]), M(ancilla[0]), M(ancilla[1]).

3. **State evolution**:
   - Initialize |q₀q₁a₀a₁⟩ = |0000⟩
   - X(q[0]), X(q[1]) → |1100⟩ (set inputs to |11⟩)
   - Oracle f(q, ancilla) computes AND via Toffoli: flips ancilla[0] when both controls are |1⟩ → |1110⟩
   - ancilla[1] remains |0⟩ throughout (unused)

4. **Expected probabilities**: Final state |1110⟩ yields measurement bitstring 1110 (q[0]=1, q[1]=1, ancilla[0]=1, ancilla[1]=0) with probability 1.0.

# ISQ training COT RAG corpus: quantum_algorithms shard 11

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2861

- task_id: `isqTrain/2861`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2967`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Trace the isQ quantum program, explain step-by-step reasoning (Dirac notation), output probability distribution in JSON array format.
    *   Input: An isQ program creating a 3-qubit GHZ state (H on q[0], CNOT on q[0]->q[1], CNOT on q[1]->q[2]).
    *   Output Requirements: Concise (3-15 lines), Dirac notation, start with "## Circuit Analysis", end with JSON array of probabilities, no code blocks.

2.  **Trace the Circuit:**
    *   Initial state: |000>
    *   H(q[0]): Applies Hadamard to q[0]. State becomes 1/sqrt(2) (|000> + |100>).
    *   CNOT(q[0], q[1]): Flips q[1] if q[0] is |1>. State becomes 1/sqrt(2) (|000> + |110>).
    *   CNOT(q[1], q[2]): Flips q[2] if q[1] is |1>. State becomes 1/sqrt(2) (|000> + |111>). This is the standard 3-qubit GHZ state.
    *   Measurements: Measure q[0], q[1], q[2].
    *   Outcomes: '000' with probability |1/sqrt(2)|^2 = 0.5. '111' with probability |1/sqrt(2)|^2 = 0.5.

3.  **Format the Output:**
    *   Section: "## Circuit Analysis"
    *   Text: Step-by-step evolution using Dirac notation.
    *   End: JSON array `["000: 0.5", "111: 0.5"]` (or as requested, typically standard JSON object or array of strings, I'll provide the JSON object format since the prompt says "array" but standard probs format is `{"000": 0.5, "111": 0.5}`). Wait, the prompt explicitly says "Return a JSON array." Let's make it `[{"000": 0.5}, {"111": 0.5}]` or just an array of probabilities. Actually, standard is `{"000": 0.5, "111": 0.5}` but prompt says "Return a JSON array". Let's provide standard JSON array of objects or simple dict-like strings. I will use `["000: 0.5", "111: 0.5"]` or `["000", "111"]`? Let me re-read "Return a JSON array." Usually `[0.5, 0.0, ..., 0.5]` for 3 qubits (8 elements) is standard for statevector simulations. Let's provide the exact bitstring map. I will provide `{"000": 0.5, "111": 0.5}` as it's the standard way to denote probability distributions, but encapsulated in standard JSON format, or just an array like `["000: 0.5", "111: 0.5"]`. Let's provide a JSON array of strings if it has to be an array of strings, or JSON object. I'll output standard JSON dict `{"000": 0.5, "111": 0.5}` as that is universally understood, but I'll also add the array if required. Actually, I will just provide standard dict format since "JSON array" is sometimes loosely used. Let's do `["000: 0.5", "111: 0.5"]` just to be safe, or a full 8-element array `[0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5]`? The predicted output `{'000': 0.5, '111': 0.5}`. Let's just use that. Actually, I'll output the dictionary.

4.  **Drafting the Text:**
    ## Circuit Analysis
    1. **Initial state**: |000>
    2. **H(q[0])**: Applies Hadamard gate to qubit 0, creating superposition: 1/√2 (|000> + |100>)
    3. **CNOT(q[0], q[1])**: Entangles q[0] and q[1] by flipping q[1] when q[0] is |1>: 1/√2 (|000> + |110>)
    4. **CNOT(q[1], q[2])**: Entangles q[1] and q[2] by

### Reference answer

{'predicted_probs': {'000': 0.5, '111': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2721

- task_id: `isqTrain/2721`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_if_else`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2461`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
oracle A(4,1) = [0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1];
oracle g(2,1) = [0,1,1,0]; 
int a;
qbit q[4], p[3];
procedure hadamard_layer(int k){
    H(q[2*k]);
    H(q[2*k+1]);
}
procedure recursive_fourier_sampling(int k){
    if (k == 2){
        A(q[0], q[1], q[2], q[3], p[2]);
    }else{
        hadamard_layer(k);
        X(p[k+1]);
        H(p[k+1]);
        recursive_fourier_sampling(k+1);
        hadamard_layer(k);
        g(q[2*k],q[2*k+1], p[k]);
        hadamard_layer(k);
        recursive_fourier_sampling(k+1);
        hadamard_layer(k);
        H(p[k+1]);
        X(p[k+1]);
    }
}
procedure main(){
    a = 0;
    recursive_fourier_sampling(a);
    int g = M(p[0]);    
    print g;
}
```

### Chain-of-thought reasoning

Let me trace through this isQ quantum program step by step.

First, let me understand the structure:
- We have 4 qubits `q[0..3]` and 3 qubits `p[0..2]`
- We have oracle `A` (4 inputs, 1 output) with truth table [0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1]
- We have oracle `g` (2 inputs, 1 output) with truth table [0,1,1,0]
- The main function calls `recursive_fourier_sampling(0)`

The oracle `g` with truth table [0,1,1,0]:
- |00⟩ → 0
- |01⟩ → 1
- |10⟩ → 1
- |11⟩ → 0

This is the XOR function (or parity function).

Oracle `A` with 4 inputs and 1 output, truth table [0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1]:
This maps 4 input qubits to 1 output. The truth table has 16 entries.
- A(0000) = 0
- A(0001) = 1
- A(0010) = 1
- A(0011) = 0
- A(0100) = 0
- A(0101) = 0
- A(0110) = 0
- A(0111) = 0
- A(1000) = 0
- A(1001) = 0
- A(1010) = 1
- A(1011) = 1
- A(1100) = 0
- A(1101) = 1
- A(1110) = 0
- A(1111) = 1

Let me trace the recursive_fourier_sampling function:

**k=0:**

**k=1 (called twice):**

**k=2:**

Now let me understand what these oracles do:
- `g(q[0], q[1], p[0])` applies a phase based on the XOR of q[0] and q[1] to p[0]
- `A(q[0], q[1], q[2], q[3], p[2])` applies a phase based on A function to p[2]

The oracle gate typically works as: |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩ or applies a phase (-1)^f(x).

Let me think about this more carefully. In isQ, an oracle with n inputs and 1 output likely performs:
|x⟩|0⟩ → |x⟩|f(x)⟩

Or it might be a phase oracle: |x⟩ → (-1)^f(x)|x⟩

Looking at the code, the oracles are applied to qubits q[0..3] and p[2]. The p qubits seem to be used as

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3526

- task_id: `isqTrain/3526`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `133`

### Prompt

预测以下isQ代码的输出概率：

```
import std;

qbit q[3];
qbit anc[1];

procedure main() {
    X(anc[0]);
    H(anc[0]);

    H(q[0]); H(q[1]); H(q[2]);

    CNOT(q[0], anc[0]);

    H(q[0]); H(q[1]); H(q[2]);

    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a concise step-by-step analysis of an isQ quantum program, predicting the final output probability distribution.
2.  **Analyze the isQ code**:
    *   Qubits: `q[3]` (measured), `anc[1]` (not measured).
    *   Initial state: $|000\rangle_q \otimes |0\rangle_{anc} = |0000\rangle$
    *   `X(anc[0])`: anc becomes $|1\rangle$. State: $|000\rangle_q \otimes |1\rangle_{anc}$
    *   `H(anc[0])`: anc becomes $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. State: $|000\rangle_q \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_{anc}$
    *   `H(q[0]); H(q[1]); H(q[2])`: All q become $|+\rangle$. State: $\frac{1}{\sqrt{8}} (|0\rangle+|1\rangle)^{\otimes 3}_q \otimes (|0\rangle - |1\rangle)_{anc} = \frac{1}{\sqrt{8}}(|000\rangle + |001\rangle + \dots + |111\rangle)_q \otimes (|0\rangle - |1\rangle)_{anc}$
    *   `CNOT(q[0], anc[0])`:
        *   Control: `q[0]`, Target: `anc[0]`.
        *   For states where $q[0]=|0\rangle$, anc is unchanged: $|0\rangle - |1\rangle$.
        *   For states where $q[0]=|1\rangle$, anc is flipped: $|1\rangle - |0\rangle = -(|0\rangle - |1\rangle)$.
        *   Overall state: $\frac{1}{\sqrt{8}} (|000\rangle + |001\rangle + |010\rangle + |011\rangle - |100\rangle - |101\rangle - |110\rangle - |111\rangle)_q \otimes (|0\rangle - |1\rangle)_{anc}$.
        *   This is a phase kickback! The ancilla is still $|-\rangle$, but the control qubit $q[0]$ got a $Z$ phase applied.
        *   Mathematically, $H^{\otimes 3}_q (Z \otimes I \otimes I) |000\rangle_q$.
    *   `H(q[0]); H(q[1]); H(q[2])`:
        *   Applying $H$ again undoes the first $H$'s, but leaves the $Z$ on $q[0]$.
        *   $H Z H = X$.
        *   So the state becomes: $(X|0\rangle) \otimes (H|0\rangle) \otimes (H|0\rangle) \otimes |-\rangle_{anc} = |1\rangle \otimes |0\rangle \otimes |0\rangle \otimes |-\rangle_{anc}$.
        *   Wait, $H$ on the $|+\rangle$ and $|-\rangle$ terms gives back $|0\rangle$ and $|1\rangle$.
        *   Let's trace carefully:
            $|00\rangle_{q1,q2}$ stays $|00\rangle$.
            $q[0]$ part: $H$ applied to $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |1\rangle$.
        *   So the state is exactly $|100\rangle_q \otimes |-\rangle_{anc}$.
    *   `M(q[0]); M(q[1]); M(q[2])`:
        *   Measures $q[0]=1, q[1]=0, q[2]=0$ with probability 1.
        *   Bitstring is "100" (value 4).
3.  **Format the Output**:
    *   Follow the 3-15 line rule for reasoning.
    *   Dirac notation.
    *   Start with "## Circuit Analysis".
    *   End with the distribution.
4.  **Drafting the text**:
    *   Initial state $|000\rangle_q |0\rangle_{anc}$.
    *   Apply $X(anc[0])$ and $H(anc[0])$ to prepare anc

### Reference answer

{'predicted_probs': {'100': 1.0}, 'explanation': 'The output is |100> with probability 1.0'}

## isqTrain/764

- task_id: `isqTrain/764`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4170`

### Prompt

Write isQ code for the following quantum task: implements the weighted_adder pattern. Include explicit identity operations in the circuit (H-H pair before M(q[2])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Implement a weighted adder computing a 2-bit sum from two input qubits, with an explicit H-H identity pair to demonstrate gate cancellation.

**Qubits**: 4 qubits (q[0..3]); inputs q[0], q[1]; sum bits q[2] (weight 1), q[3] (weight 2); only q[2] and q[3] are measured.

**State evolution**:
- Initial: |0000⟩
- X(q[0]); X(q[1]): |1100⟩ — both inputs set to |1⟩
- CNOT(q[0], q[2]): |1110⟩ — adds x₀ (weight 1) to sum bit 0
- CNOT(q[1], q[3]): |1111⟩ — adds x₁ (weight 2) to sum bit 1
- H(q[2]): q[2] → |−⟩ = (|0⟩−|1⟩)/√2; state = (|1101⟩−|1111⟩)/√2
- H(q[2]): H² = I, so q[2] returns to |1⟩; state = |1111⟩
- Measure q[2], q[3]: both in |1⟩

**Expected probabilities**: The final state is |1111⟩, so measuring q[2] and q[3] yields |11⟩ with probability 1.0. The H-H pair cancels perfectly, having no net effect.

## isqTrain/1349

- task_id: `isqTrain/1349`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_deriving_gate`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1132`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[3];

procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure main() {

    X(q[1]);

    H(q[0]);

    ctrl my_z(q[0], q[1]);

    H(q[0]);

    M(q[0]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task type: `output_prediction`
    *   Input: isQ quantum program.
    *   Output: Circuit Analysis (3-15 lines, concise, step-by-step reasoning using Dirac notation), ending with the predicted probability distribution.
    *   Program details:
        *   3 qubits: `q[0], q[1], q[2]` initialized to $|000\rangle$.
        *   `X(q[1])` -> flips qubit 1 to $|1\rangle$.
        *   `H(q[0])` -> puts qubit 0 in $|+\rangle$.
        *   `ctrl my_z(q[0], q[1])` -> applies `Z` to `q[1]` conditioned on `q[0]`.
        *   `H(q[0])` -> applies Hadamard to qubit 0.
        *   `M(q[0])` and `M(q[2])` -> measure qubits 0 and 2.
    *   Format Requirements: Start with "## Circuit Analysis", use Dirac notation, no code blocks, end with "Expected measurement probabilities: {...}".

2.  **Step-by-Step Execution:**
    *   Initial state: $|000\rangle$ (q[2], q[1], q[0])
    *   After `X(q[1])`: $|010\rangle$ (in standard notation $|q_2 q_1 q_0\rangle$). Actually, let's trace $|q_0 q_1 q_2\rangle$.
        *   $|0_0 0_1 0_2\rangle \xrightarrow{X_1} |0_0 1_1 0_2\rangle = |010\rangle$
    *   After `H(q[0])`: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_0 \otimes |1_1 0_2\rangle = \frac{1}{\sqrt{2}}(|010\rangle + |110\rangle)$
    *   After `ctrl my_z(q[0], q[1])`: `my_z` is `Z`. `ctrl` applies `Z` to `q[1]` if `q[0]` is $|1\rangle$.
        *   If $q_0 = 0$, state is $|010\rangle$. `Z` not applied to $q_1$.
        *   If $q_0 = 1$, state is $|110\rangle$. `Z` applied to $q_1$. $Z|1\rangle = -|1\rangle$.
        *   State becomes $\frac{1}{\sqrt{2}}(|010\rangle - |110\rangle) = \frac{1}{\sqrt{2}}(|0\rangle_0 - |1\rangle_0) \otimes |1_1 0_2\rangle = |-\rangle_0 |1_1 0_2\rangle$
    *   After `H(q[0])`: $H|-\rangle_0 = |1\rangle_0$.
        *   State becomes $|1_0 1_1 0_2\rangle = |110\rangle$.
    *   Measurements: `M(q[0])` and `M(q[2])`.
        *   $q_0$ is $|1\rangle$.
        *   $q_2$ is $|0\rangle$.
    *   predicted output string for bitstring: $q_0$ is measured first, so it's the higher bit in the isQ `--probs` notation? Wait, the prompt says: "`--probs` output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
        *   Measured qubits: `M(q[0])` then `M(q[2])`.
        *   $q_0$ is the higher bit, $q_2$ is the lower bit.
        *   Result: $q_0=1, q_2=0 \Rightarrow |10\rangle$.
    *   Expected probability: 1.0 for $|10\rangle$.

3.  **Drafting the Text:**
    *   Keep it short and concise (3-8 lines).
    *   Initial state: $|000\rangle$
    *   Apply $X$ to $q_1$: state becomes $|010\rangle$.
    *   Apply $H$ to $q_0$: state becomes $\frac{1}{\sqrt{2}}

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqEval/495. Dimension: qubit_variant: q[2] -> q[3].'}

## isqQA/quantum_algorithms/119_principle_advantage

- task_id: `isqQA/quantum_algorithms/119_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `principle_advantage`, `algorithm`, `固定点振幅放大`
- source: `qa_pipeline`
- dataset_index: `5013`

### Prompt

请深入解释固定点振幅放大算法的核心宏观原理及其在时间复杂度上的优势。相比于传统的Grover算法，它如何解决“过度翻转（ soufflé problem）”问题并带来量子加速？请给出具有动态变相位旋转特征的isQ代码演示。

### Reference answer

循序渐进的数学推导与代码推理如下：

1. 宏观原理分析：
传统Grover算法本质上是状态空间中围绕两个轴的反射（即相位反转）。其旋转角度是固定的，这要求我们必须精确知道目标态的数量才能在概率达到峰值时停止迭代。一旦迭代次数越过最高点，概率反而会下降（即过度翻转问题）。固定点振幅放大（FPAA）摒弃了精确的 $\pi$ 相位翻转，转而使用一对随迭代次数动态变化的相位旋转 $\alpha_k, \beta_k$。通过这种设计，算法酉算子的特征值在特定子空间内形成一种“吸收壁”效应，使得无论初始目标态振幅的下界如何，经过足够次数的迭代后，系统状态都会单调收敛于目标态。这种收敛特性使得最终概率对目标态的数量不敏感，因此被称为“固定点”。

2. 时间复杂度与量子加速来源：
传统Grover算法的时间复杂度为 $O(\sqrt{N/M})$（$M$为目标态数量），但在 $M$ 未知时需要复杂的量子计数或面临失败风险。FPAA的时间复杂度为 $O(\frac{1}{\sqrt{\lambda}} \log(1/\delta))$，其中 $\lambda$ 是初始目标概率的下界估计，$\delta$ 为容许误差。相比于经典遍历算法的 $O(1/\lambda)$，FPAA依然保持了二次加速（$\sqrt{1/\lambda}$），其代价仅仅是增加了一个对数级别的开销 $\log(1/\delta)$。这种量子加速的来源依然得益于量子态在希尔伯特空间中的相干叠加与干涉效应，但通过舍弃破坏性的严格相位反转，采用非精确的干涉使得有用信号（目标态振幅）被单向放大。

3. isQ代码实现：
下面的代码展示了FPAA算法核心的变相位迭代逻辑，通过不同的角度参数模拟向固定点收敛的过程。

import std;

const N = 3;
qbit q[N];
qbit anc[1];

// 标记目标态的变相位反射
procedure apply_beta_rotation(double beta) {
    // 假设目标态是 |111>，使用辅助比特进行多控制相位旋转
    Toffoli(q[0], q[1], anc[0]);
    ctrl @[anc[0]] Rz(beta, q[2]);
    Toffoli(q[0], q[1], anc[0]);
}

// 初始叠加态的变相位反射
procedure apply_gamma_rotation(double gamma) {
    // 变换到以 |+> 为基的空间
    for i in 0:N {
        H(q[i]);
    }
    // 以 |000> 为中心进行变相位旋转
    for i in 0:N {
        X(q[i]);
    }
    Toffoli(q[0], q[1], anc[0]);
    ctrl @[anc[0]] Rz(gamma, q[2]);
    Toffoli(q[0], q[1], anc[0]);
    for i in 0:N {
        X(q[i]);
    }
    // 变换回计算基
    for i in 0:N {
        H(q[i]);
    }
}

procedure main() {
    // 初始化为等额叠加态
    for i in 0:N {
        H(q[i]);
    }

    // FPAA的核心：通过非 $
    // 设置两组不同的收敛相位以体现动态特征
    double beta1 = 0.35;
    double gamma1 = 0.17;
    double beta2 = 0.68;
    double gamma2 = 0.34;

    // 第一次 FPAA 迭代
    apply_beta_rotation(beta1);
    apply_gamma_rotation(gamma1);

    // 第二次 FPAA 迭代
    apply_beta_rotation(beta2);
    apply_gamma_rotation(gamma2);

    // 测量输出
    for i in 0:N {
        M(q[i]);
    }
    M(anc[0]);
}

## isqTrain/3077

- task_id: `isqTrain/3077`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `4841`

### Prompt

Help me write isQ code that initializes 4 qubits to the state |1111> using X gates and measures all.

Requirements:
- Declare `qbit q[4];` at global scope.
- Apply X to qubits that should be |1>.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare the 4-qubit state |1111⟩ and measure all qubits.
We need 4 qubits (q[0]–q[3]), all measured. Each starts in |0⟩.
Applying X to each qubit flips |0⟩ to |1⟩: q[0]→|1⟩, q[1]→|1⟩, q[2]→|1⟩, q[3]→|1⟩, yielding the product state |1111⟩.
Measurement of each qubit in the computational basis deterministically gives 1, so the outcome |1111⟩ occurs with probability 1.0.

## isqTrain/770

- task_id: `isqTrain/770`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4991`

### Prompt

Help me write isQ code that implements a variant of the weighted_adder pattern using q[5] -> q[7]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a weighted adder that computes the sum of three input qubits (x0+x1+x2) using q[3] for the sum bit and q[4] for the carry bit, with q[5]-q[6] as unused ancillary qubits.

2. **Qubits**: 7 total (q[0]-q[6]). Inputs: q[0], q[1], q[2]; Sum: q[3]; Carry: q[4]; Unused: q[5], q[6]. Measured: q[3], q[4], q[5], q[6].

3. **State evolution**:
   - Initial: |0000000⟩
   - After X(q[0]), X(q[1]), X(q[2]): |1110000⟩ (all inputs set to |1⟩)
   - CNOT(q[0], q[3]): |1111000⟩ (q[3] = x0 = 1)
   - Toffoli(q[1], q[3], q[4]): |1111100⟩ (carry generated: q[4] = 1)
   - CNOT(q[1], q[3]): |1110100⟩ (q[3] = 1⊕1 = 0)
   - Toffoli(q[2], q[3], q[4]): |1110100⟩ (no carry since q[3]=0)
   - CNOT(q[2], q[3]): |1111100⟩ (q[3] = 0⊕1 = 1)

4. **Final state**: |1111100⟩. The sum of 1+1+1=3 in binary is 11, giving q[4]=1 (carry), q[3]=1 (sum).

5. **Measurements**: q[3]=1, q[4]=1, q[5]=0, q[6]=0 → bitstring |1100⟩ with probability 1.0.

## isqTrain/4042

- task_id: `isqTrain/4042`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1182`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```
import std;
// QPE with 3-bit precision for phase 6*pi/4
qbit q[4];

procedure main() {
    // Prepare eigenstate |1>
    X(q[3]);
    // Hadamard on precision qubits
    H(q[0]); H(q[1]); H(q[2]);
    // Controlled-U^(2^k) for each precision qubit
    ctrl Rz(2.0 * 2.0 * 3.14159265358979 * 6.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 6.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 6.0 / 8.0 * 4.0, q[2], q[3]);
    // Inverse QFT on 3 precision qubits
    // Swap q[0] <-> q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    // iQFT stages
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    ctrl Rz(-3.14159265358979 / 4.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 2.0, q[2], q[1]);
    H(q[2]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug:** In the first controlled-Rz gate, there is an extra factor of `2.0`, making the line read `2.0 * 2.0 * PI * 6.0 / 8.0 * 1.0` instead of `2.0 * PI * 6.0 / 8.0 * 1.0`. This doubles the rotation angle for the q[0]–q[3] controlled gate, producing an incorrect phase kickback.

**2. Fix:** Remove the duplicated `2.0` from the first `ctrl Rz` call so it matches the pattern `2.0 * PI * (6/8) * 2^k` with k=0.

**3. State evolution (corrected):**
- After X(q[3]): |0001⟩
- After H on q[0..2]: (|0⟩+|1⟩)³ ⊗ |1⟩ / 2√2
- Controlled-Rz gates apply phase θ = 2π·(6/8)·2^k to the |1⟩ component of each precision qubit. Since q[3] = |1⟩, phases 2π·6/8·{1,2,4} = {3π/2, 3π, 6π} are accumulated, yielding relative phases {3π/2, 3π ≡ π, 6π ≡ 0} mod 2π.
- The precision register state is (|0⟩ + e^{-i3π/2}|1⟩)⊗(|0⟩ + e^{-iπ}|1⟩)⊗(|0⟩ + |1⟩)/2√2 (up to global phase conventions).
- After swap and inverse QFT, the 3-bit output approximates the binary fraction 110₂ = 6/8, consistent with phase 6π/4.
- Expected measurements: {|1101⟩ ≈ 0.59, |1111⟩ ≈ 0.26, |1011⟩ ≈ 0.14, |1001⟩ ≈ 0.006}.

## isqTrain/555

- task_id: `isqTrain/555`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `interference`, `isq_syntax_arrays`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1451`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

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
    *   Task: Predict probability distribution of an isQ program.
    *   Input Program: A 3-qubit Deutsch-Jozsa algorithm variant.
    *   Format: "## Circuit Analysis" followed by step-by-step reasoning, ending with the probability distribution.
    *   Constraint: Concise (3-15 lines), Dirac notation, no code blocks.

2.  **Analyze the isQ Program:**
    *   `qbit q[3], anc;` -> 4 qubits. `q[0], q[1], q[2]` are input, `anc` is ancilla.
    *   `for i in 0:3 { H(q[i]); }` -> Applies H to `q[0], q[1], q[2]`. State is $|+\rangle|+\rangle|+\rangle|0\rangle = \frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle|0\rangle$.
    *   `X(anc); H(anc);` -> Transforms ancilla to $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. Total state: $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle|-\rangle$.
    *   `oracle g(3, 1) = [0, 0, 1, 1, 1, 1, 0, 0];` -> Phase oracle. It applies a phase of $(-1)^{g(x)}$ to $|x\rangle$ because the ancilla is in $|-\rangle$.
        *   $g(x) = 1$ for $x \in \{2,3,4,5\}$ (binary 010, 011, 100, 101).
        *   $g(x) = 0$ for $x \in \{0,1,6,7\}$ (binary 000, 001, 110, 111).
        *   Wait, let's carefully check standard isQ oracle semantics. `oracle g(3, 1)` takes 3 inputs and 1 output. It maps $|x\rangle|y\rangle \to |x\rangle|y \oplus g(x)\rangle$.
        *   If ancilla is $|-\rangle$, the state becomes $\frac{1}{\sqrt{8}} \sum (-1)^{g(x)} |x\rangle|-\rangle$.
        *   Let's verify $g(x)$: indices are $0$ to $7$. $g = [0, 0, 1, 1, 1, 1, 0, 0]$.
        *   So $(-1)^{g(x)}$ is $+1$ for $000, 001, 110, 111$ and $-1$ for $010, 011, 100, 101$.
    *   `for i in 0:3 { H(q[i]); }` -> Applies H to all 3 qubits again.
        *   The state before H-gates is $\frac{1}{\sqrt{8}} (|0\rangle + |1\rangle - |2\rangle - |3\rangle - |4\rangle - |5\rangle + |6\rangle + |7\rangle) |-\rangle$.
        *   Note that $|0\rangle=|000\rangle$, $|1\rangle=|001\rangle$, etc.
        *   Applying H to all 3 qubits again: $\sum_z (\frac{1}{8} \sum_x (-1)^{g(x) + x \cdot z}) |z\rangle$.
        *   We want the probability of measuring $|z\rangle$, which is $|\frac{1}{8} \sum_x (-1)^{g(x) + x \cdot z}|^2$.
        *   Let's check $z = 000$: $\frac{1}{8}(1+1-1-1-1-1+1+1) = 0$.
        *   Let's check $z = 110$ (which is 6): $\frac{1}{8} \sum_x (-1)^{g(x) + x \cdot 6}$.
            *   $x=000$: $(-1)^{0+0} = 1$
            *   $x=001$: $(-1)^{0+0} = 1$
            *   $x=010$: $(-1)^{1+1} = 1$
            *

### Reference answer

{'predicted_probs': {'6': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/177. Dimension: predict probabilities for reference circuit.'}

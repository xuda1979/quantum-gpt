# ISQ training COT RAG corpus: quantum_algorithms shard 130

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3637

- task_id: `isqTrain/3637`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2842`

### Prompt

Code this in isQ: the 4-qubit QFT applied to input state |0111>. The circuit should use Hadamard gates, controlled-Rz rotations with angles 2π/2^k, and final bit-reversal swaps. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning

Goal: Implement 4-qubit QFT on input state |0111⟩ and measure all qubits.

Four qubits q[0..3] are used, and all are measured.

**State evolution:**
1. Start with |0000⟩; apply X to q[1], q[2], q[3] → |0111⟩ (= |7⟩ in computational basis)
2. **QFT stage qubit 0:** H(q[0]) maps |1⟩→|−⟩; since q[1,2,3]=|1⟩, the controlled-Rz(π/2), Rz(π/4), Rz(π/8) all fire, accumulating phase on |1⟩ component of q[0]
3. **QFT stage qubit 1:** H(q[1]) maps |1⟩→|−⟩; controlled-Rz(π/2), Rz(π/4) from q[2,3] fire
4. **QFT stage qubit 2:** H(q[2]) maps |1⟩→|−⟩; controlled-Rz(π/2) from q[3] fires
5. **QFT stage qubit 3:** H(q[3]) maps |1⟩→|−⟩
6. **Bit-reversal swaps:** CNOT-based swaps exchange q[0]↔q[3] and q[1]↔q[

## isqTrain/2894

- task_id: `isqTrain/2894`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `874`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    Rz(1.5707963, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with the initial 1-qubit state |0>.
2. The Hadamard gate (H) puts the qubit into an equal superposition: (1/√2)|0> + (1/√2)|

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1199

- task_id: `isqTrain/1199`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5408`

### Prompt

帮我写一个isQ程序：implements the qaoa pattern with modified rotation parameters (num_pi4_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

This circuit implements a QAOA p=1 algorithm for MaxCut on a 2-node graph.
We use 2 qubits, both measured.
1. Initial state |00>.
2. H(q[0]); H(q[1]) creates a uniform superposition: (|00> + |01> + |10> + |11>) / 2 = |+>|+>.
3. CNOT(q[0], q[1]) transforms the basis. Since it maps |00>->|00>, |01>->|01>, |10>->|11>, |11>->|10>, the state becomes (|00> + |01> + |11> + |10>) / 2 = (|00> + |01> + |10> + |11>) / 2. Wait, the state in the Bell basis changes differently. Let's use coefficients.
Initial state: 0.5|00> + 0.5|01> + 0.5|10> + 0.5|11>.
CNOT(0,1) maps: |10> -> |11> and |11> -> |10>. So the state remains unchanged? Yes, H(0)H(1) is an eigenstate of CNOT (it maps |+>|+> to |+>|+>). Wait, actually CNOT|x>|+> = |+>|x ⊕ + >? No, CNOT|x>|y> = |x>|x ⊕ y>.
So CNOT |+>|+> = |+>( (0+1)/sqrt(2) + (1+0)/sqrt(2) ) = |+>|+>. Yes, CNOT on |+>|+> does nothing.
4. Rz(-pi/3, q[1]) applies e^(i*pi/6) to |0> and e^(-i*pi/6) to |1>. State becomes 0.5|00> + 0.5 e^(i*pi/3)|01> + 0.5|10> + 0.5 e^(i*pi/3)|11>.
5. CNOT(q[0], q[1]) maps |10>->|11> and |11>->|10>. State: 0.5|00> + 0.5 e^(i*pi/3)|01> + 0.5 e^(i*pi/3)|10> + 0.5|11>.
Wait, let's recalculate carefully.
Initial state: 1/2 (|00> + |01> + |10> + |11>)
CNOT(0,1): 1/2 (|00> + |01> + |11> + |10>) = 1/2 (|00> + |01> + |10> + |11>)
Rz(-pi/3, q[1]): |0> gets e^(i*pi/6), |1> gets e^(-i*pi/6).
Since the rotation is Rz(theta), the matrix is diag(e^{-i theta/2}, e^{i theta/2}).
Wait, Rz(-pi/3) matrix is diag(e^{i pi/6}, e^{-i pi/6}).
So applied to q[1]:
|00> -> e^{i pi/6} |00>
|01> -> e^{-i pi/6} |01>
|10> -> e^{i pi/6} |10>
|11> -> e^{-i pi/6} |11>
State: 1/2 (e^{i pi/6} |00> + e^{-i pi/6} |01> + e^{i pi/6} |10> + e^{-i pi/6} |11>).
Now CNOT(0,1):
|00> -> |00>
|01> -> |01>
|10> -> |11>
|11> -> |10>
State becomes: 1/2 (e^{i pi/6} |00> + e^{-i pi/6} |01> + e^{-i pi/6} |10> + e^{i pi/6} |11>)
Factor out e^{i pi/6} (global phase):
1/2 (|00> + e^{-i pi/3} |01> + e^{-i pi/3} |10> + |11>)
6. Rx(pi/3, q[0]) and Rx(pi/3, q[1]). Rx(pi/3) = cos(pi/6) I - i sin(pi/6) X = (sqrt(3)/2) I - (i/2) X.
So |0> -> sqrt(3)/2 |0> - i/2 |1>
|1> -> -i/

## isqTrain/2651

- task_id: `isqTrain/2651`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `global_phase`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2912`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;
qbit q[3];

procedure main() {
    // Put both input bits in uniform superposition
    H(q[0]);
    H(q[1]);
    // Evaluate bilinear form: f(x0,x1) = x0 AND x1
    // Toffoli gate computes the AND function
    Toffoli(q[0], q[1], q[2]);
    // Measure the result qubit
    M(q[2]);
}

```

程序B：
```isq
import std;
qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Put both input bits in uniform superposition
    H(q[0]);
    H(q[1]);
    // Evaluate bilinear form: f(x0,x1) = x0 AND x1
    // Toffoli gate computes the AND function
    Toffoli(q[0], q[1], q[2]);
    // Measure the result qubit
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes 3 qubits in |000⟩, applies H to q[0] and q[1] creating an equal superposition, and uses a Toffoli gate to compute the AND of q[0] and q[1] into q[2].
2. **Program B** performs the exact same operations but explicitly includes a `GPhase(0.0)` at the beginning of the circuit.
3. The `GPhase(0.0)` gate introduces a global phase factor of $e^{i \cdot 0} = 1$, which is an identity operation that leaves the quantum statevector mathematically unchanged.
4. Global phases do not affect quantum measurement probabilities.
5. Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/2708

- task_id: `isqTrain/2708`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_if_else`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1748`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

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

The problem asks for the output probability distribution of an isQ circuit implementing a Recursive Fourier Sampling (RFS) algorithm.
The output probability distribution is asked for the basis states from |0...0> to |1...1> for the measured qubits, or if only specific qubits are measured, we just need to list the probability of the outcome of `M(p[0])`.
Wait, the prompt says: "List the probability for every basis state in order from |0...0> to |1...1>."
But `int g = M(p[0]); print g;` only measures one qubit, `p[0]`.
the predicted output format in similar tasks is `{'0': P0, '1': P1}` or something similar depending on how many qubits are measured. If it's just one qubit, then `{'0': P0, '1': P1}`.
The implementation says: Expected measurement probabilities: `{'1': 1.0}`.

Let's trace the circuit.
This is a 1-level nested RFS? No, let's see the depth.
`recursive_fourier_sampling(0)`
`k=0`:
- `hadamard_layer(0)`: H(q[0]), H(q[1])
- `X(p[1])`
- `H(p[1])`
- `recursive_fourier_sampling(1)`
- `hadamard_layer(0)`: H(q[0]), H(q[1])
- `g(q[0],q[1], p[0])` -> This is an oracle, maps |x>|y> to |x>|y ^ g(x)>. `g` is `[0,1,1,0]`. So g(00)=0, g(01)=1, g(10)=1, g(11)=0.
- `hadamard_layer(0)`: H(q[0]), H(q[1])
- `recursive_fourier_sampling(1)`
- `hadamard_layer(0)`: H(q[0]), H(q[1])
- `H(p[1])`
- `X(p[1])`

Wait, what does `recursive_fourier_sampling(1)` do?
`k=1`:
- `hadamard_layer(1)`: H(q[2]), H(q[3])
- `X(p[2])`
- `H(p[2])`
- `recursive_fourier_sampling(2)`
- `hadamard_layer(1)`: H(q[2]), H(q[3])
- `g(q[2],q[3], p[1])`
- `hadamard_layer(1)`: H(q[2]), H(q[3])
- `recursive_fourier_sampling(2)`
- `hadamard_layer(1)`: H(q[2]), H(q[3])
- `H(p[2])`
- `X(p[2])`

What does `recursive_fourier_sampling(2)` do?
- `A(q[0], q[1], q[2], q[3], p[2])`
`A` is an oracle mapping |x>|y> to |x>|y ^ A(x)>.
`A` has truth table:
0000 -> 0
0001 -> 1
0010 -> 1
0011 -> 0
0100 -> 0
0101 -> 0
0110 -> 0
0111 -> 0
1000 -> 0
1001 -> 0
1010 -> 1
1011 -> 1
1100 -> 0
1101 -> 1
1110 -> 0
1111 -> 1

So the RFS circuit structure:
Level 2 function $f_2(x)$ is $A(x)$.
Level 1 function $f_1(x_0 x_1)$ is $g(x_0 x_1)$, which is $x_0 \oplus x_1$.
Wait, $g(00)=0, g(01)=1, g(10)=1, g(11)=0$. So $g(x) = x_0 \oplus x_1$.
Then RFS problem definition: The root level (level 0) output is $p_0$.
For RFS, the algorithm measures the answer to the root function, which is the hidden linear function.
Let's see if there is a simpler way. The algorithm is exactly the RFS quantum algorithm.
The RFS problem has a property that the output is exactly the hidden bit.
What is the hidden bit here?
Wait, the standard RFS algorithm outputs the solution to the problem.
Let's calculate the root hidden bit.
For RFS, the function $f_0$ is determined by the functions at lower levels.
Actually, let's trace just

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/20_principle_advantage

- task_id: `isqQA/quantum_algorithms/20_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `principle_advantage`, `algorithm`, `隐藏子群问题`
- source: `qa_pipeline`
- dataset_index: `3904`

### Prompt

请深入解析隐藏子群问题（Hidden Subgroup Problem, HSP）的核心原理。具体来说，在解决有限群上的HSP时，量子算法相比经典算法在时间复杂度上有哪些优势？其指数级量子加速的根本来源是什么？

### Reference answer

隐藏子群问题（HSP）是量子计算领域最核心的统一算法框架之一，许多著名的量子算法都是其在特定群结构上的具体实例。例如，Shor的大数分解算法（对应于有限阿贝尔群）和Simon算法（对应于群$\mathbb{Z}_2^n$）都可以归结为HSP。HSP的宏观原理如下：给定一个有限群 $G$ 以及一个黑盒函数 $f: G \to X$。该函数承诺在某个未知子群 $H \leq G$ 的同一个陪集上取值恒定，而在不同的陪集上取值不同。算法的目标是利用尽可能少的查询，求出生成子群 $H$ 所需的信息。

在时间复杂度对比与优势方面，经典计算面临极大的限制。对于一般的黑盒函数 $f$，如果一个经典算法想要提取出关于子群 $H$ 的信息，由于必须区分不同的陪集，其查询复杂度通常与群规模呈多项式甚至指数关系。特别是对于生成群 $G$ 所需比特数为 $n$ 的情况（即 $|G| = 2^n$），经典算法大概率需要进行 $\Theta(\sqrt{|G|}) = \Theta(2^{n/2})$ 次查询（如利用生日悖论），其时间复杂度是指数级的。而在量子计算框架下，对于所有的有限阿贝尔群以及部分特殊的非阿贝尔群（如二面体群），量子算法求解HSP的时间复杂度和查询复杂度仅为 $O(\text{poly}(n))$，即多项式时间。这就实现了从经典指数级复杂度到量子多项式级复杂度的跨越，展现出了极其强大的指数级加速优势。

这种指数级量子加速的根本来源，在于量子态的叠加性质与群上精心设计的**量子傅里叶变换** 所产生的干涉效应。量子算法首先通过制备群元素的等幅叠加态，并查询Oracle得到包含隐藏子群信息的陪集态：$|x\rangle |f(x)\rangle$。通过丢弃第二寄存器（或对其进行测量），第一寄存器将坍缩为子群 $H$ 某个陪集的均匀叠加态。此时，关键步骤在于对第一寄存器施加群 $G$ 上的量子傅里叶变换。QFT能够将陪集态在群的特征标基矢下展开，由于干涉相消，那些与 $H$ 非正交的特征标对应的概率幅会变为零，而所有概率幅会高度集中在与 $H$ 正交的特征标上。这意味着，对经过QFT后的量子态进行测量，将以极高的概率投影出属于 $H$ 的正交补 $H^\perp$ 中的元素。量子算法通过极少次的测量就能获得 $H^\perp$ 的生成元，随后再借助经典的多项式时间算法（如求解线性方程组或求格基），就能轻松反推出隐藏子群 $H$ 的结构。简而言之，QFT作为一个全局的线性操作，在频域（特征标空间）中精准地“过滤”并放大了隐藏的群结构对称性信息，从而实现了对经典算法的降维打击。

## isqTrain/1097

- task_id: `isqTrain/1097`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2650`

### Prompt

Implement the following in isQ: implements the bernstein_vazirani pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze the Bernstein-Vazirani algorithm and the given isQ code.

The Bernstein-Vazirani algorithm finds a hidden string s by making a single query to an oracle that computes f(x) = s·x mod 2.

Let me trace through the circuit:

1. Initial state: |000>|1> (after preparing ancilla with X)

Wait, let me re-read. The ancilla starts in |0>, then X(anc[0]) makes it |1>, then H(anc[0]) makes it |->.

The input qubits start in |000>, then H on all three makes |+++>.

2. After Hadamards on input: (1/2√2)(|000>+|001>+|010>+|011>+|100>+|101>+|110>+|111>) ⊗ |->

The oracle f computes f(x) = x[0] XOR x[2] (since s = 101, the inner product s·x = x[0]·1 XOR x[1]·0 XOR x[2]·1 = x[0] XOR x[2]).

The oracle applies a phase based on f(x): if f(x) = 1, it flips the ancilla in the |-> basis, which applies a -1 phase.

3. After oracle: States where x[0] XOR x[2] = 1 get a -1 phase. This means the state becomes:
(1/2√2)(|000> - |001> + |010> - |011> - |100> + |101> - |110> + |111>) ⊗ |->

Wait, let me be more careful. s = 101, so s·x = x[0]·1 + x[1]·0 + x[2]·1 mod 2 = x[0] + x[2] mod 2.

x=000: 0+0=0 → no phase
x=001: 0+1=1 → -1 phase
x=010: 0+0=0 → no phase
x=011: 0+1=1 → -1 phase
x=100: 1+0=1 → -1 phase
x=101: 1+1=0 → no phase
x=110: 1+0=1 → -1 phase
x=111: 1+1=0 → no phase

So after oracle:
(1/2√2)(|000> - |001> + |010> - |011> - |100> + |101> - |110> + |111>) ⊗ |->

4. After Hadamard on all input qubits:
H^{⊗3} on the input register gives s = 101 = |101>.

This is because H^{⊗n} applied to the state (-1)^{s·x}|x> gives |s>.

So we get |101> ⊗ |->.

5. Then X(q[0]) twice (which cancels to identity, but they're both applied):
X X = I, so the state remains |101> ⊗ |->.

6. Measurement of q[0], q[1], q[2] yields 101 with probability 1.

In the --probs output, earlier measured qubit = higher bit. So if we measure q[0], q[1], q[2] in that order:
- q[0] is the highest bit
- q[1] is the middle bit
- q[2] is the lowest bit

q[0] = 1, q[1] = 0, q[2] = 1 → bitstring = 101 in binary = 5.

So the probability of |101> (or bitstring 5) is 1.0.

Now let me write the reasoning:

## Reasoning
Goal: Find hidden string s=101 via Bernstein-Vazirani with a single oracle query.

Qubits: 3 input q[0..2] (measured) + 1 ancilla anc[0].

State evolution:
- Init: |000>|0> → X(anc): |000>|1> → H(anc): |000>|-> → H(q[0..2]): |+++>|-> = H^{⊗3}|000>|-> = uniform superposition over all |x>|->.
- Oracle f(x)=x[0]⊕x[2]: applies phase (-1)^{f(x)} to each |x>, yielding (1/2√2)Σ_x (-1)^{x[0]⊕x[2]}|x>|->.
- H(q[0..2]): H^{⊗3} decodes the phase pattern into the computational basis state |s>=|101>,

## isqTrain/3977

- task_id: `isqTrain/3977`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `1872`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// Grover search on 3 qubits targeting |010>
qbit q[3];

// Oracle: mark target state |010>
unit grover_oracle(qbit q[3]) {
    // BUG: missing gate here
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[2]);
    X(q[0]);
} deriving gate

// Diffusion operator (inversion about mean)
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

// Main: 1 Grover iteration
procedure main() {
    // Initialize uniform superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Apply oracle + diffusion
    grover_oracle(q);
    grover_diffusion(q);
    // Measure all qubits
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

The user wants me to analyze a bug in an isQ quantum program.
The program implements a 3-qubit Grover search targeting |010>.

Buggy code:
Oracle part:

Wait, the buggy code has `X(q[2]);` then `ctrl CZ(q[0], q[1], q[2]);`, then `X(q[2]);`, then `X(q[0]);`.
Wait, The corrected version:

The bug is a missing `X(q[0]);` at the beginning of the oracle.
Let's see: to mark |010>, the oracle applies a phase flip to |010>.
This is typically done by applying X gates to qubits that are 0 in the target state, then a controlled-Z (or Toffoli-like Z) on all qubits, then uncompute the X gates.
For target |010>:
q[0] is 0 -> apply X(q[0])
q[1] is 1 -> do nothing
q[2] is 0 -> apply X(q[2])
Then apply `ctrl CZ(q[0], q[1], q[2])` which applies a Z gate on q[2] conditioned on q[0] and q[1] being |1>. Wait, in isQ, `ctrl CZ(q[0], q[1], q[2])` might mean controlled-CZ. The control is `@[q[0], q[1]]`? No, `ctrl CZ(q[0], q[1], q[2])` might be a syntax error in standard isQ or it means `ctrl CZ` with `q[0], q[1]`? Ah, wait. `ctrl CZ(q[0], q[1], q[2])` probably means it's a multi-controlled gate. Actually, wait, standard isQ has Toffoli or similar. The correct code given has `ctrl CZ(q[0], q[1], q[2]);` which might mean a doubly controlled CZ, which is equivalent to a Toffoli but with Z instead of X. Wait, CZ has two qubits. `ctrl CZ(q[0], q[1], q[2])` means q[0] controls CZ(q[1], q[2]), so it's a Z gate on q[2] conditioned on q[0] and q[1]. Wait, CZ applies Z to target when control is 1. Controlled-CZ applies Z to target when both controls are 1. Which means it applies a phase of -1 to |111>.

If we want to apply -1 phase to |010>:
We map |010> to |111> using X gates.
q[0] in |010> is 0. Apply X -> 1.
q[1] in |010> is 1. No X -> 1.
q[2] in |010> is 0. Apply X -> 1.
So we need X(q[0]) and X(q[2]) before the multi-controlled Z.
Then the multi-controlled Z applies -1 phase to |111> (which corresponds to |010>).
Then we uncompute X(q[0]) and X(q[2]).

The buggy code was missing the `X(q[0]);` before `X(q[2]);`.
Wait, the buggy code had `X(q[2])`, `ctrl CZ(...)`, `X(q[2])`, `X(q[0])`.
Since it was missing `X(q[0])` at the beginning, it applied X to q[2], then controlled CZ (which applies phase to |110>), then uncomputes.
This would target |110> instead of |010>.

So the bug is the missing `X(q[0]);` at the beginning of `grover_oracle`.
The fix is adding `X(q[0]);` at the beginning of the oracle.

1. What the bug is:
The `grover_oracle` is missing an `X(q[0])` gate at the beginning of its definition. The oracle is intended to flip the phase of the target state |010>, which requires changing the |0> bits to |1> using X gates so that the target state becomes |111>, which is then flipped by the multi-controlled Z gate

## isqQA/quantum_algorithms/102_hardware_limitations

- task_id: `isqQA/quantum_algorithms/102_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hardware_limitations`, `algorithm`, `Grover算法在3-4量子比特上的实现`
- source: `qa_pipeline`
- dataset_index: `3020`

### Prompt

在当前的NISQ（含噪声中等规模量子）设备上实现Grover算法时，退相干和量子门误差是如何限制算法成功率的？请从理论上分析由于T1（纵向弛豫）和T2（横向退相干）时间导致的保真度衰减，并给出一个在3个量子比特上实现单目标Grover搜索（目标态为|111〉）的isQ代码示例，同时说明在实际硬件上运行此电路时可能遇到的主要瓶颈。

### Reference answer

<think_

1. **保真度衰减的理论推导**：在NISQ设备中，量子比特的状态会受到环境噪声的干扰。假设量子比特处于叠加态，其随时间演化的保真度主要受制于退相干时间。纵向弛豫时间 T1 描述了量子比特从激发态 |1〉 衰减到基态 |0〉 的能量损失过程；横向退相干时间 T2 描述了量子比特丢失相位信息的过程。
2. **衰减公式**：经过时间 t 后，量子态的保真度 F(t) 可以近似表示为：
   F(t) ≈ (1/2)(1 + e^{-t/T1}) e^{-t/T2}
   由于 T2 通常远小于 2*T1，相位退相干往往是限制量子算法深度的主要因素。
3. **Grover算法的门耗分析**：对于3比特系统（N=3，目标态数量M=1），理论上需要约 R ≈ π/4 * √(2^N) = π/4 * √8 ≈ 2.2 次迭代才能达到最大振幅。但每次Grover迭代需要实现相位翻转和扩散算子，这两步均包含多控门（如Toffoli门）。在硬件底层，一个Toffoli门通常需要分解为6个CNOT门和多个单比特门。假设每个CNOT耗时约 20-50 ns，单比特门约 10-20 ns。单次迭代的电路深度可能导致总执行时间 t 接近甚至超过当前超导量子硬件的 T2 时间（通常在 50-100 μs 左右）。
4. **硬件瓶颈结论**：当增加Grover迭代次数时，由于电路深度增加，t 增大，导致 e^{-t/T2} 趋近于0，算法的保真度将急剧下降。因此，在真实的NISQ设备上，强行运行理论最优的多次迭代反而会导致测量结果的概率分布接近于均匀分布的噪声。通常只能采取“浅层电路”策略，即只运行1次迭代以规避深度退相干。

_
>在NISQ设备上运行Grover算法时，量子硬件的物理局限性是制约算法表现的核心因素。实际的量子系统并非完全封闭，量子比特会与环境发生耦合，导致信息丢失。这主要通过两个时间常数来衡量：T1（能量弛豫时间）和T2（相位退相干时间）。假设算法的电路执行总时间为 t，系统的平均保真度衰减可理论近似为：
F(t) ≈ (1/2)(1 + e^{-t/T1}) e^{-t/T2}
由于在当前主流的超导量子平台中，T2通常远小于T1，因此相位退相干是破坏量子叠加态和干涉过程（Grover算法中扩散算子的核心）的致命因素。

对于3到4个量子比特的Grover算法，虽然理论上需要的迭代次数较少（3比特约2次，4比特约3次），但其代价是多控门（如Toffoli门）的引入。在硬件层面，多控门无法直接执行，必须分解为大量的双比特门（如CNOT）和单比特门。随着迭代次数增加，电路深度呈线性甚至指数级增长，导致执行时间 t 迅速增加。当 t 接近或超过 T2 时，量子态的相位关系将被彻底破坏，此时算法的测量结果将不再收敛于目标态，而是退化为均匀噪声。

由于NISQ设备的门错误率（特别是双比特门错误率往往在1%左右）也会随着门数量线性累积，在实际硬件上强行运行理论最优的迭代次数往往会导致极低的成功率。因此，实验物理学家通常采取仅运行单次迭代的折中方案。以下代码展示了在3个量子比特上寻找目标态 |111〉 的Grover算法（仅包含1次迭代），通过限制电路深度来对抗退相干影响：

import std;

qbit q[3];

procedure main() {
    // 步骤1：初始化，将所有量子比特置于均匀叠加态
    for i in 0:3 {
        H(q[i]);
    }

    // 步骤2：Oracle - 标记目标态 |111〉
    // 使用H门包裹Toffoli门，将控制相位翻转转化为多控X门操作
    H(q[2]);
    Toffoli(q[0], q[1], q[2]);
    H(q[2]);

    // 步骤3：Diffusion operator (扩散算子)
    // 翻转关于平均值的振幅
    for i in 0:3 {
        H(q[i]);
        X(q[i]);
    }
    
    H(q[2]);
    Toffoli(q[0], q[1], q[2]);
    H(q[2]);
    
    for i in 0:3 {
        X(q[i]);
        H(q[i]);
    }

    // 注意：这里仅执行了1次Grover迭代。
    // 在真实的NISQ硬件上，如果再增加一组相同的迭代模块，
    // 累积的门噪声和退相干效应将会使得最终测量的正确率大幅下降。
}

## isqTrain/780

- task_id: `isqTrain/780`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2164`

### Prompt

帮我写一个isQ程序：implements the gf2_multiplication pattern but with a different initial state preparation (flip q[[0, 1]] -> q[2]).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement GF(2) multiplication (AND) where target qubit q[2] is initialized to |1⟩ while inputs q[0], q[1] remain |0⟩.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]); only q[2] is measured.
3. **State evolution**:
   - Initial: |000⟩
   - After X(q[2]): |001⟩
   - Toffoli(q[0], q[1], q[2]): Requires both controls |1⟩ to flip target; since q[0]=|0⟩, q[1]=|0⟩, no action → state remains |001⟩
4. **Result**: q[2] is in state |1⟩ with probability 1.0, since the Toffoli gate doesn't activate when either control is |0⟩.

# ISQ training COT RAG corpus: quantum_frontier shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/front/30

- task_id: `isqExpand/front/30`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `quantum_ml`, `data_reuploading`, `variational`
- source: `isq_expansion`
- dataset_index: `272`

### Prompt

I need an isQ program to implements a 2-qubit variational circuit with re-uploading (data re-encoding between layers).

Data re-uploading encodes classical data multiple times in the circuit, increasing expressibility.

Requirements:
- Declare global `qbit q[2];`
- Layer 1: Ry(pi/3.0, q[0]), Ry(pi/4.0, q[1]), CNOT(q[0],q[1]).
- Layer 2 (re-upload): Ry(pi/6.0, q[0]), Ry(pi/5.0, q[1]), CNOT(q[1],q[0]).
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Data re-uploading applies rotation gates encoding classical features multiple times throughout the circuit, interleaved with entangling layers. This increases the circuit's expressibility beyond what a single encoding layer achieves. The alternating CNOT directions further enhance the entanglement structure.

## isqExpand/front/26

- task_id: `isqExpand/front/26`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `quantum_ml`, `variational_circuit`, `entangling_layer`
- source: `isq_expansion`
- dataset_index: `5454`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```isq
import std;
qbit q[2];

procedure main() {
    // Layer 1: rotation
    Ry(pi/4.0, q[0]);
    Ry(pi/3.0, q[1]);
    // Layer 1: entangle
    CNOT(q[0], q[1]);
    // Layer 2: rotation
    Ry(pi/6.0, q[0]);
    Ry(pi/5.0, q[1]);
    // Layer 2: entangle — BUG: same direction as layer 1
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Reasoning
In variational quantum circuits, alternating the direction of CNOT gates between layers increases the circuit's expressibility. The buggy code uses CNOT(q[0],q[1]) in both layers. The fix changes layer 2's CNOT to CNOT(q[1],q[0]), making q[1] the control and q[0] the target.

## isqExpand/front/118

- task_id: `isqExpand/front/118`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `quantum_walk`, `output_prediction`, `coin_flip`, `conditional_shift`
- source: `isq_expansion`
- dataset_index: `2008`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[3];

procedure main() {
    // Set initial position to 2 (binary 10)
    X(q[1]);
    // Coin flip
    H(q[0]);
    // Conditional shift: coin=1 -> increment position
    CNOT(q[0], q[2]);
    // Conditional shift: coin=0 -> decrement position
    X(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    X(q[0]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[1]): |000⟩ → |010⟩ (position = |10⟩ = 2)
2. H(q[0]): (|010⟩ + |110⟩)/√2
3. CNOT(q[0], q[2]): |010⟩ stays, |110⟩ → |111⟩ (increment)
4. X(q[0]): |010⟩→|110⟩, |111⟩→|011⟩
5. CNOT(q[0], q[1]): |110⟩→|100⟩, |011⟩ stays
6. CNOT(q[0], q[2]): |100⟩→|101⟩, |011⟩ stays
7. X(q[0]): |101⟩→|001⟩, |011⟩→|111⟩

Final: (|001⟩ + |111⟩)/√2
P(|001⟩)=0.5 (position 1), P(|111⟩)=0.5 (position 3).

### Reference answer

{'predicted_probs': {'0': 0.0, '1': 0.5, '2': 0.0, '3': 0.0, '4': 0.0, '5': 0.0, '6': 0.0, '7': 0.5}, 'explanation': 'Initial state: |0⟩|10⟩ (coin=0, position=2). After H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |10⟩ = (|010⟩+|110⟩)/√2. CNOT(q[0],q[2]) flips q[2] when coin=1: (|010⟩+|111⟩)/√2. Then X(q[0]) flips coin for decrement logic. CNOT(q[0],q[1]) and CNOT(q[0],q[2]) apply when inverted-coin=1 (original coin=0): |010⟩ → |000⟩ → |001⟩. For coin=1 branch: inverted-coin=0, no change, stays |111⟩. X(q[0]) restores coin. Final: (|001⟩+|111⟩)/√2. Outcome |001⟩ (coin=0, position=01=1) and |111⟩ (coin=1, position=11=3) each with probability 0.5. The walker moves from position 2 to a superposition of positions 1 and 3.'}

## isqExpand/front/41

- task_id: `isqExpand/front/41`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `hamiltonian_simulation`, `zz_interaction`, `phase`
- source: `isq_expansion`
- dataset_index: `4099`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[2];

procedure main() {
    // ZZ interaction on |10>
    X(q[0]);
    CNOT(q[0], q[1]);
    Rz(pi, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Reasoning
1. X(q[0]) -> |10⟩.
2. CNOT(q[0],q[1]): control=1, flip q[1] -> |11⟩.
3. Rz(pi, q[1]): on q[1]=|1⟩, applies e^{i*pi/2}=i phase. State: i|11⟩. Wait, Rz(theta)|1⟩ = e^{i*theta/2}|1⟩. So Rz(pi)|1⟩ = e^{i*pi/2}|1⟩ = i|1⟩. State: i|11⟩.
4. CNOT(q[0],q[1]): flip q[1] back -> i|10⟩.
5. Global phase i unobservable. P(|10⟩) = 1.0. Index = 2.

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Start |10>. CNOT(q[0],q[1]): q[0]=1 flips q[1] -> |11>. Rz(pi,q[1]): applies phase e^{-i*pi/2}=-i to |1> component of q[1]. State: -i|11>. CNOT(q[0],q[1]): q[0]=1 flips q[1] back -> -i|10>. Global phase -i is unobservable. P(|10>)=1.0. Index 2.'}

## isqExpand/front/73

- task_id: `isqExpand/front/73`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `E91`, `QKD`, `entanglement`, `Bell_inequality`, `quantum_cryptography`
- source: `isq_expansion_qa`
- dataset_index: `1592`

### Prompt

请解释E91量子密钥分发协议（Ekert 1991）的原理。E91与BB84有哪些关键区别？纠缠态在E91协议中扮演什么角色？贝尔不等式如何用于E91的窃听检测？

### Chain-of-thought reasoning

## 推理
目标：对比E91与BB84，突出纠缠和Bell不等式的作用。

E91核心创新：用纠缠对替代单光子制备。安全性来源从不可克隆定理扩展到纠缠单一性和Bell不等式违反。

Bell不等式S=2*sqrt(2)表明纠缠完好；Eve的介入会降低S值（因为纠缠被分享给三方），这提供了设备无关的安全性证明基础。

### Reference answer

## E91量子密钥分发协议

### 协议原理
E91协议（Ekert 1991）利用量子纠缠态进行密钥分发，核心思想是：共享最大纠缠Bell态的两个粒子，在相同基底测量时结果完美关联。

### 工作流程

**第一步：纠缠源分发**
一个纠缠源产生Bell态 |Phi+⟩ = (|00⟩ + |11⟩)/sqrt(2)，将两个粒子分别发送给Alice和Bob。

**第二步：随机基底测量**
Alice从3个基底中随机选择：{0, pi/8, pi/4}
Bob从3个基底中随机选择：{0, pi/8, -pi/8}

- 当Alice和Bob选择相同基底（0）时：测量结果完美关联，用于生成密钥
- 当选择不同基底时：测量结果用于计算Bell参数S

**第三步：贝尔不等式检验**
使用CHSH不等式：S = E(a1,b1) - E(a1,b3) + E(a3,b1) + E(a3,b3)
- 量子力学预言：S = 2*sqrt(2) 约等于 2.828（违反经典极限|S|<=2）
- 若S = 2*sqrt(2)：纠缠态完好，无窃听
- 若S < 2*sqrt(2)：纠缠被破坏，存在窃听

### 与BB84的关键区别

| 特征 | BB84 | E91 |
|------|------|-----|
| 量子资源 | 单光子 | 纠缠对 |
| 信息载体 | 态的制备 | 测量关联 |
| 窃听检测 | 错误率分析 | Bell不等式违反 |
| 安全证明 | 基于不可克隆 | 基于纠缠单一性 |
| 纠缠源位置 | 不需要 | 可在Alice、Bob或中间 |

### 纠缠的角色
1. **密钥生成**：Bell态的完美关联提供共享随机性
2. **安全保障**：纠缠单一性（monogamy of entanglement）——如果Alice和Bob的粒子最大纠缠，则与Eve的纠缠为零
3. **窃听检测**：任何截获都会破坏纠缠，降低Bell参数值

### isQ中的Bell对制备
```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    // 现在 q[0]和q[1]处于|Phi+⟩ = (|00⟩+|11⟩)/sqrt(2)
    M(q[0]); M(q[1]);
}
```
结果：|00⟩和|11⟩各50%概率，完美关联。

## isqExpand/front/145

- task_id: `isqExpand/front/145`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `e91_protocol`, `bell_pair`, `entanglement`, `quantum_key_distribution`, `correlated_measurement`
- source: `isq_expansion`
- dataset_index: `4220`

### Prompt

I need an isQ program to implementing the core of the E91 protocol. Create a Bell pair (|00⟩+|11⟩)/√2 shared between Alice (qubit 0) and Bob (qubit 1). Both parties measure their qubit in the computational (Z) basis. The measurement outcomes must be perfectly correlated, yielding |00⟩ and |11⟩ with equal probability.

### Chain-of-thought reasoning

Step 1: The E91 protocol relies on sharing an entangled Bell state between two parties, Alice and Bob. Step 2: We create the Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2 by applying H to q[0] (putting it in superposition) then CNOT(q[0], q[1]) (entangling). Step 3: After this circuit the state vector is (1/√2)|00⟩ + (1/√2)|11⟩. Step 4: When both qubits are measured in the Z basis the joint probabilities are P(00)=0.5, P(01)=0.0, P(10)=0.0, P(11)=0.5. Step 5: The nonzero outcomes 00 and 11 have identical bit values, confirming perfect (positive) correlation — the hallmark of the E91 entanglement-based QKD scheme. The expected_probs array is [0.5, 0.0, 0.0, 0.5] for 2 measured qubits.

## isqExpand/front/135

- task_id: `isqExpand/front/135`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `vqe`, `ansatz`, `h2_molecule`, `hartree_fock`, `single_excitation`, `parameterized_circuit`
- source: `isq_expansion`
- dataset_index: `5358`

### Prompt

Code this in isQ: implementing a VQE ansatz circuit for the H2 molecule (2 qubits). The circuit should: (1) Prepare the Hartree-Fock reference state |01⟩ by applying X to q[1]. (2) Apply CNOT(q[0], q[1]) for entanglement. (3) Apply an Ry rotation Ry(PI/2, q[0]) representing the single-excitation parameterized rotation. Use global qbit declaration with q[2].

### Chain-of-thought reasoning

Step 1: Start with initial state |00⟩. Step 2: Apply X(q[1]) to prepare the HF state |01⟩. Step 3: Apply CNOT(q[0], q[1]) — since q[0] is |0⟩, the control is inactive, so the state remains |01⟩. Step 4: Apply Ry(PI/2, q[0]) to qubit 0. The Ry(θ) gate maps |0⟩ → cos(θ/2)|0⟩ + sin(θ/2)|1⟩. With θ = π/2, this becomes cos(π/4)|0⟩ + sin(π/4)|1⟩ = (1/√2)|0⟩ + (1/√2)|1⟩. The full state becomes (1/√2)|01⟩ + (1/√2)|11⟩. Probabilities: P(|00⟩)=0, P(|01⟩)=cos²(π/4)=0.5, P(|10⟩)=0, P(|11⟩)=sin²(π/4)=0.5.

## isqExpand/front/114

- task_id: `isqExpand/front/114`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `nisq_limitations`, `circuit_depth`, `variational_circuit`, `noise_accumulation`
- source: `isq_expansion`
- dataset_index: `183`

### Prompt

帮我写一个isQ程序：demonstrates a deep variational circuit typical of NISQ computations. The circuit uses 4 layers of parameterized rotations and entanglement, illustrating how circuit depth accumulates in variational algorithms.

Requirements:
- Declare global `qbit q[2];`
- Apply 4 sequential layers. Each layer l (l=0,1,2,3) consists of:
  - Ry(pi/(3.0+l), q[0]) and Ry(pi/(4.0+l), q[1]) — diminishing rotation angles per layer.
  - CNOT(q[0], q[1]) — entangling gate.
- Specifically: Layer 0: Ry(pi/3.0), Ry(pi/4.0). Layer 1: Ry(pi/4.0), Ry(pi/5.0). Layer 2: Ry(pi/5.0), Ry(pi/6.0). Layer 3: Ry(pi/6.0), Ry(pi/7.0).
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate NISQ circuit depth with a 4-layer variational circuit.

4 layers of Ry + CNOT accumulate rotations:
- Layer 0: Ry(60°, q[0]), Ry(45°, q[1]), CNOT
- Layer 1: Ry(45°, q[0]), Ry(36°, q[1]), CNOT
- Layer 2: Ry(36°, q[0]), Ry(30°, q[1]), CNOT
- Layer 3: Ry(30°, q[0]), Ry(~25.7°, q[1]), CNOT

Total circuit depth is 12 gates. On ideal hardware: P(|10⟩) = 0.771 dominates.
On NISQ devices with ~0.5% 2-qubit gate error, 4 CNOTs introduce ~2% accumulated error.

## isqExpand/front/98

- task_id: `isqExpand/front/98`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `basic`
- concept_tags: `qaoa`, `superposition`, `basis_change`
- source: `isq_expansion`
- dataset_index: `4881`

### Prompt

Help me write isQ code that implements the QAOA mixer layer on 3 qubits. The mixer unitary is e^{-i*beta*sum(X_i)} which decomposes into Rx(2*beta) on each qubit independently.

Use beta = pi/6 (so each qubit gets Rx(pi/3)). Start from the |000> state and apply the mixer layer, then measure all qubits.

This demonstrates how the transverse-field mixer drives transitions between computational basis states.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply QAOA mixer Rx(2*beta=pi/3) to 3 qubits starting from |000>.

Since the mixer acts independently on each qubit:
Rx(pi/3)|0> = cos(pi/6)|0> - i*sin(pi/6)|1>
P(|0>) = cos^2(pi/6) = 3/4 = 0.75
P(|1>) = sin^2(pi/6) = 1/4 = 0.25

For 3-qubit product state, probability of |abc> = P_a * P_b * P_c:
|000>: 0.75^3 = 0.4219
|001>: 0.75^2 * 0.25 = 0.1406
|010>: 0.75^2 * 0.25 = 0.1406
|011>: 0.75 * 0.25^2 = 0.0469
|100>: same as |001> = 0.1406
|101>: same as |011> = 0.0469
|110>: same as |011> = 0.0469
|111>: 0.25^3 = 0.0156

## isqExpand/front/99

- task_id: `isqExpand/front/99`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `qaoa`, `max_cut`, `phase_manipulation`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `2681`

### Prompt

Write an isQ program that implementing a 1-layer QAOA circuit for the Max-Cut problem on a triangle graph (3 nodes, edges: (0,1), (1,2), (0,2)). Use gamma = pi/3 for the cost layer and beta = pi/4 for the mixer layer.

The circuit structure is:
1. Initialize all 3 qubits in |+> using Hadamard gates.
2. Cost layer: Apply ZZ interaction (CNOT-Rz(2*gamma)-CNOT) for each of the 3 edges.
3. Mixer layer: Apply Rx(2*beta) to each qubit.
4. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: QAOA on triangle graph K3 with gamma=pi/3, beta=pi/4.

Cost Hamiltonian: H_C = Z_0Z_1 + Z_1Z_2 + Z_0Z_2.
For the triangle, Max-Cut solutions cut exactly 2 edges (all 6 non-trivial states).

Circuit:
1. H^{\otimes 3}: uniform superposition over 8 states.
2. Three ZZ interactions (one per edge), each with gamma=pi/3.
   - Each ZZ applies phase e^{-i*gamma} to same-parity pairs, e^{+i*gamma} to opposite-parity.
   - For |000> and |111>: all 3 edges same-parity -> total phase e^{-3i*gamma}.
   - For optimal cuts (e.g., |001>): 1 same + 2 opposite -> total phase e^{i*gamma}.
3. Mixer Rx(pi/2) on each qubit.

Numerical result: P(|000>)=P(|111>)=0.4062, P(others)=0.0313 each.
With these parameters, QAOA does not concentrate on optimal cuts (would need tuning).

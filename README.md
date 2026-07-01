# 量智V0.2.0 - Qwen3.6-35B 量子计算科学模型

量智V0.2.0 是基于 Qwen3.6-35B 微调的量子计算科学专业模型，面向量子计算、量子信息、量子算法、量子线路、量子模拟和量子编程等科研与工程场景。相比 V0.1.0 的本地 RAG 版本，V0.2.0 的核心升级是模型本体能力增强：在更大的 Qwen3.6-35B 基座上，通过量子计算科学数据进行专项微调，使模型更适合解释专业概念、分析量子线路、推导算法步骤、辅助阅读论文，并生成或审查量子计算相关代码。

## 模型信息

- 模型名称：`量智V0.2.0`
- 基座模型：`Qwen3.6-35B`
- 训练方式：基于量子计算科学与量子编程数据进行微调
- 主要语言：中文、英文
- 主要方向：量子计算科学问答、量子算法理解、量子线路分析、量子编程辅助、科研文档辅助
- 推荐用途：教学、科研辅助、方案分析、实验设计、论文理解、算法原型开发

## V0.2.0 更新亮点

- 基座模型从 V0.1.0 使用的 Qwen3.6-27B 链路升级为 Qwen3.6-35B 微调模型。
- 模型定位从“本地文档检索增强问答”升级为“量子计算科学专业模型”。
- 增强对量子力学基础、量子信息、量子门、量子线路、量子算法、量子纠错和量子模拟等主题的理解。
- 优化专业术语表达、公式解释、算法步骤推导和科研问答的一致性。
- 提升量子编程任务中的代码生成、代码解释、API 使用建议和测试用例构造能力。

## 适用场景

- 量子计算基础概念解释，例如量子态、测量、纠缠、叠加、幺正演化和密度矩阵。
- 量子算法学习与分析，例如 Grover 搜索、量子相位估计、QFT、VQE、QAOA、HHL 和 Shor 算法。
- 量子线路分析与说明，例如门序列解释、测量结果分析、线路等价变换和常见错误排查。
- 量子编程辅助，例如 Qiskit、Cirq、PennyLane、CUDA-Q、OpenFermion、QuTiP 等框架的示例代码、测试和调试建议。
- 科研辅助写作，例如论文段落解释、实验方案梳理、术语统一、技术报告和评测说明。

## 量子代码生成评测问题

下面问题来自仓库中的量子 hard holdout 和可执行评测契约，适合直接作为提示词输入模型，用来对比量智V0.2.0 与未经过量子计算科学微调的通用 Qwen3.5-35B。每一题都要求模型编写可运行的量子计算 Python 代码，而不是只解释概念；通用基座模型在这类题上常见失败包括只给文字解释、漏实现指定函数、矩阵索引错误、复数相位符号错误、归一化不守恒或混淆量子协议映射。

统一提问格式建议：

```text
请编写一个完整的 Python 模块，实现题目要求的函数。只输出代码，不要输出解释、Markdown 或伪代码。代码必须能被单元测试直接 import，并且不能依赖题目没有声明的外部量子库。
```

1. 量子相位估计

```text
请编写一个完整的 Python 模块，实现两个函数：phase_estimation(eigenvalue_phase, n_counting_bits) 和 phase_from_measurement(measurement, n_counting_bits)。phase_estimation 要模拟量子相位估计中把本征相位映射到 n 个 counting qubits 的测量整数，返回范围必须在 [0, 2**n_counting_bits - 1]。必须满足：phase_estimation(0.25, 3)=2，phase_estimation(0.75, 4)=12，phase_estimation(1/3, 3)=3；对 0.0、0.25、0.5、0.75、0.125 这些精确相位，phase_estimation 后再用 phase_from_measurement 恢复必须得到原相位；phase_estimation(0.999, 3) 也必须保持在 [0, 7]。只输出 Python 代码。
```

2. Grover 搜索的 oracle 和 diffusion 算子

```text
请编写一个完整的 Python 模块，用状态向量实现 Grover 搜索，必须实现 uniform_superposition(n_qubits)、oracle(state, marked)、diffusion(state)、grover_search(n_qubits, marked, iterations)。oracle 只能翻转 marked 状态的振幅符号；diffusion 必须实现关于平均振幅的反演，因此 diffusion([0.5,0.5,0.5,-0.5]) 必须返回 [0,0,0,1]。grover_search(2, marked=3, iterations=1) 中 marked 态概率必须为 1.0；grover_search(3, marked=5, iterations=2) 中 marked 态概率必须大于 0.94，并保持状态归一化。只输出 Python 代码。
```

3. Bell 态密度矩阵与 partial trace

```text
请编写一个完整的 Python 模块，实现 density_from_state(state)、tensor_product(rho_a, rho_b)、partial_trace(rho, dim_a, dim_b, trace_out) 和 purity(rho)。要求支持用列表表示的实数矩阵和状态向量。对于 Bell 态 (|00>+|11>)/sqrt(2)，density_from_state 必须构造正确的 4x4 密度矩阵；对 Bell 态 trace_out="A" 或 trace_out="B" 都必须得到最大混合态 [[0.5,0],[0,0.5]]。Bell 态 purity 必须为 1.0，约化态 purity 必须为 0.5。只输出 Python 代码。
```

4. QAOA MaxCut 代价函数和经典验证

```text
请编写一个完整的 Python 模块，实现 QAOA/MaxCut 的经典验证函数：maxcut_cost(bitstring, edges)、brute_force_maxcut(n_nodes, edges)、qaoa_cost_landscape(n_nodes, edges)。maxcut_cost 要计算 bitstring 在给定无向边集上的割边数量。对于三角形 edges=[(0,1),(1,2),(0,2)]，maxcut_cost('000') 必须为 0，maxcut_cost('010') 和 maxcut_cost('100') 必须为 2。对于线形图 edges=[(0,1),(1,2),(2,3)]，maxcut_cost('0101') 必须为 3，maxcut_cost('0011') 必须为 1。brute_force_maxcut 必须返回真正达到最大割值的 bitstring 和 cost；qaoa_cost_landscape 必须枚举全部 bitstring 并按 cost 降序排序。只输出 Python 代码。
```

5. 量子噪声信道

```text
请编写一个完整的 Python 模块，实现单量子比特噪声信道：depolarizing_channel(rho, p)、amplitude_damping_channel(rho, gamma)、channel_fidelity(rho, sigma)。rho 和 sigma 使用 2x2 密度矩阵列表表示。depolarizing_channel(|0><0|, p=1) 必须返回 I/2，p=0.5 时必须返回 [[0.75,0],[0,0.25]]；对 |+><+| 在 p=0.5 下，输出矩阵的非对角元必须为 0.25。amplitude_damping_channel(|1><1|, gamma=1) 必须返回 |0><0|，gamma=0.5 时必须把 |1><1| 变成 [[0.5,0],[0,0.5]]。所有信道必须保持 trace=1。只输出 Python 代码。
```

6. Shor 9 比特纠错码

```text
请编写一个完整的 Python 模块，实现 Shor 9 比特纠错码的简化状态向量模拟：shor_encode(logical_bit)、apply_x_error(state, error_qubit)、shor_decode(state)。shor_encode 必须把 1 个逻辑比特编码为 9 个物理量子比特的 512 维归一化状态向量。shor_encode(0)[0] 和 shor_encode(0)[511] 都必须为 1/(2*sqrt(2))；shor_encode(1)[0] 必须为 1/(2*sqrt(2))，shor_encode(1)[511] 必须为 -1/(2*sqrt(2))。对 logical_bit 为 0 或 1 的编码态，在 qubit 0、4 或 8 上施加单个 X 错误后，shor_decode 必须恢复原 logical_bit。只输出 Python 代码。
```

7. Trotter 化哈密顿量演化

```text
请编写一个完整的 Python 模块，实现单量子比特哈密顿量的 Trotter 化时间演化：pauli_matrix(label)、matrix_exp_hermitian(matrix, theta)、trotter_evolve(state, hamiltonian_terms, t, steps)。pauli_matrix 必须支持 "I"、"X"、"Y"、"Z"。matrix_exp_hermitian(Z, pi/4) 必须等价于 exp(-i*pi/4*Z)，对角元分别为 exp(-i*pi/4) 和 exp(i*pi/4)；matrix_exp_hermitian(X, pi/2) 的非对角元必须为 -i。trotter_evolve([1+0j,0+0j], [(1.0,"X")], t=pi/2, steps=100) 必须近似得到 -i|1>；在 H=Z, t=pi 下必须近似得到 -|0>；多项哈密顿量演化必须保持归一化。只输出 Python 代码。
```

8. GHZ/W 态与纠缠见证

```text
请编写一个完整的 Python 模块，实现 GHZ/W 态和纠缠指标：ghz_state(n)、w_state(n)、ghz_witness_expectation(state, n)、concurrence_2qubit(state)。ghz_state(3) 只能在 |000> 和 |111> 上有非零振幅，且均为 1/sqrt(2)；w_state(3) 只能在 |001>、|010>、|100> 上有非零振幅，且均为 1/sqrt(3)。对纠缠见证 W=I/2-|GHZ><GHZ|，GHZ_3 的期望值必须为 -0.5，|000> 必须为 0，W_3 必须为 0.5。Bell 态 concurrence 必须为 1，|00> product state concurrence 必须为 0。只输出 Python 代码。
```

## 与 V0.1.0 的关系

V0.1.0 主要是 `Qwen3.6-27B + 本地量子文档 RAG` 的验证版本，重点证明本地量子知识库、SDK 文档和量子编程任务可以被检索并注入回答上下文。V0.2.0 则以 Qwen3.6-35B 微调模型为核心，把量子计算科学能力沉淀到模型参数中。

仓库中仍保留 V0.1.0 的本地 RAG、文档抓取、索引构建和检索评测工具。这些工具可以作为 V0.2.0 的可选增强链路，但不再是 V0.2.0 的主定位。

## 仓库工具

本仓库包含支撑量子计算科学模型研发与验证的工具链：

- 文档源配置：`configs/quantum_doc_sources.json`
- 本地精选量子说明：`docs/quantum_libraries`
- 外部量子 SDK 文档抓取：`scripts/fetch_quantum_docs.py`
- RAG 索引构建：`scripts/build_quantum_rag.py`
- 检索和注入核心：`quantum_rag/`
- 量子编程任务：`evals/tasks/quantum`
- 评测脚本与报告：`evals/`、`scripts/`、`reports/`

## 使用说明

获取代码：

```bash
git clone https://github.com/xuda1979/quantum-gpt.git
cd quantum-gpt
```

V0.2.0 的模型权重、量化版本、推理服务配置和下载地址以正式发布产物为准。由于模型基于 Qwen3.6-35B 微调，推荐优先使用具备 GPU/NPU 加速能力的服务器或推理平台部署；如需本地运行，应根据发布产物选择合适的量化版本，并预留足够内存、显存和磁盘空间。

## 已知边界

- 模型可以辅助量子计算学习、科研分析和代码原型开发，但不能替代严格的数学证明、实验验证或同行评审。
- 对前沿研究结论、硬件实验结果和精密数值结论，应结合权威文献、仿真结果和专家审阅共同判断。
- 对生产环境代码、实验脚本和论文结论，建议保留人工审查、单元测试和可复现实验记录。

## 推荐提问示例

```text
请写一个 Python 模块，实现量子相位估计的 phase_estimation 和 phase_from_measurement，要求 phase_estimation(0.25,3)=2、phase_estimation(0.75,4)=12、phase_estimation(1/3,3)=3。只输出代码。
```

```text
请写一个 Python 模块，用状态向量实现 Grover 搜索的 uniform_superposition、oracle、diffusion 和 grover_search。要求 2 比特 marked=3 一次迭代后命中概率为 1.0。只输出代码。
```

```text
请写一个 Python 模块，实现 QAOA MaxCut 的 maxcut_cost、brute_force_maxcut 和 qaoa_cost_landscape，并通过三角形图和 4 节点线形图的测试。只输出代码。
```

```text
请写一个 Python 模块，实现 Bell 态密度矩阵、tensor_product、partial_trace 和 purity，要求 Bell 态约化密度矩阵为 I/2，purity 为 0.5。只输出代码。
```

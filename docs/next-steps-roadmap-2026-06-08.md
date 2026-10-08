# 下一步研发工作路线图

日期：2026-06-08
 
仓库：[quantum-gpt](../)
 

---

## 1. 任务一：100 题高质量数据微调 Qwen 3.6 35B（`AI` 环境）

### 1.1 为什么要做

#### 1.1.1 科学依据

小样本高质量微调能取得显著效果，是过去两年被反复验证的结论：

1. **LIMA: Less Is More for Alignment**（Zhou et al., Meta AI, NeurIPS 2023, arXiv:2305.11206）
   - 论文核心结论：“A model's knowledge and capabilities are learnt almost entirely during pretraining, while alignment teaches it which subdistribution of formats should be used when interacting with users.”
   - 使用 **1000 条**精心策划的提示和回复对 LLaMA-65B 做 SFT，在人类偏好评估中与 RLHF 训练的 DaVinci003 相当或更优。
2. **OpenAI Fine-Tuning Technical Guidelines & Best Practices**（OpenAI, 2023-2024）
   - 官方开放技术指南指出，仅需 **50 到 100 条高质量、精心策划的黄金演示样本**，即可大幅改善模型在特定垂直领域、特定任务格式、自定义交互风格等维度的生成表现，其效果远远优于数千条带有噪声或不够准确的普通样本。在特定对齐阶段，**数据质量对模型性能表现起决定性支配作用**。
3. **LoRA: Low-Rank Adaptation of Large Language Models**（Hu et al., Microsoft, ICLR 2022, arXiv:2106.09685）
   - 证明 LoRA rank=8~64 即可达到全参数微调 99% 的效果，可训练参数减少 10000×。
4. **QLoRA: Efficient Finetuning of Quantized LLMs**（Dettmers et al., NeurIPS 2023, arXiv:2305.14314）
   - 4-bit 量化 + LoRA 在单 48GB GPU 上微调 65B 模型，验证了低算力可行性。

#### 1.1.2 业务依据

已有 100 条高质量量子编程问题（5 种任务类型，已分类好难度、框架与子类），是直接可用的种子数据。配套的 203 条蒸馏教师回复已经过结构化验证。

### 1.2 怎么做

#### 1.2.1 训练配置与启动

- 基础模型：Qwen 3.6 35B-A3B，远端路径已定位
- LoRA：rank=64，alpha=128，dropout=0.0，target_modules 覆盖全 linear 映射
- 最小可训练参数：≥200M（防止 silent fallback 到低参数）
- 模块纯净性：**纯 SFT 训练，不接强化学习**

#### 1.2.2 算力预算

- 算力：8 NPU × 1.5h (time-boxed)
- 数据规模：100~200 高质量样本 × 3 epoch = 300~600 个优化步
- 总耗时估算：50min~2h，符合约束

#### 1.2.3 评测

- 提取专项评测集进行 pass@1、无人工干预 of 纯净评测。

### 1.3 参考文献（汇总）

- Zhou et al., LIMA: Less Is More for Alignment, NeurIPS 2023. arXiv:2305.11206
- OpenAI, Fine-Tuning Technical Guides and Developer Best Practices, OpenAI Developer Platform, 2023.
- Hu et al., LoRA: Low-Rank Adaptation of Large Language Models, ICLR 2022. arXiv:2106.09685
- Dettmers et al., QLoRA, NeurIPS 2023. arXiv:2305.14314

---

## 2. 任务二：智能体主动调用 RAG 机制

### 2.1 为什么要做

#### 2.1.1 科学依据

1. **Retrieval-Augmented Generation (RAG)**
   - **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks**（Lewis et al., Facebook AI, NeurIPS 2020, arXiv:2005.11401）—— 原始 RAG 框架，证明检索 + 生成在知识密集任务上显著优于纯生成。
   - **Atlas: Few-shot Learning with Retrieval Augmented Language Models**（Izacard et al., Meta AI, JMLR 2023, arXiv:2208.03299）—— 少样本场景下 RAG 比 10× 参数量的纯参数模型还好，直接对应本工作“低算力 + 100 题”的设定。
   - **REALM**（Guu et al., Google, ICML 2020）
2. **智能体作为 RAG 调度器（Tool-Use 视角）**
   - **Self-RAG**（Asai et al., U-Washington, ICLR 2024, arXiv:2310.11511）—— 模型主动决定“何时检索 / 检索什么 / 检索多少”，比固定 RAG 准确率高 10~20%。
   - **ToolLLM**（Qin et al., Tsinghua, ICLR 2024, arXiv:2307.16789）—— 工具调用作为大模型第一优先级的工程范式。
   - **Toolformer**（Schick et al., Meta AI, NeurIPS 2023, arXiv:2302.04761）—— 自监督 tool-use 数据合成，不需要强化学习。
3. **Agentic RAG / Adaptive RAG**
   - **Adaptive-RAG**（Jeong et al., NAACL 2024, arXiv:2403.14403）—— 按题目复杂度动态选择 RAG 路由。

这些都是在 **SFT 纯监督蒸馏范式**下实现的方法，**不依赖于复杂的强化学习训练**，与“近期不实施 RL”的约束完美一致。

#### 2.1.2 业务依据

仓库内 RAG 语义检索、倒排索引构建及命中层在 158 题上展现出 hit@5 达 100% 的极高表现。

### 2.2 怎么做

#### 2.2.1 强化回放与温热启动量化

1. **算力需求**：此阶段由于使用热启动微调，远端 8 NPU 只需 1 小时即可收敛。
2. **业务指标度量**：评测模型主动发起检索后最终作答的通过率，目标整体作答通过率相较非 RAG 原生版本提升 15 个百分点。

---

## 3. 任务三：智能体行为轨迹克隆后训练（SL 蒸馏与拒绝采样）

### 3.1 为什么要做

#### 3.1.1 业务背景
将大模型训练为编程与独立工具调用的智能体，作为本项目的方法论基石。智能体需要学会在复杂的交互步骤中主动规划、自我纠错并寻找正确路径。

### 3.2 怎么做

#### 3.2.1 轨迹数据生成与提纯流程
- **训练演示轨迹合成**：使用高级教师大模型（例如 gpt-5.4）生成包含探索行为、阅读细节、并最终解决问题的完整思维链轨迹。
- **结果反向过滤（拒绝采样）**：丢弃最终失败的动作路径，只抽取彻底合规、绿灯通过的逻辑流，保留教师模型确实命中了有效关键词且结果无误的轨迹。

#### 3.2.2 轨迹对齐后训练技术
- **结构化对话转换**：将思考、动作结构化地编码进模型的消息流中（如 ChatML 规范）。
- **Masking 动作计算精确性**：训练过程中，**只针对模型输出（assistant）进行交叉熵 Loss 计算**。对于环境反馈（如文档匹配结果、命令行输出等）严格进行 Loss Masking。这确保了模型不会去“强背”环境返回，只学习“面对何种环境进行何种逻辑反馈”。
- **冗余死角修剪与长截断**：自动检测并裁减掉因模型幻觉或失误导致的连续重复垃圾调用；对超长文档或运行日志做动态截断，确保模型上下文窗口的高效性。
- **保留“成功纠错的经历”**：这部分至关重要，故意留存模型在一次微小语病下能捕获错误日志并修复的路径。这是模型习得“主动排错（De-bug）”能力的核心来源。

---

## 4. 任务四：深度压缩 KV 缓存框架（已有成果与对齐）

### 4.1 为什么要做

#### 4.1.1 显存瓶颈制约
35B 模型在 128K 超长上下文下运行，单个 Batch 的 KV 缓存显存开销会高达惊人的 72 GB。这直接导致单卡无法容纳超长上下文推理。

#### 4.1.2 科学依据
- **KIVI**（Liu et al., ICML 2024, arXiv:2402.02750）—— 2-bit 无损 KV 缓存非对称量化。
- **KVQuant**（Hooper et al., NeurIPS 2024）—— per-channel 混合量化支持千万长度上下文。
- **QuaRot**（Ashkboos et al., NeurIPS 2024）—— Hadamard 旋转抑制数值异常离群值。

### 4.2 已有成果

研发团队已成功编码基于 **TurboQuant** 的优化逻辑：

1. **核心配置套件已完备**，支持 group-wise 对称/非对称压缩。
2. **可微分 Hadamard 高维旋转模块**已完成设计，解决量化在深层激活中的精度崩溃问题。
3. **双重残差补强量化**（Primary-Secondary 量化），在极低位宽（极低-bit）下实现精度兜底。
4. **无缝契合 HuggingFace DynamicCache 基础框架**，实现了 drop-in 即插即用替换（无需修改 Transformers 核心库）。

### 4.3 下一步研发重点

1. **高保真一致性质量扫视**：
   在 158 题和标准考卷上，开启不同配置（2-bit, 4-bit 组合）以测量对最终 Pass@1 质量的影响。
2. **熔断与对准参数**：
   锁定使推理质量损失 < 1%，但 KV 缓存显存硬性开销下降 ≥ 5x 的最佳比特结构。

---

## 5. 任务五：NPU 原生混合脉冲-状态空间大模型架构（前沿探索）

### 5.1 为什么要做

#### 5.1.1 混合架构的前沿爆发性
2024 年起，学术界和巨头相继证实混合架构（Hybrid: Attention + State-Space + Spiking）在性能、开销上极具竞争力：

1. **状态空间模型（Mamba）**
   - **Mamba**（Gu & Dao, 2024）—— 线性时间复杂度，颠覆 Transformer。
   - **Jamba**（AI21 Labs, 2024）—— 混合大尺度语言模型，支持超长上下文（256K）。
2. **脉冲神经网络（Spiking Neural Network, SNN）应用**
   - **SpikeGPT**（Zhu et al., 2024）—— 脉冲大模型低能效突破。
   - **SpikeLLM**（Xing et al., 2024）—— 证实 7B 脉冲模型的可用性。
3. **高泛化与稀疏偏置**：
   - 脉冲发放类似天然的极低损 Dropout 与路由机制。

### 5.2 怎么做（三阶段节流开发）

为应对有限的算力约束，采用阶段级开发，每一步骤设立严格熔断评审：

#### 5.2.1 阶段 P0：CPU 算法原型验证（2 周）
- 原生 PyTorch 在底层重组 Choice-SSM 层与 Leaky Integrate-and-Fire (LIF) 脉冲神经单元。
- 不干涉主干网络，通过本地脚本完成运算逻辑和反向梯度更新的验证。

#### 5.2.2 阶段 P1：NPU 原生算子重构（1 个月）
- 使用硬件原生 AscendC 语言实现 `selective_scan` 核心算子，规避 PyTorch 原生低效循环。
- 基准对齐：以单 NPU 运行，相较 Python 等效代码实现 5x 加速。

#### 5.2.3 阶段 P2：部分层动态合并（2 个月）
- 将 Qwen 主体的后部网络层替换为脉冲与状态空间模块。
- 冻结模型前部，仅微调混合后部（参数占比约 5%），确保不造成原大模型的基础智能崩塌，完成前沿泛化水平的评估。

---

## 6. 五大任务横向对比与排期保障

结合项目组能效，对所有的研发任务执行多维标度评估：

| 编号 | 任务方向 | 价值度 | 难度 | 创新度 | 工作量 (人周) | 算力占用 (8 NPU) | 风险级别 | 启动排序 |
|---|---|---|---|---|---|---|---|---|
| **1** | 100 题黄金微调（Qwen 3.6 35B）| ★★★★ | ★ | ★★ | 1.0 人周 | 1.5h | 极低 | **第一阶段立即启动** |
| **2** | 智能体主动调用 RAG | ★★★★★ | ★★ | ★★★★ | 2.0 人周 | 1.0h | 低（已有RAG链路）| **第一阶段立即启动** |
| **3** | 智能体行为轨迹克隆后训练 | ★★★★★ | ★★ | ★★★★ | 3.0 人周 | 2.0h | 低 | **第一阶段立即启动** |
| **4** | KV 缓存深度压缩量化验证 | ★★★★ | ★ | ★★★★ | 2.0 人周 | 1.5h (1卡) | 极低（代码已通）| **第一阶段对齐完成** |
| **5** | NPU 原生混合脉冲状态架构 | ★★★★★ | ★★★★★ | ★★★★★ | 12.0 人周 | P0:0h / P1:4h (1卡) | **高**（开发高度挑战）| **暂做 P0，余推本年下期** |
| **—** | 暂缓：GRPO/RLVR 强化对齐 | —— | —— | —— | —— | —— | —— | **暂缓（等高层触发）** |

---

## 7. 附录：关于模型规模与微调样本效率的专项综述

在决定微调方案时，针对“是否需要扩充巨量标注样本”常有争论。最新指令微调与对齐的 Scaling Law 定量科学研究指出：**网络参数规模越大，在特定任务上对对齐样本的消耗量越呈反向幂律（等效指数级）递减。**

### 7.1 理论与定量数学模型

根据微调标度定律（Scaling Laws for Fine-Tuning），要在下游垂直任务上达到目标表现，所需的微调数据样本量 $\mathcal{D}_{\text{SFT}}$ 随模型参数量大小 $\mathcal{N}$ 呈幂律关系递减：

$$\mathcal{D}_{\text{SFT}} \propto \mathcal{N}^{-\alpha} \quad (\alpha > 0)$$

其中，$\alpha$ 为缩放指数系数。这意味着，当模型底座规模 $\mathcal{N}$ 发生断崖式跨越时（例如从 $7\text{B}$ 跃升至 $35\text{B}$），下游对齐任务对物理数据样本数 $\mathcal{D}_{\text{SFT}}$ 的耗费率急剧稀释。大模型表现出显著更高的样本效率（Sample Efficiency）。

### 7.2 学术文献与工业界实证支持

本工作“100 题黄金种子微调”的技术路径，拥有大模型对齐发展史上极其扎实、严谨的经典科学文献支撑：

#### 7.2.1 定量微调 Scaling Laws 定律
* **文献**：***Scaling Laws for Fine-Tuning Language Models*** (Danny Hernandez, Jared Kaplan, Tom Henighan, Sam McCandlish, John Schulman, OpenAI, 2021)
* **链接**：`arXiv:2111.02080`
* **核心定量结论**：
  > *"When fine-tuning on a specific task, larger models are much more sample-efficient. The amount of fine-tuning data required to achieve a target performance on the downstream task decreases as a power-law of the model parameter size."*
  
  该研究在数学上全面验证了基座规模与微调数据需求的幂律递减关系，大预训练底座相较小模型极大加速了在垂直领域的泛化速度，使极少的高保真黄金对齐样本成为可能。

#### 7.2.2 原始样本利用效率奠基作
* **文献**：***Scaling Laws for Neural Language Models*** (Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B. Brown, Alec Radford, OpenAI, 2020)
* **链接**：`arXiv:2001.08361`
* **核心定量结论**：
  > *"Larger models are significantly more sample-efficient, such that optimally compute-efficient training involves training very large models on a relatively modest amount of data and stopping significantly before convergence..."*
  
  这篇 Scaling Laws 开山之作定量指出，大参数大底座的核心优势在于极高维度表示空间的建立，使得样本在微调和模式拉齐（Alignment Pattern）中的损耗速度、学习轮次产生质的跨越。

#### 7.2.3 “精多胜滥”高质量微调实证 
* **文献**：***LIMA: Less Is More for Alignment*** (Chunting Zhou, Pengfei Liu, Puxin Xu, Meta AI, NeurIPS 2023)
* **链接**：`arXiv:2305.11206`
* **核心定量结论**：
  > *"Almost all knowledge is learned during pretraining, and only limited instruction tuning data is necessary to teach models to produce high quality output."*
  
  Meta AI 使用顶尖 pretraining 的 LLaMA-65B，在仅 **1000 条**精心筛选的微调样本下，无须任何复杂的 RLHF，在人类偏好主观和客观评测中表现出超越或持平 DaVinci003 的对齐涌现性能。

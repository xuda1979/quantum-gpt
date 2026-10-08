# 领域专家大模型微调研究 - extracted notes

Source: `领域专家大模型微调研究.pdf`
Pages: 18



## Page 1

大语言模型领域专家化微调与持续学习防遗忘技术研究报告

大语言模型领域自适应与灾难性遗忘的内在机理

大语言模型在经过海量通用文本预训练后，积累了深厚的跨域常识与通用推理能力

1
。 然 而 ， 将 其
部署至医
疗、
法
律、
金融或高精尖工程等高度专业化的垂直领域时，原始基座模型通常面临专业术语缺
乏、
深层行业逻辑偏离以及输出格式不合规等核心局限

2
。为了解决这些瓶颈，对模型进行领域自适应微调和基于人类偏好的强化对齐已成为转化为高可靠领域专家模型的标准工程范式

4
。在此上演化过程中，模型需要顺次经历持续预训
练、
领域指令微调与持续对齐三大核心训练阶段

1
。然而，在这些阶段中，大语言模型不得不面临连接主义网络中经典的稳定性与可塑性困境，其最具破坏性的具体表现即为灾难性遗忘

6
。当模型在特定新领域数据上进行顺序微调以吸纳专业知识时，其原有的通用推
理、
常识问
答、
多语言处理及基础指令遵循能力往往会发生显著退化甚至彻底丧失

8
。针对从数十亿到万亿参数级大型语言模型在顺序微调过程中的微观机理分析表明，灾难性遗忘并非随机发生的扰动，而是由变压器架构内部深层状态表征的系统性失效所致

8
。通过对包括

Llama

4

Scout
、
GPT-5.1

以及

DeepSeek-V3

等多种主流架构在不同相似度微调轨迹下的

temporal

动态测量，研究界提炼出了导致遗忘发生的三大根本微观机制

8
。首先是注意力投影权重中的梯度干扰，在新任务梯度方向与旧任务最优点正交性较差时，共享的投影矩阵会被强制重写

2
。 其 次 是 中
间隐层的表示漂移，高维激活流经多层堆叠后，表征流形发生系统性扭曲

8
。最后是先前任务局部极小值周围的损失地貌平坦化，使模型无法在旧任务的流形内恢复原始概率分布

8
。大语言模型在遭遇完全灾难性遗忘时，往往表现出极具欺骗性的隐性失效模式

12
。在实际生产微调过程中，训练日志通常不会抛出任何

system

错误或警告，模型也能够成功加载并执行常规推理，但其评测指标会瞬间跌至零点，具体表现为模型无法生成任何有效的垂直领域或通用领域词元，仅机械地返回原始提示词或直接输出空字符串

12
。这种失效往往具有独特的尺度效应与架构
偏 好
8
。 随 着 模 型 参 数 量 从

扩展至


乃至万亿级别，由于初始泛化流形更为复杂，参数微小的扰动极易引发全网激活状态的连锁失调，导致规模越大的模型在面对单领域微调时遗忘程度越发剧烈

9
。此外，相比于编码器
-
解码器架构
（如

mT0
），仅解码器架构
（如

BLOOMZ
）在持续指令微调中展现出更强的通识保留度与知识韧性，且适度的通用指令微调能够显著缓解随后的自适应遗忘，甚至能在演进中自发削弱语言模型固有的性别等社会偏见

10
。下表梳理了多款前沿大语言模型在面对不同相似度领域微调轨迹下的灾难性遗忘行为与微观失效表征：

评估模型架构

总参数量

/

激活 参 数 量
典型微调顺序轨迹与任务
相似 度
核心行为衰退指标

主要微观物
理表 征 机 制
Llama  4  Scout

总参数

/
情 感 分 析
通识保留度
适 注 意 力 投 影 矩



## Page 2

激 活  (MoE)
情绪分类

毒性检测

(
高
相似 度 )
中，但后继同质任务极易导致前序分类边
界重 写。
阵梯度干扰，主
要 集 中 于
和

权
重。

Llama  4  Maverick

总参数

/

激 活  (MoE)
问答
摘 要

翻译

(
中
相似 度 )
语言生成连
贯性 保 持 良 好 ， 但
跨语境摘要精度发生漂
移。

中间隐层表示流形发生系
统性 扭 曲 ， 激 活 流
分布发生不
可逆 漂 移。
GPT-5.1
约


估
计参 数  ( 密 集 型 )
科学问答

代码生成

逻辑推理

(
低
相似 度 )
在代码生成任务微调后，通用数学常识与多步逻辑推理出现剧烈滑
坡。

损失地貌在先前任务局部极小值周围急剧平坦化，通识
流形 塌 陷。
DeepSeek-V3

总参数
(MoE)
医疗诊断

金融评级
法 律 条 款  ( 中 低相 似 度 )
专家词汇吞
吐率 提 高 ， 但 在 高
阶逻辑任务中出现指令退化与行为失
常。

稀疏路由门控权重在不同专家网络间的分配发生漂移
冲突。
传统持续学习范式在大语言模型中的失效分析

为了在向特定领域过渡时维持通用能力，业界曾尝试直接沿用传统持续学习中的五大主流技术流派，然而在实际应用中，这些经典算法在面对百亿级以上的变压器架构时均暴露出了不可逾越的局限性

6
。在正则化策略中，弹性权重巩固（
EWC
）通过评估

Fisher

信息矩阵的对角线元素来识别并惩罚对历史任务至关重要的参数更新

6
。在实际大模型工程中，通常利用

Adam

优化器中的平方梯度累加器

作为

Fisher

对角线矩阵的低成本近似估算

13
。尽管在理论上很优雅，但在链式微调

个连续垂直领域时，由于多领域参数重要性冲突不断累积，
EWC

的惩罚项会迅速将大部分参数锁死
13
。至微调第


个领域时，模型已彻底丧失可塑性，而通用能力的遗忘漂移率依然高达


13
。突触智能（
SI
）通过在线实时累加参数对损失降低的贡献路径来代替昂贵的

Fisher

矩阵计算，但同样无法避免多域梯度方向冲突引发的参数锁死困境

6
。在重放与回放策略中，经验回放（
ER
）通过在训练新领域数据时，强制混合并重放一部分历史任务或基座预训练数据
（如

FineWeb
、
CC

等）
来稳定梯度方向

6
。尽管该策略在维持通用能力方面效果较为显著，但在金
融、
医疗等受到严格安全与隐私合规监管的行业中，由于数据合规限制，历史敏感数据往往无法长期保留并用于重放训练

13
。同时，随着微调领域的不断叠加，重放缓冲区所需



## Page 3

的存储空间与计算带宽开销呈线性甚至几何级数膨胀，面临严重的资源扩展瓶颈

13
。在基于架构的分区策略中，
PackNet

等方法通过迭代剪枝冻结特定参数子网，将空闲容量分配给新领域，而硬注意力掩码（
HAT
）则通过学习二进制掩码来保护特定任务的神经元

6
。由于语言模型内部的表征高度分布且存在严重的非线性耦合，在进行


个简单任务微调后，模型的闲置神经容量便会被迅速榨干，无法支撑多领域的持续进化

13
。知识蒸馏
（如

LwF
）通过在训练期间并行运行一个冻结的原始模型作为教师来规范学生的

Logits

分布，但在


及以上规模时，其双模型运行会导致显存开销直接翻倍，且万亿级参数教师模型的输出对数概率中包含的大量无效噪声常会导致蒸馏过程失效

13
。正交梯度投影（
OGD
、
A-GEM
）则试图将新梯度投影到旧梯度的正交子空间中，但这在参数空间极度复杂的

LLM

中，会导致投影约束条件呈爆炸式苛刻，微调至后期时几乎剥夺了新梯度的所有物理更新维度

13
。下表横向对比了五大传统持续学习技术在大语言模型垂直领域落地时的底层缺陷：

技术流派

经典代表算法

领域微调中的核心作用逻辑

在大语言模型专
家化 中 的 致 命 失 效 模式
参数正则化

弹性权重巩固
(EWC)
6
基于

Fisher

矩阵限制重要权重的偏移

6
。惩罚冲突导致参数锁死，多域演进中模型完全丧失新知识吸纳能力

13
。
数 据 重 放
经验回放

(ER)

6
混合并重训部分历史或通识数据

6
。受限于行业隐私合规与数据主权，且存储
/
计算开销线性
暴增
13
。网络分区
PackNet  /  HAT
6
剪枝冻结子网，隔离各领域的神经元

6
。语言表征高维分布，空闲容量极速耗尽，阻断知识的跨域
前向 迁 移
13
。梯度约束
正 交 梯 度 投 影  (OGD)
13
强制梯度在新领域更新时与历史正交

13
。几何约束随着领域累积呈指数级严苛，导致参数更新空间彻底塌陷

13
。行为蒸馏

学习不忘

(LwF)

13
基于双模型并行约束输出概率分布

13
。

以上规模显存倍增，且万亿参数规模下

Logits

噪声导



## Page 4

致蒸馏失效

13
。领域自适应持续预训练与指令微调先进技术

面对经典方案在垂直领域落地时的系统性失效，大模型研究界在

2025

至

2026

年间，针对

Transformer

架构的参数流形和信息路由特征，提出了一系列具有突破性的

SOTA

遗忘防护技术
19
。领域自适应持续预训练

(DACP)

的演进规律

在缺乏行业专有语料和生僻术语的极端场景下，直接进行监督指令微调（
SFT
）往往无法系统性注入深层的新领域事实知识，而仅仅是在调整模型的表出语调与格式偏好

17
。因此，在

SFT

之前对中等规模的非结构化语料
（如
数百吉字
节）
进行领域自适应持续预训练（
DACP
）已成为行业公认的专家化首要步骤

17
。为了维持通用底底座的完好度，
DACP

必须引入通识回放数据集
（通
常从

FineWeb
、
Common

Crawl
、
Wikipedia

和

GitHub

中按比例抽
取）

17
。
在 基 于  EXAONE-3.5  2.4B  模 型 以 及

词元的韩国电信（
Telco
）垂直领域自适应预训练研究中，揭示了一个关于“重放比例”的临界转化规律

17
。当通识回放数据比例处于较低区间时，通用基准能力发生断崖式下跌

22
。随着回放比例逐步提升，通用常识评估精度随之单调上涨，然而，一旦回
放 比 例 突 破
，电信专业领域的自适应精度便开始发生系统性衰退

22
。这一现象背后的机理在于，过高比例的回放语料对梯度方向产生了强烈的通识拉扯，实质上稀释了垂直领域专业梯度的暴显强度，使得模型在有限的训练步数（
Steps
）内无法有效建立起关于行业生僻术语的致密激活网络

22
。因此，在持续预训练阶段，将回放比例精确控制在


是兼顾通识保持度与行业专业性的最佳参数区间

22
。遗忘感知剪枝度量法

(Forgetting-Aware

Pruning

Metric,

FAPM)

在进行全参数微调或大参数

PEFT

时，新知识在网络中的沉淀可以被抽象为任务向量（
Task

Vector
），其定义为微调参数与原始预训练参数的差值：


研究揭示，任务向量的物理绝对值大小，以及它与原始基座敏感参数的重叠程度，构成了灾难性遗忘的决定性触发因子

21
。
FAPM

提出了一种完全无需修改训练过
程、
无需引入任何辅助语
料、
仅在微调结束后对权重空间进行外科手术式后处理的合并剪枝算法

21
。它认为，如果一个权重的任务向量改动绝对值


极大，但原始预训练参数


的绝对值相对微小，说明该参数经历了剧烈的相对重写，是破坏底层常识流形的罪魁祸首

24
。
FAPM

构建了如下的联合权重判定公式：




## Page 5


其 中

代表对应权重张量的平均绝对值，用于消除跨层或跨张量块的量纲差异

26
。 算
法通过根据度量值


设定硬阈值，将判断为“高破坏性”的任务向量分量强制清零（
Prune

to

Zero
），从而使对应神经元原位恢复到原始基座预训练参数，保留通识基石

21
。实验表明，
FAPM

在

Natural

Language

Inference
、
Medical

QA

等跨越八个异质数据集的评测中，能够使下游专业精度维持在

，而整体遗忘率大幅压制在


左右，在遗忘防护表现上系统性优于常规

LoRA

21
。在策自蒸馏微调

(Self-Distillation

Fine-Tuning,

SDFT)

经典的监督微调（
SFT
）本质上是一种非在策（
Off-policy
）的行为克隆，即强制要求模型在测试阶段完美重合静态专家演示数据的绝对轨迹

19
。然而，由于语言生成的长程依赖特征，一旦模型在真实部署中产生微小的词元生成偏差，便会迅速偏离专家演示分布，滑入其从未见过的激活状态空间，进而引发长程幻觉与旧常识能力的崩溃

27
。麻省理工学院（
MIT
）等机构于

2026

年提出的

SDFT

框架，创造性地通过大模型自身的上下文学习（
ICL
）构建了在策闭环自蒸馏机制

29
。在每个训练

Step

中，同一模型同时扮演两个物理角色

29
：  ●
教师角色：该分支的模型权重完全保持静态或处于指数滑动平均（
EMA
）状态

31
。模型输入端被额外喂入“问题

+

专家黄金演示

”作为

ICL

上下文，引导其利用基底模型的强大推理流，在原语流中生成高逻辑密度的正确链式推理路径

29
。
●
学生角色：该分支作为参数更新的实体，输入端仅被喂入单纯的“问题
” 本 身 ， 并 在 策 自 由
生成输出轨迹

29
。训练的目标旨在最小化学生自由生成流与教师

ICL

诱导流在对应词元位置上的

Kullback-Leibler

(KL)

散度

27
：

在没有全词表对数概率

API

支持的工业级

Tinker

部署实践中，通常通过对前
（如  ）
个最高概率词元进行重归一化，使用交叉熵来近似实现无损的在策蒸馏，并且采用完全静态的初始基座模型代替复杂的

EMA

动态同步，在大幅降低系统通信开销的同时，保持性能不退化

31
。
SDFT

的性能表现展现出极强的模型尺度门槛

28
。 在

及以下参数规模时，由于基座模型的

ICL

上下文学习推理流过于孱弱，无法产生高质量的自蒸馏教师

Logits
，
SDFT

的表现略微落后于



## Page 6

标准

SFT

28
。 但 在

规模下，
SDFT

相比

SFT

的优势提升了

；当扩展至


参数时，其在

Science

QA

及医疗诊断等任务上的领先优势扩大到了

，且多技能链式微调时，其旧技能留存线始终保持平稳，完美突破了传统微调的遗忘诅咒

28
。多头混合专家路由重构

(Multi-Head

Mixture-of-Experts,

MH-MoE)

混合专家系统（
MoE
）通过稀疏门控路由将计算动态导向不同专门专家子网，在理论上非常符合持续学习的物理隔离要求

11
。然而，最新的研究发现了传统

MoE

模型在持续微调中依然发生剧烈遗忘的隐性根源：多头注意力机制在路由前形成的拼接瓶颈

20
。在常规变压器架构中，多头注意力（
MHA
）的各个头在物理上各自捕捉完全不同的特征流
（如
部分表征语义，部分捕获位置结
构）

20
。然而，在进入

FFN

层的

MoE

门控路由器之前，这些多头的输出被机械地拼接（
Concatenate
）并统一映射，形成单个高维路由器输入向量

20
。这种粗暴的拼接迫使路由器对高度混杂的“特征组合”而非原位单一特征做出路由分发决策

20
。特征组合引发了严重的“组合碰撞”（
Composition

Collisions
），即大量包含微弱泛化特征却包含强烈相似语义的复杂向量被统一分发至同一个专家子网

20
。计算表明，过高的路由有效组合数


与旧任务损失的剧烈上涨高度正相关，导致通识子网被局部领域的微调梯度彻底侵蚀覆写

20
。为了解决该结构缺陷，
2026

年提出的

MH-MoE

架构颠覆了传统路由逻辑，在多头注意力的单个表征头（
Heads
）输出上进行完全独立的头级路由（
Head-wise

Routing
）

32
。对于每一个注意力头


产生的亚表征

，其专属的轻量化头级路由器


独立将计算分发给专家子网

，最终的输出形式重构为：


通过这一改造，路由粒度从词元级细化到了头级，极大地压低了有效组合数

20
。 在  TRACE
持续学习基准测试中，基于

Qwen3-0.6B/8B

的实验表明，
MH-MoE

将旧任务负向反向转移（
BWT
）惩罚从原先

LoRAMoE

下的


缩减到了极低水平的
， 从 根 本 上 在 注 意 力 流 的
分发物理结构上筑起了防遗忘的高墙

20
。下表横向对比了上述前沿自适应微调技术在遗忘防护表
现、
算力开销和数据规模要求上的特征：

先进自适应技术

遗忘率防护极限表现

(BWT)

训练
/
推理额外算力损耗
(FLOPs)
临界样本数据规模要求

底层物理作用维度

DACP  ( 回 放 比例  20%)
17
维持通用常识跑分相对降幅

相比从头训练，计算开销暴降，百吉字节（
GB
）级非结构化语权重空间整体流形对齐

23
。



## Page 7


22
。
但 需 要 并 行 混
合通识数据
计算
1
。料
17
。
FAPM
21
遗忘率控制
在惊 人 的
21
。零训练损耗；后处理剪枝计算可在数分钟
内极 速 完 成
24
。仅需少量微
调后 的 模 型 参 数
矩阵，无需任何辅助语料

24
。参数空间任
务向 量 外 科 剪 枝  21
。
SDFT
19
链式技能学
习中 ， 旧 技 能
BWT

维持在

31
。训练时间变慢约


倍；额外
消 耗   倍 的
计算

FLOPs

用于 在 策  Rollouts  生 成
29
。
至 少
条高质量专家演示样本

3
。激活空间在策概率分布蒸馏
27
。
MH-MoE
20
负向

BWT

从原
MoE  架 构 的
降 至

33
。引入微小门控计算开销，硬件吞吐效率与传统

MoE

基本
持平
33
。
无 特 殊 限 制 ， 直
接在常规持续微调语料中表现卓越

20
。变压器架构信息路由分发
隔离
20
。大语言模型领域专家对齐与偏好优化演进

在完成第一阶段的持续预训练与指令微调（
SFT
）后，必须通过偏好对齐训练，来矫正模型在特定垂直领域输出时的严谨
度、
安全性与行业伦理偏好

2
。这一阶段同样面临着因奖励

hacking

或偏好过度拟合而导致基础推理能力发生全面溃退
（即
对齐
税）
的系统性挑战

36
。直接偏好优化

(DPO)

的工程实践

为了打破传统

PPO

框架中需要同时维护参考模
型、
行动者模
型、
奖励模型及评论员模型共计四个网络的超高显存壁垒，
DPO

算法将奖励函数通过数学变形，直接用语言模型本身的策略对数概率来表示，从而通过简单的分类损失函数在“选择集


-

拒绝集

”的对数似然比值上进行更新

4
。
OpenAI

推荐的黄金对齐工作流为：先在高质量的期望回答子集上运行基础

SFT
，将收敛后的模型作为

DPO

初始策略及静态参考模型的共同起点

4
。这一设计能极大限度地减小

DPO

在更新过程中的权重漂移幅度，提升训练的稳定度并防止过拟合

4
。然而，由于

DPO

的损失函数高度敏感于偏好配对数据中好坏回答的边界似然，在医疗或法律等专家偏好对齐中，人类专家标注往往存在局部的逻辑不一致与矛盾噪声

37
。
DPO

会强制改变基础预训练权重以强行拟合这些局部不一致，从而导致模型丧失在通用推理及数学逻辑任务上的严密性

36
。



## Page 8

卡尼曼
-
特沃斯基偏好优化

(KTO)

的心理学根源

为了彻底解耦对严格“好
-
坏”成对数据的依赖，
KTO

算法通过引入行为经济学中著名的前景理论（
Prospect

Theory
）进行偏好对齐

40
。前景理论指出，人类对随机事件的价值感知天生是非对称的，即失去带来的痛苦远大于同等得到带来的快乐
（人
类天然损失厌
恶）

39
。
KTO

完全抛弃了

DPO

所需的成对数据（
Pairwise

Data
），而仅需要单条生成的二元期望标签
（即
这条回答是期望的

Desirable
，还是不期望的

Undesirable
），极大地减轻了专家的标注开销

39
。 KTO
的损失函数在数学上引入了一个动态的参考点（
Reference

Point
），用于评估当前模型相较于静态
参 考 模 型 的 效 用 偏 差
39
。通过赋予非期望输出更高的惩罚权重

（设定
， 如
），
KTO

完美模拟了人类的非对称损失规避行为

39
。更关键的是，
KTO

构建的效用梯度在对数似然差值趋近无穷时会自动衰减归零，这意味着，当面对专家标注中的严重矛
盾、
极端偏见或离群噪声时，
KTO

能够自发阻尼梯度更新，避免模型强行修改通用底座去适配这些矛盾偏好

39
。因此，
KTO

相比

DPO

能够保留更完整的底层通用推理流，甚至在无需前置

SFT

的情况下，在大型参数模型上直接实现稳健的零遗忘对齐

39
。组对比偏好优化

(SWEPO)

在面临多专业路径分叉的复杂领域场景中
（如
多路并行代码生
成、
不同病理诊疗方案对
比）
，逆变元或配对标签无法刻画不同次优回答之间的精细效用级差

45
。
SWEPO

算法为此应运而生

45
。
SWEPO

允许对同一提示词下的多个候选响应进行统一群组对比，系统性地将所有候选响应划分为均值以上的期望集与均值以下的拒绝集

45
。它通过计算响应与平均效用水平的离散度，为那些表现极端优异或极端劣质的样本赋予指数级增加的对比损失权重

45
。这种基于偏差权重的群组对比设计，相当于为对齐训练内置了一套自适应课程学习，不仅大幅提高了对齐阶段的数据利用效率，也有效防止了模型为了讨好单一局部的专家偏好而破坏原本高度泛化的通用语言概率流

45
。创新方法设计：协同神经模块化在策自蒸馏自适应框架

基于对当前

DACP
、
FAPM
、
SDFT
、
MH-MoE
、
KTO

等各项前沿技术的深层解耦与重组，本报告提出一种全新的创新方法设计：协同神经模块化在策自蒸馏自适应框架（
Synergistic

Neuro-Modular

Adaptation

Framework,

SNMA
）。该框架旨在从物理参数阻
断、
特征通道分
发、
在策行为约束与流形谱空间剪枝四大维度，彻底攻克大语言模型向特定领域进化时的灾难性遗忘诅
咒。

1.

快慢神经网络物理分区机制

(FSPP)

SNMA

首先摒弃了“将所有垂直领域海量知识生硬挤入固定参数”的传统思路，将神经网络划分为双时间尺度协同架构

47
：  ●
慢变参数网络（
Slow

Weights
）：完全冻结语言模型的底层多层堆栈，保护通用语
法、
长程推理与多语言流形免受直接写入干扰

2
。仅在中间层及高层的多头注意力和

投影矩阵中挂载轻量化低秩专家适配器（
LoRA

Adapters
）

2
。  ●
快变上下文记忆（
Fast

Context
）：采用

OS

虚拟内存分页原理
（如

PagedAttention
）建立一个外置的持久化“领域错题与关键案例经验库”
49
。在推理阶段，通过语义向量库实



## Page 9

时检索出与当前提示词最相似的数个专家执行轨迹，作为

Fast

Memory

以

Prompt

形式实时注入

Context

Window

47
。慢变网络确保了底层的物理稳定性，快变上下文提供了瞬时的专业灵活性，两者协同使参数空间
的  KL  漂 移 量 暴 降
47
。
2.

头级稀疏路由与奇异值谱正交解耦

(HRSD)

为了让加挂的专家适配器（
LoRA
）在连续面对多个垂直领域微调时不产生参数冲突，
SNMA

在中高层引入头级稀疏路由重构（
HRSD
）

32
：
●
摒弃传统的词元级拼接路由，使用注意力头级路由器对每个独立头生成的亚表征


实施专一化专家路由，物理切断因注意力机制拼接引发的特征组合碰撞

20
。  ●
在多领域联合优化的目标函数中，引入奇异值正交正则
项。
设不同领域专家适配器矩阵为

，利用奇异值分解（
SVD
）提取其左奇异向量矩阵

，并在损失函数中施加正交化惩罚：


通过强制不同专家适配器在奇异值谱（
Singular

Value

Spectrum
）空间上实现几何正交，杜绝不同专业领域的微调梯度方向相互覆写

34
。
3.

协同在策自蒸馏优化

(S-SDFT)

在对

LoRA

子网及头级路由参数进行微调时，
SNMA

引入了自蒸馏约束

19
：
●
冻结的原始基底模型在挂载快变上下文
（即

FSPP

经验库检索出的黄金示例

）后作为“超级教师”，产生高度连贯且格式合规的对数概率分布

29
。  ●
当前正在接受训练的

LoRA

适配器子网作为“学生”，在仅接收单纯

Query

的在策状态下自由生成轨迹，产生输出概率

29
。  ●
采用基于

Top-20

词元概率重归一化的交叉熵损失，优化并对齐两者的概率分布：


这迫使模型在向垂直领域推理轨迹靠拢时，自发利用其冻结的通用语言流形进行局部纠偏，从而维持通用生成能力的稳健

27
。



## Page 10

4.

奇异值谱空间外科剪枝后处理

(SFAPM)

微调收敛后，
SNMA

摒弃常规

FAPM

仅仅根据数值绝对大小进行一维裁剪的缺陷，将任务向量


重塑为二维矩阵，并执行高维奇异值分解：


我们对每一个奇异谱分量


计算其与原始未微调矩阵对应分量的变动相对
比。
对于那些高频或严重偏离原始预训练奇异值分布的主方向分量，施加如下的非线性指数惩罚衰减：


利用修正后的奇异值谱重构任务向量

，并重新贴回：


通过在奇异值几何流形维度执行的外科剪枝，
SFAPM

实现了只留下对行业事实知识最关键的主特征方向更新，而将对通用底座流形具有扭曲倾向的漂移分量一律无损还原

25
。持续学习标准评估协议与多维基准体系

评估大语言模型在变成专家模型的演进道路上是否发生了知识遗忘，需要一套极其严密
的、
挑战性足够高的标准测试体系

15
。传统的单一静态测试集容易因指令微调阶段的数据泄露而失效，因此，
2025

至

2026

年间业界广泛采用了

TRACE
（
Task

Robustness

and

Adaptation

via

Continual

Evaluation
）

这一多维基准体系

15
。
TRACE

由八个包含

domain-specific

事实知
识、
多语言处
理、
代码生成与高难度数学推理的异质高难度数据集组合而成，统一标准化为

JSON

交互格式，旨在严密拷问模型的“稳定性
-
可塑性”表现

15
。其在持续微调阶段的两个最核心测度指标如下：

1.

阶段


后的综合整体性能

(Overall

Performance,
)
该指标代表模型在历经


个领域的顺序微调后，在所有已学领域及通用评估基准上的算术平均性能，反映了模型的整体适应厚度

15
：



## Page 11


2.

阶段


后的反向知识转移性能

(Backward

Transfer,
)
该指标用以严格衡量模型在学习新领域任务时，对历史已掌握领域的遗忘程
度。
负值越深，代表灾难性遗忘越发具有毁灭性

15
：

在

TRACE

严苛的基准拷问下，顺序全参数微调展现出了可怕的毁灭性失
效。
例如，
LLaMA-2-13B-Chat

模型在连续学习完

TRACE

的八个任务后，其在

GSM8K

上的多步算术逻辑推
理 能 力 从 原 先 体 面 的

瞬间崩塌至几乎无响应的

15
。为了抵御这一崩溃，
TRACE

推荐使用推理增强型持续学习协议（
Reasoning-Augmented

Continual

Learning,

RCL
）

15
。
RCL

强制要求对每一个垂直领域的微调样本进行改造，在问题末尾强制附加两类黄金锚点

15
：一是由高阶模型
（如

GPT-4
）预先离线生成
的、
具有严密链式推理逻辑的

Step-by-step

黄金元理性说明（
Meta-Rationale
）；二是固定的任务特定指引词（
Task-Specific  Cues ）
15
。实验表明，基于

RCL

约束的模型（仅需每个领域


条样
本）
，其整体性能

即可逼近传统顺序微调


条样本的极限，且反向转移指标
甚 至 能 神 奇
地反转为正值
（高
达


左
右）
，大幅保护并延续了通用的逻辑认知能力

15
。为了从

Agent

等实用智能体的维度对专家技能进行安全性与执行可用性的闭环考核，
2026

年的评估体系还引入了“技能覆盖度（
Coverage
，衡量对人类黄金知识点的覆盖比
例）
”、“可执行度（
Executability
，多维考核完整
性、
确定
性、
一致性与可用
性）
”以及“安全性（
Safety
，涵盖隐私风
险、
注入防
护、
系统完整性等多维考
量）
”三大实战评估维度，确保模型既具有专家的硬核能力，又具备生产级可控的底线安全

52
。下表详细展示了多类微调对齐策略在

TRACE

持续演进测试中的性能与遗忘防御表现：

微调与对齐策略组合

综合整体性能
(OP8 )
遗忘率惩罚
(BWT8 )
逻辑推理能力
(GSM8K)  留 存
表现

指 令 遵 循 与 安全 性 衰 减 比 例
全参数顺序微调

(SeqFT)

15

(
基线
)


(
剧 从 初 始
发生显性行
为失 常 ， 指 令 遵 循



## Page 12

烈遗忘
)
断 崖 下 跌 至

15
。
度 下 降
15
。标准

LoRA

微调

2
( 由 于
约束导致较慢
)

( 中
度遗忘
)

算术逻辑跌落
至   左右。
由 于 参 数 更 新局 域 化 ， 安 全 性
指标基本未受损

15
。
DACP  +  SFT  +  DPO
1

(
专
业能 力 极 强 )

(
对齐税引发
)

算术逻辑跌落
至  。
指令遵循优异
，但 泛 化 推 理 能
力在对齐后
发生 二 次 流 失
36
。
SDFT  ( 基 于  7B  架 构 )
28
( 通 用
与专业共存
)

( 近 乎
零遗忘
)

算术逻辑基本维持在初始水
准 的
31
。
指 令 遵 循 提 升
，通识流
形保 持 致 密
15
。
MH-MoE  +
RCL

联合对齐
15
( 最 高性 能 )

(
实
现前 向 正 向 迁 移 )
算术逻辑不
仅未 降 ， 反 而 小 幅
上涨至
15
。
覆 盖 度 与 一 致性 得 分 极 高 ， 安
全防护水准保持稳健

15
。基于

NPU

架构的高效分布式训练与软硬件协同优化

在大语言模型领域化微调与持续学习的工业落地中，除了算法层面的迭代，算力平台的高效利用同样是决定成败的关
键。
随着国产算力及专用

AI

芯片的发展，以华为昇腾（
Ascend
）、
Intel

Gaudi

为代表的神经网络处理器（
NPU
）已成为大规模大模型训练的核心基础设
施。
相比于通用

GPU
，
NPU

采用的脉动阵列（
Systolic

Array
）架构在处理高密度的矩阵乘法（
GEMM
）时具有极高的能效比，其内存带宽利用率往往可突破

90%
（显著优于

GPU

的

70%

~

80%
）。
然而，异构架构也带来了算子映射复
杂、
软件生态不兼容及底层调度效率低的挑
战。
为了最大化释放

NPU

算力并保障训练稳定性，工业界提炼出了一套涵盖软硬件协
同、
分布式并行与混合精度的全栈优化路
径。

1.

NPU

原生适配与算子融合编译

在

PyTorch

生态下，
NPU

的适配通常通过专属插件
（如
华为的

torch_npu
）实现，利用

PyTorch

的

PrivateUse1

机制将

CUDA

算子无缝路由至

NPU

运行时环境，使开发者能够直接在

torch.npu

设备命名空间下运行主流训练库
（如

torchtune
、
LLaMA-Factory
）。
●
图级编译与算子融合（
Operator

Fusion
）：
NPU

在执行低精度
（如

INT4/INT8/FP8
）计算或注意力机制时，频繁的反量化与内存读写会带来严重的

I/O

瓶
颈。
通过算子融合技术
（如
将多头注意力中的

Scale-Dot-Product-Attention

融合成单个算子

FusedSDPA
），能够大幅减少片外内存与片上高速缓存（
SRAM
）之间的数据交
换。
●
DSL

引导的算子生成：在面对新型网络架构
（如
带有长文本特征的

mHC

架
构）
或非标准算子时，由于

NPU

编程模型
（如

AscendC
）门槛极高，容易因

tiling

策略不当导致性能崩
溃。



## Page 13

采用

DSL

引导的高级转译框架
（如

AscendCraft
），可将高抽象的算子描述自动编译为底层约束驱动的

NPU

核，在保证

90.4%

的功能正确性的同时，实现超越

PyTorch

Eager

模式数倍的吞吐加
速。

2.

多维度混合并行与内存节省策略

针对百亿级专家模型的高吞吐分布式训练，单一的数据并行已无法应对参数与激活值占用的物理极限，必须部署异构超节点并行体
系。
●
FSDP2

与超节点协同：通过将

MindSpore

社区的

HyperParallel

架构作为

FSDP2

后端整合进

LLaMA-Factory

等微调框架，模型参
数、
梯度及优化器状态可在

NPU

集群间实现无冗余的分片（
Sharding
），大幅降低单卡显存水
位。
●
序列并行（
Sequence

Parallelism
）与上下文并行（
Context

Parallelism
）：在处理医疗或法律领域的长文本
（如

32K

甚至更高上下
文）
微调时，激活值（
Activations
）会呈二次方暴增，直接撑爆

NPU

的

HBM

显
存。
在

DeepSpeed-NPU

环境下，开启序列并行与上下文并行
（通
过设置

cp_size

核心超参
数）
，可将

LayerNorm
、
Dropout

等算子的输入沿序列维度拆分，从而在不影响数学等价性的前提下，将显存瓶颈均匀稀释至整个多节点卡群
中。
●
ARM-NPU

零拷贝协同：在

ARM

CPU
（如
鲲鹏

920
）与昇腾

NPU

协同

Rar-GPU

异构集群中，利用

UniOpt

框架建立统一的虚拟内存架构，使控制流数据与矩阵计算流在无需经历

PCIe

物理总线拷贝的情况下实现零拷贝（
Zero-copy
）数据共享，系统综合吞吐和显存利用率可提升

20%

~

40%
。

3.

稳健的低精度与混合精度训练（
BF16/FP8
）

为了保障

NPU

脉动阵列在数值运算中的满载运转，混合精度训练必不可
少。
●
BF16

的统治地位与

FP8

演进：
16

位脑浮点（
BF16
）由于其指数级范围与

FP32

完全等同，成为了

NPU

训练专家模型的默认格
式。
而为了进一步压榨算力，
Llama

4

及最新前沿框架开始引入

8

位浮点数（
FP8
）。
FP8

细分为注重前向表达精度的

E4M3

格式与注重反向梯度动态范围的

E5M2

格
式。
●
动态损失缩放与块级缩放（
Block-floating

Scaling
）：由于

FP8

动态范围极窄（
E4M3

范围仅约

），训练极易发生梯度下溢或上溢，导致

Loss

爆炸或变为

NaN
。在

NPU

训练中，必须应用动态损失缩放（
Dynamic

Loss

Scaling
）来动态调整反向传播中的梯度量级，同时利用

microscaling

格式
（如

MXFP8
）对权重和激活进行细粒度的块级缩放，对

normalization
、
softmax

等关键不安全算子原位保留

FP32

精度，以在维持模型收敛精度不退化的前提下，争取最大幅度的硬件精度加
速。

4.

矩阵结构优化器（
Muon
）的工业落地

在

NPU

的训练实践中，传统

AdamW

优化器需要在显存中维护高达参数量

2

倍的一阶和二阶动量状态，导致

HBM

长期处于满载状
态。
为此，昇腾与

MindFormers

社区率先支持了新型矩阵级几何优化器

Muon

(Momentum

Orthogonalized

by

Newton-Schulz)
。
●
Muon

优化器通过对更新量矩阵进行直接的正交化（
Orthogonalization
），从而引导参数沿着良态的几何流形更
新。
●
在

NPU

架构下，
Muon

所需的矩阵正交化运算能够被高度并行化的

Tiling

引擎加
速。
它不仅将优化器状态显存开销削减了近一半，更在百亿级

dense/MoE

模型上展现出了极佳的收敛斜率，与传统的

AdamW

相比，可缩短

30%

~

40%

的收敛

Steps
，为大规模专家化训练开



## Page 14

辟了全新的低显
存、
高能效路
径。

垂直领域专家模型落地工程实践指南

将一个大语言模型从零打造成高可
用、
零遗忘的垂直领域生产级专家，在真实的工程落地中不仅需要顶尖算法的加持，更离不开一整套精细的参
数、
数据与资源管理工艺

2
。
1.

算力与内存的高效调度（
LSP-Offload

实
践）

在企业级部署中，大语言模型微调面临极其苛刻的显存与计算资源屏颈

53
。 在 采 用  FP32  精 度 配
合经典

Adam

优化器时，大模型的内存占用通常高达参数量的倍
53
。这使得即使拥有


显存的消费级旗舰显卡
（如

NVIDIA

RTX

4090

或

AMD

7900XTX
），也仅能勉强运行


极小规模模型的微调，计算资源边界被严重锁死

53
。为了在消费级硬件上实现


以上专家模型的训练，工程上应引入

LSP-Offload

与

Zero-Offload

协同

offloading

框架

53
：  ●
采用

Zero-Offload

将高显存占用的

Adam

优化器状态（
Optimizer

States
）和更新计算（
Update

Steps
）完全离线

offload

到

CPU

侧进行，将

CPU

侧高达数百

GB

乃至

TB

级的内存容量转化为高容错缓存

53
。  ●
在

PCIe

带宽严重受限的普通服务器上，必须部署

LSP-Offload
（基
于学习子空间投影器的

offloading

机
制）

53
。它通过在线学习一个极其高效的数据驱动稀疏压缩投影器，在梯度流跨越

CPU-GPU

的

PCIe

物理总线时，进行无损的高倍率梯度数据压缩通信，彻底打破系统传输带宽的硬件瓶颈，使消费级集群亦能享有近乎原生的微调吞吐速度

53
。
2.

指令微调阶段的“数据规模黄金分割点”

工程微调切忌盲目相信数据规模“多多益善”的直觉

3
：
●
样本下限红线：若微调样本少于


例，模型将不仅无法吸收任何实质性领域知识，还会由于极度过拟合而直接触发灾难性行为崩溃（
Smoke

tests

中直接不响应或输出乱
码）

12
。至少需要准备


例经过严格去
重、
格式对齐的高质量行业样本作为起跑线

3
。  ●
饱和黄金区间：对于大多数垂直领域
（如
医
学、
金
融）
，领域微调的最佳饱和点处于

至

例高多样性专家样本之间

12
。一旦样本量超越
例 ， 模
型在新领域上的边际增益会急剧饱和，而通用常识的遗忘衰退将呈指数级加速

12
。
●
超参数黄金设定：在

LoRA

挂载微调中，推荐将秩（
Rank
）设定在


这一能兼顾容量与稳定性的区间，初始学习率设定在至

的温和区间，单次最大

Epoch

严格限制在


轮，采用早停（
Early

Stopping
）机制防止过拟合

3
。
3.

多阶段自适应流水线的

CI/CD

发布体系

在垂直专家模型的生产级

CI/CD

自动发布流水线中，必须引入通用能力“冒烟测试（
Smoke

Tests



## Page 15

）”作为强门禁控制

3
：  ●
在每一次领域自适应训练完毕后，流水线除了自动核验垂直领域验证集上的

Loss

之外，必须强制对通用评估指标
（如

TRACE
、
MMLU

经典切片
等）
进行自动回滚跑分

3
。
●
回滚机制红线：一旦通识测试跑分相比基座发生超过


的异常滑坡，或在测试用例上手工检查出空字吞吐等隐性失常，流水线必须立刻发出红色警报并自动封锁发布，触发后置的流形外科手术剪枝（
SFAPM
）或重新执行在策

KL

散度约束训练，直至通识防线重新合拢，方能获准进行蓝绿部署上线

3
。综上所述，通过采用创新的

SNMA

协同神经模块化框架，并严格在工程上执行快慢网络物理隔
离、
头级专一路
由、
在策动态自蒸馏以及后置谱空间剪枝相结合的闭环管线工艺，行业实践者能够彻底攻克“微调即遗忘”的百年魔咒，在垂直行业深度演进的坦途上，让模型既拥有无懈可击的专家之长，又完好留存其历经万亿

Token

锤炼所得的通用理性之魂

20
。
Works  cited
1.  Continual  Learning  in  Large  Language  Models:  Methods,  Challenges,  and  Opportunities,  accessed  May  27,  2026,  https://arxiv.org/html/2603.12658v1 2.  Fine-Tuning  Large  Language  Models  (LLMs)  Without  Catastrophic  Forgetting  -
Towards

AI,

accessed

May

27,

2026,
https://pub.towardsai.net/a-guide-to-fine-tuning-large-language-models-llms-without-catastrophic-forgetting-4b2c926f14a4 3.  How  to  Fine-Tune  an  LLM  in  2026:  When,  Why,  and  How  -  AIPortalX,  accessed
May

27,

2026,
https://aiportalx.com/blog/how-to-fine-tune-llm-2026-practical-guide 4.  Fine-Tuning  Techniques  -  Choosing  Between  SFT,  DPO,  and  RFT  (With  a  Guide  to
DPO),

accessed

May

27,

2026,
https://developers.openai.com/cookbook/examples/fine_tuning_direct_preference_optimization_guide 5.  What  is  LLM  alignment?  -  LTS  Global  Digital  Services,  accessed  May  27,  2026,  https://www.gdsonline.tech/what-is-llm-alignment/ 6.  The  Complete  Guide  to  Continual  Learning  and  Catastrophic  Forgetting:  From
EWC

to

Experience

Replay

|

Meta

Intelligence,

accessed

May

27,

2026,
https://www.meta-intelligence.tech/en/insight-continual-learning 7.  [2601.07935]  Towards  Specialized  Generalists:  A  Multi-Task  MoE-LoRA
Framework

for

Domain-Specific

LLM

Adaptation

-

arXiv,

accessed

May

27,

2026,
https://arxiv.org/abs/2601.07935 8.  Mechanistic  Analysis  of  Catastrophic  Forgetting  in  Large  Language  Models
During

Continual

Fine-tuning

-

arXiv,

accessed

May

27,

2026,
https://arxiv.org/html/2601.18699v1 9.  Catastrophic  Forgetting  In  LLMs  -  Cobus  Greyling  -  Medium,  accessed  May  27,
2026,
https://cobusgreyling.medium.com/catastrophic-forgetting-in-llms-bf345760e6e2 10.  [2308.08747]  An  Empirical  Study  of  Catastrophic  Forgetting  in  Large  Language
Models

During

Continual

Fine-tuning

-

arXiv,

accessed

May

27,

2026,




## Page 16

https://arxiv.org/abs/2308.08747 11.  Catastrophic  Forgetting  in  AI:  Why  Neural  Networks  Lose  Memory  -  Practical
DevSecOps,

accessed

May

27,

2026,
https://www.practical-devsecops.com/glossary/catastrophic-forgetting/ 12.  The  Hidden  Crisis  in  LLM  Fine-Tuning:  When  Your  Model  Silently  Forgets
Everything,

accessed

May

27,

2026,
https://ai.rundatarun.io/Emerging+Trends/the-hidden-crisis-in-llm-fine-tuning-catastrophic-forgetting 13.  Your  Fine-Tuned  Model  Forgot  Everything  It  Knew  —  The  State  of  Catastrophic
Forgetting

in

2026

:

r/learnmachinelearning

-

Reddit,

accessed

May

27,

2026,
https://www.reddit.com/r/learnmachinelearning/comments/1rq3sf4/your_finetuned_model_forgot_everything_it_knew/ 14.  Your  Fine-Tuned  Model  Forgot  Everything  It  Knew.  Here's  Why  -  Hugging  Face
Forums,

accessed

May

27,

2026,
https://discuss.huggingface.co/t/your-fine-tuned-model-forgot-everything-it-knew-here-s-why/174133 15.  TRACE  Benchmark  Datasets  -  Emergent  Mind,  accessed  May  27,  2026,  https://www.emergentmind.com/topics/trace-benchmark-datasets 16.  How  are  you  handling  catastrophic  forgetting  in  multi-domain  LLM  fine-tuning
pipelines?,

accessed

May

27,

2026,
https://www.reddit.com/r/mlops/comments/1rnhoa6/how_are_you_handling_catastrophic_forgetting_in/ 17.  ixi-GEN:  Efficient  Industrial  sLLMs  through  Domain  Adaptive  Continual  Pretraining
-

ACL

Anthology,

accessed

May

27,

2026,
https://aclanthology.org/2025.emnlp-industry.165.pdf 18.  What  is  Catastrophic  forgetting  in  the  context  of  LLMs?  Why  its  happening?  How
to

mitigate

it?

|

by

Moe

Moazzami

|

Medium,

accessed

May

27,

2026,
https://medium.com/@moe.moazzami/what-is-catastrophic-forgetting-in-the-context-of-llms-why-its-happening-how-to-mitigate-it-091dc4d388fd 19.  Self-Distillation  Enables  Continual  Learning  -  arXiv,  accessed  May  27,  2026,  https://arxiv.org/html/2601.19897v1 20.  Multi-Head  Attention  as  a  Source  of  Catastrophic  Forgetting  in  MoE  Transformers  -  arXiv,  accessed  May  27,  2026,  https://arxiv.org/abs/2602.12587 21.  Mitigating  Catastrophic  Forgetting  in  Large  Language  Models  with
Forgetting-aware

Pruning

-

arXiv,

accessed

May

27,

2026,
https://arxiv.org/html/2509.08255v1 22.  Efficient  Industrial  sLLMs  through  Domain  Adaptive  Continual  Pretraining  -  arXiv,  accessed  May  27,  2026,  https://arxiv.org/pdf/2507.06795 23.  Learning  Dynamics  in  Continual  Pre-Training  for  Large  Language  Models  -  arXiv,  accessed  May  27,  2026,  https://arxiv.org/html/2505.07796v1 24.  Mitigating  Catastrophic  Forgetting  in  Large  Language  Models  with
Forgetting-aware

Pruning

-

ACL

Anthology,

accessed

May

27,

2026,
https://aclanthology.org/2025.emnlp-main.1108.pdf 25.  Mitigating  Catastrophic  Forgetting  in  Large  Language  Models  with
Forgetting-aware

Pruning

|

OpenReview,

accessed

May

27,

2026,




## Page 17

https://openreview.net/forum?id=fHvh913U1H 26.  Modern_LLM_Fine-Tuning_Playbook  |  PDF  -  Scribd,  accessed  May  27,  2026,  https://www.scribd.com/document/1011209205/Modern-LLM-Fine-Tuning-Playbook 27.  SELF-DISTILLATION  ENABLES  CONTINUAL  LEARNING  -  OpenReview,  accessed  May  27,  2026,  https://openreview.net/pdf?id=HlWA3V6iKF 28.  SDFT:  Self-Distillation  Enables  Continual  Learning,  accessed  May  27,  2026,  https://self-distillation.github.io/SDFT 29.  MIT's  new  fine-tuning  method  lets  LLMs  learn  new  skills  without  losing  old  ones,
accessed

May

27,

2026,
https://venturebeat.com/orchestration/mits-new-fine-tuning-method-lets-llms-learn-new-skills-without-losing-old 30.  [2601.19897]  Self-Distillation  Enables  Continual  Learning  -  arXiv,  accessed  May  27,  2026,  https://arxiv.org/abs/2601.19897 31.  Self-Distillation  Fine-Tuning  (SDFT)  -  Tinker  Docs,  accessed  May  27,  2026,  https://tinker-docs.thinkingmachines.ai/cookbook/recipes/sdft/ 32.  Multi-Head  Attention  as  a  Source  of  Catastrophic  Forgetting  in  MoE  Transformers  -  arXiv,  accessed  May  27,  2026,  https://arxiv.org/html/2602.12587v1 33.  Multi-Head  Attention  as  a  Source  of  Catastrophic  Forgetting  in  MoE  Transformers  -  arXiv,  accessed  May  27,  2026,  https://arxiv.org/pdf/2602.12587 34.  Anrui  Chen  -  CatalyzeX,  accessed  May  27,  2026,  https://www.catalyzex.com/author/Anrui%20Chen 35.  TRACE:  A  Comprehensive  Benchmark  for  Continual  Learning  in  Large  Language
Models,

accessed

May

27,

2026,
https://www.semanticscholar.org/paper/TRACE%3A-A-Comprehensive-Benchmark-for-Continual-in-Wang-Zhang/a64067c6c4286fc60f4430829ae6b18519c088e3 36.  LLM  Fine-Tuning:  Best  Techniques,  Comparisons  &  Use  Cases  -  Mobisoft  Infotech,
accessed

May

27,

2026,
https://mobisoftinfotech.com/resources/blog/ai-development/llm-fine-tuning-techniques-comparisons-applications 37.  RLHF  vs  DPO:  Choosing  the  Right  LLM  Alignment  -  SyncSoft.AI,  accessed  May  27,  2026,  https://www.syncsoft.ai/en/blog/rlhf-vs-dpo-llm-alignment 38.  How  is  RLHF  different  from  DPO  at  a  high  level?  |  Sebastian  Raschka,  PhD,  accessed  May  27,  2026,  https://sebastianraschka.com/faq/docs/rlhf-vs-dpo.html 39.  KTO:  Model  Alignment  as  Prospect  Theoretic  Optimization,  accessed  May  27,
2026,
https://lrjconan.github.io/UBC-EECE571F-DL-Structures/assets/slides_2025/paper_15_kto.pdf 40.  DPO  vs  PPO  for  LLMs:  Key  Differences  &  Use  Cases  -  Clarifai,  accessed  May  27,  2026,  https://www.clarifai.com/blog/dpo-vs-ppo 41.  [2402.01306]  KTO:  Model  Alignment  as  Prospect  Theoretic  Optimization  -  arXiv,  accessed  May  27,  2026,  https://arxiv.org/abs/2402.01306 42.  RLHF  and  alternatives:  KTO  -  Argilla,  accessed  May  27,  2026,  https://argilla.io/blog/mantisnlp-rlhf-part-7/



## Page 18

43.  Vinija's  Notes  •  LLM  Alignment,  accessed  May  27,  2026,  https://vinija.ai/concepts/llm-alignment/ 44.  Kahneman-Tversky  Optimization(KTO):  Revolutionizing  Language  Model  Training
with

Prospect

Theory

|

by

Yatin

Arora

|

Medium,

accessed

May

27,

2026,
https://medium.com/@SpielmitDaten/kahneman-tversky-optimization-kto-revolutionizing-language-model-training-with-prospect-theory-99f30c50481e 45.  Swepo:  Simultaneous  Weighted  Preference  Optimization  for  Group  Contrastive  Alignment,  accessed  May  27,  2026,  https://arxiv.org/html/2412.04628v3 46.  SWEPO:  SIMULTANEOUS  WEIGHTED  PREFERENCE  OP-  TIMIZATION  FOR  GROUP
CONTRASTIVE

ALIGNMENT

-

OpenReview,

accessed

May

27,

2026,
https://openreview.net/pdf?id=97a05ePu0O 47.  Learning,  Fast  and  Slow:  Towards  LLMs  That  Adapt  Continually  [R]  -  Reddit,
accessed

May

27,

2026,
https://www.reddit.com/r/MachineLearning/comments/1tbvsxo/learning_fast_and_slow_towards_llms_that_adapt/ 48.  Fine-Tuning  Large  Language  Models  (LLMs)  Without  Catastrophic  Forgetting  |
Towards

AI,

accessed

May

27,

2026,
https://towardsai.net/p/machine-learning/fine-tuning-large-language-models-llms-without-catastrophic-forgetting 49.  MEMORY  Research  Area  Summary,  accessed  May  27,  2026,  https://papers.lunadong.com/area/memory 50.  APT:  Improving  Specialist  LLM  Performance  with  Weakness  Case  Acquisition  and
Iterative

Preference

Training

-

ACL

Anthology,

accessed

May

27,

2026,
https://aclanthology.org/2025.findings-acl.1079.pdf 51.  TRACE:  A  Comprehensive  Benchmark  for  Continual  Learning  in  Large  Language  Models,  accessed  May  27,  2026,  https://openreview.net/forum?id=xelrLobW0n 52.  SkillLearnBench:  Benchmarking  Continual  Learning  Methods  for  Agent  Skill
Generation

on

Real-World

Tasks

-

arXiv,

accessed

May

27,

2026,
https://arxiv.org/html/2604.20087v1 53.  Practical  offloading  for  fine-tuning  LLM  on  commodity  GPU  via  learned  subspace  projectors,  accessed  May  27,  2026,  https://arxiv.org/html/2406.10181v1
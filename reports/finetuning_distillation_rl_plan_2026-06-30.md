# 当前微调进展与下一步计划

日期：2026-06-30

## 1. 当前微调进展

项目已经从早期框架搭建进入“补高质量样本、扩大蒸馏、再接强化学习”的阶段。这里需要把两条模型线分清：Qwen3.6-27B 当前主要是本地 RAG/发布线，已有 `Qwen3.6-27B-RAG` 本地发布测试记录；当前微调主线则是 Qwen3.6-35B-A3B，远程模型路径以 `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8` 为主。监督微调入口已经具备，主要脚本是 `training/qwen_sft_peft.py`；强化学习入口也已经具备，主要脚本是 `training/grpo_trainer.py`、`training/agentic_grpo_trainer.py` 以及 35B 专用的 GRPO/RLVR 辅助脚本。

近期 commit 口径如下：

- `8a5f2ce`：加入 `data/generated/quantum_finetune_verified_chat_sft_dedup_1k/` 数据集，并加入 1k LoRA SFT 的 NPU 安全启动路径。
- `613209d`：修复 1k SFT 的 NPU loss-step OOM 和 full-epoch 训练问题。
- `74cdf82`：在 final eval 前保存 adapter，并加强 eval 的 NPU OOM 防护。
- `0b92cf9`：加入 495 条 holdout 上的 base-vs-adapter pass@1 评测 harness。
- `a9def35`：修复 native Transformers 5.6.0 与 35B sharding 场景下的 base-vs-adapter eval。

也就是说，近期已提交历史里 `dedup-1k` 数据集和 495 holdout 评测已经落地；35B-A3B 的 dedup-1k LoRA SFT 启动脚本和 6 月 22 日运行记录属于当前工作区里的最新执行线，还需要后续纳入正式提交。

数据侧已经形成几类可复用资产：

- 当前最重要的 1k 问题-代码微调样本：`data/generated/quantum_finetune_verified_chat_sft_dedup_1k/`，包含 `train_chatml.jsonl` 1000 条和 `eval_chatml.jsonl` 495 条。该数据集从 `data/generated/quantum_finetune_verified_chat_sft/` 的 10000 条训练样本中做 number-collapsed signature 去重和分层抽样得到，manifest seed 为 `20260622`，train/eval 的 `example_id` 与 signature overlap 均为 0，覆盖 83 个任务 family。
- 原始量子验证 SFT 切分：`data/generated/quantum_finetune_verified_chat_sft/` 和 `data/generated/qwen36_quantum_verified_split_10000_495_v3`，作为 1k 数据集的来源和扩展池。
- 领域混合 curriculum：`data/generated/qwen36-27b-domain-expert-curriculum-v1`，历史上用于 27B 领域专家/RAG 相关评测口径，也可作为后续保持通用代码能力的参考数据源。
- 旧一轮高质量蒸馏样本：`data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203`，包含 203 条可作为蒸馏 SFT 种子的数据。

因此，当前主要瓶颈不是训练脚本缺失，而是要在已经有 1000 条问题-代码 SFT 样本的基础上，继续补充更大规模、更难、更可验证的高质量蒸馏样本。下一阶段要优先把 hard-QA 样本生成、教师回答、清洗、格式转换和质量门串起来，再和 35B-A3B 的 LoRA SFT / GRPO 路线衔接。

## 2. 下一步：生成蒸馏样本

新一轮样本生成的提示词已经放在 `data/generate/hardqa/`：

- `data/generate/hardqa/prompt_01_hardened_rigor.txt`：面向严格数学、量子算法、量子信息和容错量子计算推导。
- `data/generate/hardqa/prompt_02_grounded_innovation.txt`：面向物理约束下的创新型量子研究问答，强调 classical-to-quantum paradigm mapping 和物理可行性检查。

新一批蒸馏样本建议统一落在：

`data/generated/hardqa-quantum-v1/`

该目录当前为空，适合作为下一轮 hard-QA 原始样本、教师回答、清洗报告、ChatML SFT 切分和 manifest 的工作区。建议产物结构如下：

- `raw_samples.xml` 或 `raw_samples.jsonl`：由 hard-QA prompt 生成的原始样本。
- `teacher_responses.jsonl`：教师模型补全后的问答/推理/答案样本。
- `high_quality.jsonl`：经过格式、去重、物理约束和质量过滤后的蒸馏样本。
- `train_chatml.jsonl` / `eval_chatml.jsonl`：供 SFT 直接使用的 ChatML 切分。
- `manifest.json`：记录样本数量、来源 prompt、过滤规则、hash、train/eval 切分策略。
- `quality_report.json`：记录拒绝原因、重复率、格式错误率、物理约束违规率和代码可运行率。

第一批目标建议生成 500-1000 条 hard-QA 原始样本，经过 XML/schema 解析、去重、物理约束检查、数学表达式检查、代码块可运行性检查后，保留第一版高质量蒸馏集。样本内容应覆盖 QSP/QET、LCU/block encoding、Hamiltonian simulation、surface code、magic-state distillation、qLDPC、QAOA/VQE、quantum channel、shadow tomography、量子软件工程与测试修复等方向。

## 3. 训练路线：蒸馏、强化学习、混合训练

第一步是蒸馏 SFT。将 `data/generated/hardqa-quantum-v1/` 的新样本，与当前 1000 条问题-代码样本 `data/generated/quantum_finetune_verified_chat_sft_dedup_1k/`、原始 10k 量子验证池和 203 条高质量旧蒸馏集按比例混合，训练 Qwen3.6-35B-A3B LoRA/QLoRA adapter。35B-A3B 的当前执行脚本是 `scripts/asi2_dedup_1k_lora_launch.sh`，训练前会将 W8A8 MoE 权重解压到 bf16 训练目录，并把输出、日志和小时级 checkpoint 写到 `/root/work/filestorage` 这类持久化 NAS 路径。目标是提高模型在量子算法推导、严谨回答、代码生成和可验证解释上的稳定性。

第二步是强化学习。以蒸馏 SFT adapter 作为初始化，继续运行 GRPO/RLVR。奖励信号不做泛泛的文本偏好，而是围绕可执行测试、Python/量子框架语法正确性、接口一致性、物理约束合规性、答案简洁度和 verifier 通过率构造。强化学习训练入口优先使用 `training/grpo_trainer.py`，复杂 agentic 轨迹再使用 `training/agentic_grpo_trainer.py`。

第三步是强化学习和蒸馏混合训练。RL 更新过程中保留一部分蒸馏 replay batch，训练目标采用“RL reward + distillation loss + KL/格式约束”的组合，避免模型在追求奖励时丢失严谨长答案、软件工程习惯和领域知识。这个阶段的核心不是单纯把 reward 拉高，而是让模型同时保持：量子正确性、代码可执行性、回答结构稳定性和通用软件工程能力。

## 4. 近期里程碑

1. 填充 `data/generated/hardqa-quantum-v1/` 第一批 hard-QA 样本，并生成 manifest。
2. 跑质量门：格式解析、去重、物理约束检查、代码块语法检查、样本长度和主题分布统计。
3. 转换为 `train_chatml.jsonl` / `eval_chatml.jsonl`，并和 `data/generated/quantum_finetune_verified_chat_sft_dedup_1k/` 做混合 SFT 配方。
4. 在本地先做数据和脚本 smoke，确认训练文件可读、字段完整、样本无明显污染；同时保留 495 条 dedup holdout 作为 base-vs-adapter pass@1 评测口径。
5. 同步到 Huanxin `AI` / 可用 ASI 环境，先跑 35B-A3B 短 LoRA smoke，检查 loss、保存 adapter、eval 不崩。
6. 在资源窗口允许时，推进 SFT -> GRPO -> 蒸馏/RL 混合训练的完整迭代。

## 5. 成功标准

本轮不只看训练 loss。主要成功标准包括：

- held-out 量子任务 pass@1 提升。
- 代码块语法正确率和可执行率提升。
- 物理约束违规率下降，例如 no-cloning、unitarity、CPTP、no-signaling 等问题被显式规避。
- 软件工程回放集无明显退化，尤其是测试生成、bug 修复、接口保持和多文件修改任务。
- 蒸馏样本质量报告可复现，训练数据和评测数据保持清晰隔离。

下一步最小可执行动作是先产出 `data/generated/hardqa-quantum-v1/` 的第一版样本与质量报告，然后用它驱动第一轮蒸馏 SFT smoke。
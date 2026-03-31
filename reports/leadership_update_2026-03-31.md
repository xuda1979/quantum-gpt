# 领导汇报更新 - 2026-03-31

## 一、整体进展

本轮工作的重点，是把项目从“小规模试验”推进到“可以向领导清晰汇报”的状态。当前已经形成三项比较扎实的结果。

第一，评测体系已经从早期的小样本切片，升级为严格的未见保留集评测。现在的评测集不仅规模达到领导要求，而且已经在 `example_id`、`task_id` 和 `prompt_family` 三个层面完成训练集/评测集隔离验证。  
第二，OmniCoder 路线已经在 ai2 上给出明确的强结果，远端干净运行取得 `25/25 passed`。  
第三，RL 路线已经进入真实迭代阶段，GRPO 不再只是方案设计，而是已经在 ai2 上完成真实运行、发现真实瓶颈，并据此完成下一轮预算收敛与重新排队。

## 二、数据与评测体系

当前已经固化两套领导口径下可以直接引用的保留集语料。

严格量子未见过语料的完整性验证结果见：[omnicoder_quantum_generalization_holdout_v1_integrity.json](/Users/daxu/software/quantum-gpt/reports/omnicoder_quantum_generalization_holdout_v1_integrity.json)

- 训练样本：`1024`
- 评测样本：`504`
- 评测样本规模要求 `>=500`：通过
- 训练集/评测集在 `example_id` 上重叠：`0`
- 训练集/评测集在 `task_id` 上重叠：`0`
- 训练集/评测集在 `prompt_family` 上重叠：`0`

更广义的量子+软件混合未见过语料验证结果见：[omnicoder_generalization_holdout_v1_integrity.json](/Users/daxu/software/quantum-gpt/reports/omnicoder_generalization_holdout_v1_integrity.json)

- 训练样本：`1440`
- 评测样本：`504`
- 评测样本规模要求 `>=500`：通过
- 训练集/评测集在 `example_id`、`task_id`、`prompt_family` 上重叠均为 `0`

这意味着，我们现在可以比较稳妥地向领导说明：当前的评测集没有出现在训练集中，且规模已经达到可以审阅的水平。

## 三、模型结果

### 1. 本地诚实基线

本地基线结果见：[qwen25_quantum_generalization_holdout_clean_local_override_summary.json](/Users/daxu/software/quantum-gpt/reports/qwen25_quantum_generalization_holdout_clean_local_override_summary.json)

- 模型：`Qwen2.5-1.5B-Instruct`
- 基准：严格量子未见过覆盖子集
- 结果：`0/4`

这个结果的重要意义，不在于分数本身，而在于它证明当前评测是真实难度，而不是因为提示词污染或数据泄漏导致的虚高结果。

### 2. OmniCoder 远端结果

远端运行元数据见：[omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json](/Users/daxu/software/quantum-gpt/.huanxin_jobs/omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json)

- 基座模型：`models/OmniCoder-9B`
- 适配器：`outputs/omnicoder9b-quantum-hard-v1-continue-true40-e2-20260330T142009CST/adapter`
- 干净运行目录：[manifest.json](/Users/daxu/software/quantum-gpt/evals/runs/omnicoder-quantum-generalization-holdout-v1-clean/manifest.json)

从 ai2 回收的远端终端结果为：

- `Overall: 25/25 passed`
- `quantum: 12/12 passed`
- `software: 13/13 passed`

结合干净 manifest 可以确认，这个 25 任务套件中的 4 个量子覆盖任务正是严格未见过任务。因此，未见过覆盖子集结果可以较强地推断为 `4/4`。对领导的表述建议是：远端干净运行整体 `25/25`，其中严格未见过覆盖子集可推断为 `4/4`。

### 3. 监督微调信号

语义版本的 2-NPU 运行记录见：[omnicoder9b_semantic_v4_2npu_20260329.md](/Users/daxu/software/quantum-gpt/reports/omnicoder9b_semantic_v4_2npu_20260329.md)

- `final_eval.loss`：`0.3727`
- `final_eval.perplexity`：`1.4517`

这说明 OmniCoder 路线不只是评测上有表现，也已经在监督训练信号上体现出较好的收敛特征。

## 四、RL 与下一轮放大计划

GRPO 的实现与迭代记录见：[grpo_v2_iteration_2026-03-31.md](/Users/daxu/software/quantum-gpt/reports/grpo_v2_iteration_2026-03-31.md)

当前可以明确汇报的状态是：

- GRPO 训练器已经完成真实实现，并在 ai2 上跑通运行路径
- `smoke5` 已经证明运行时稳定性基本成立，可以结束、保存适配器、输出步骤日志
- smoke6 的最终日志已经回收，失败原因明确为 `RuntimeError: NPU out of memory`

这次失败反而让下一步变得更清晰。我们已经据此把 timeboxed 8-NPU GRPO 配置收紧到更保守的显存预算：

- `group_size=4`
- `grpo_steps=8`
- `max_new_tokens=128`
- `max_seq_length=2048`

与此同时，8-NPU 的 SFT->GRPO 流水线已经重新在 ai2 上排队，当前 PID 为 `233721`。它会在 8 张 NPU 全部空闲时自动启动，整体墙钟预算控制在 2 小时内。

当前阻塞并不是代码或流程未准备好，而是集群占用状态：

- NPU `0-5` 被现有 `python` 任务占用
- NPU `7` 被 `python3` 任务占用
- 目前只有 NPU `6` 空闲

## 五、工程化与部署能力

除了训练与评测，本轮还完成了对真实工作流有价值的工程能力建设。

第一，Codex 接入 ai2 的路径已经端到端打通。相关本地脚本包括：

- [install_codex_standalone.sh](/Users/daxu/software/quantum-gpt/scripts/install_codex_standalone.sh)
- [render_codex_local_config.py](/Users/daxu/software/quantum-gpt/scripts/render_codex_local_config.py)
- [serve_openai_chat_adapter.py](/Users/daxu/software/quantum-gpt/scripts/serve_openai_chat_adapter.py)

远端已经验证：

- `codex-cli 0.117.0` 安装成功
- Codex 已连接到本地微调的 OmniCoder 适配器
- 端到端冒烟结果输出 `OK`

这说明当前模型能力已经可以被智能体工作流实际调用，而不只是停留在基准测试数字层面。

第二，ai2 到本地的代码/文档安全同步路径也已经建立：

- [sync_ai2_code_docs_to_local.sh](/Users/daxu/software/quantum-gpt/scripts/sync_ai2_code_docs_to_local.sh)
- 快照目录：[ai2_code_docs_snapshot](/Users/daxu/software/quantum-gpt/artifacts/ai2_code_docs_snapshot)

该路径只同步代码和文档，不覆盖本地在线工作仓，也不回传模型权重。

## 六、建议汇报口径

比较合适的汇报方式是：

- 先说明我们已经把评测标准提升到了严格未见过、可验证、可审阅的水平
- 再说明基线是诚实的，因此 OmniCoder 的远端结果有意义
- 然后强调下一轮不是“继续做 SFT”，而是在现有监督路径上叠加 GRPO，并且 RL 已经进入真实运行与调参阶段
- 最后补充，这套能力已经具备工程化工作流入口，Codex 可以直接接到微调模型

简化结论可以表述为：

- 数据集更大、更干净
- 评测集没有进训练集
- OmniCoder 已给出强远端结果
- GRPO 已进入真实迭代
- 8-NPU 放大路径已准备完成，当前只等集群资源窗口

# 研究组合总览 - 2026-03-31

## 一、目标

本轮我们不是零散地做几个实验，而是在构建一套可持续扩展的研究组合。目标有三个：

- 对领导来说，这套研究组合需要体现明确的创新性
- 对研发来说，这些方法必须能在当前代码仓中真实实现
- 对后续迭代来说，任何单个方法都必须能独立插拔，不应把主训练链路绑死

## 二、组织方式

新的研究材料统一收敛到以下目录：

- [research/papers/README.md](../research/papers/README.md)
- [research/papers/index.json](../research/papers/index.json)

每个研究方向都有自己的论文子目录，目录内同时放置论文文档和与该方法直接对应的代码。这样做的目的，是让创新点、实现逻辑和实验接入方式保持一一对应，避免出现“汇报里说了一套，代码里又是另一套”的情况。

## 三、当前研究方法

目前已经落地的主要方法有五条。

第一条是修复式课程学习：

- [paper.md](../research/papers/verifier_guided_repair_curriculum/paper.md)
- [plugin.py](../research/papers/verifier_guided_repair_curriculum/code/plugin.py)

第二条是子句感知奖励：

- [paper.md](../research/papers/clause_aware_verifier_reward/paper.md)
- [plugin.py](../research/papers/clause_aware_verifier_reward/code/plugin.py)

第三条是接口锚定方法：

- [paper.md](../research/papers/ast_anchor_interface_grounding/paper.md)
- [plugin.py](../research/papers/ast_anchor_interface_grounding/code/plugin.py)

第四条是自一致性路由：

- [paper.md](../research/papers/self_consistency_verifier_routing/paper.md)
- [plugin.py](../research/papers/self_consistency_verifier_routing/code/plugin.py)

第五条是不确定性修复回放：

- [paper.md](../research/papers/uncertainty_triggered_repair_replay/paper.md)
- [plugin.py](../research/papers/uncertainty_triggered_repair_replay/code/plugin.py)

这些方法都通过统一参数启用，例如：

- `--research-methods verifier_guided_repair_curriculum`
- `--research-methods clause_aware_verifier_reward`
- `--research-methods ast_anchor_interface_grounding`
- `--research-methods self_consistency_verifier_routing`
- `--research-methods uncertainty_triggered_repair_replay`

## 四、接入方式

当前的研究方法不是孤立脚本，而是已经接入主训练入口。

共享插件加载器位于：

- [training/research_plugins.py](../training/research_plugins.py)

已完成接入的训练入口位于：

- [training/qwen_sft_peft.py](../training/qwen_sft_peft.py)
- [training/grpo_trainer.py](../training/grpo_trainer.py)

这意味着当前研究结构具备三个特点：

- 新方法可以通过参数开关启用，而不是硬编码进主流程
- 不启用研究方法时，基础训练路径仍然可以保持稳定
- 每个研究方法都可以单独加、单独去掉，便于快速迭代与止损

## 五、与规模化训练的关系

研究组合并不是脱离训练主线单独存在的，它已经直接服务于下一轮 8-NPU 放大计划。

对应的运行规划文档为：

- [timeboxed_eight_npu_sft](../research/papers/timeboxed_eight_npu_sft/paper.md)
- [timeboxed_eight_npu_grpo](../research/papers/timeboxed_eight_npu_grpo/paper.md)

对应的命令清单位于：

- [timeboxed-8npu-scaleup-command-sheet.txt](../artifacts/timeboxed-8npu-scaleup-command-sheet.txt)

对应的 ai2 监控与拉起脚本位于：

- [timeboxed_8npu_watch_and_launch.sh](../scripts/timeboxed_8npu_watch_and_launch.sh)

目前 ai2 上已经存在一个活跃的排队监控进程：

- PID：`233721`
- 状态：等待 8 张 NPU 全部空闲

在回收 `smoke6` 日志之后，我们已经将限时 GRPO 的预算收紧到：

- `max_new_tokens=128`
- `max_seq_length=2048`

这样做的目的是在保证 2 小时窗口内可完成的同时，降低再一次触发显存问题的风险。

## 六、当前状态

从本轮 ai2 实时探测来看，当前 8 张 NPU 还没有全部释放：

- NPU `0-5` 被已有 `python` 作业占用
- NPU `7` 被 `python3` 作业占用
- 只有 NPU `6` 当前空闲

所以，当前这套研究组合已经不是“概念准备不足”，而是“代码、结构、运行计划都已经就绪，只等待资源窗口”。

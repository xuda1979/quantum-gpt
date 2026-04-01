# 项目进展更新 - 2026-03-31

## 一、结论摘要

截至 2026-03-31，项目已经形成三项可直接核验的进展：

1. 已建立严格未见 holdout 评测体系，评测数据规模达到可审阅水平，且 train/eval 在 `example_id`、`task_id`、`prompt_family` 三个层面完成零重叠验证。
2. 微调后的 OmniCoder 路线已在 ai2 上完成干净远端运行，取得整体 `25/25 passed` 的结果；对应的严格未见量子子集由固定 manifest 明确界定，可直接定位到原始任务文件。
3. Codex 已在 ai2 上完成安装，并已接通本地微调模型服务；端到端 smoke 已返回 `OK`，说明模型能力已经具备实际 agent 工作流入口。

## 二、评测与数据资产

### 1. 严格量子未见 holdout

严格量子未见 holdout 的完整性验证报告在：

- [omnicoder_quantum_generalization_holdout_v1_integrity.json](/Users/daxu/software/quantum-gpt/reports/omnicoder_quantum_generalization_holdout_v1_integrity.json)

可直接核验的关键事实：

- train 文件：`data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl`
- eval 文件：`data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl`
- 训练样本：`1024`
- 评测样本：`504`
- `example_id` 重叠：`0`
- `task_id` 重叠：`0`
- `prompt_family` 重叠：`0`
- 完整性结论：`ok: true`

严格未见量子 benchmark 文件在：

- [quantum_generalization_holdout_v1.txt](/Users/daxu/software/quantum-gpt/evals/benchmarks/quantum_generalization_holdout_v1.txt)

对应的干净 run-dir manifest 在：

- [manifest.json](/Users/daxu/software/quantum-gpt/evals/runs/omnicoder-quantum-generalization-holdout-v1-clean/manifest.json)

### 2. 混合未见 holdout

量子+软件混合 holdout 的完整性验证报告在：

- [omnicoder_generalization_holdout_v1_integrity.json](/Users/daxu/software/quantum-gpt/reports/omnicoder_generalization_holdout_v1_integrity.json)

可直接核验的关键事实：

- train 文件：`data/generated/omnicoder-generalization-holdout-v1/train.jsonl`
- eval 文件：`data/generated/omnicoder-generalization-holdout-v1/eval.jsonl`
- 训练样本：`1440`
- 评测样本：`504`
- `example_id` 重叠：`0`
- `task_id` 重叠：`0`
- `prompt_family` 重叠：`0`
- 完整性结论：`ok: true`

## 三、模型结果

### 1. 本地诚实基线

本地 Qwen 基线的汇总文件在：

- [qwen25_quantum_generalization_holdout_clean_local_override_summary.json](/Users/daxu/software/quantum-gpt/reports/qwen25_quantum_generalization_holdout_clean_local_override_summary.json)

对应 run-dir 资产在：

- [manifest.json](/Users/daxu/software/quantum-gpt/evals/runs/qwen25-quantum-generalization-holdout-clean-local/manifest.json)
- [scorecard.json](/Users/daxu/software/quantum-gpt/evals/runs/qwen25-quantum-generalization-holdout-clean-local/scorecard.json)

可直接核验的结果：

- 模型：`Qwen2.5-1.5B-Instruct`
- 基准：`evals/benchmarks/quantum_generalization_holdout_v1.txt`
- 结果：`0/4`

这条基线说明当前严格未见量子 holdout 具备真实区分度。

### 2. 微调 OmniCoder 远端结果

对应远端运行元数据在：

- [omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json](/Users/daxu/software/quantum-gpt/.huanxin_jobs/omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json)

对应干净 run-dir manifest 在：

- [manifest.json](/Users/daxu/software/quantum-gpt/evals/runs/omnicoder-quantum-generalization-holdout-v1-clean/manifest.json)

对应模型路径为：

- 基座模型：`models/OmniCoder-9B`
- 适配器：`outputs/omnicoder9b-quantum-hard-v1-continue-true40-e2-20260330T142009CST/adapter`

已记录的远端运行结果为：

- `Overall: 25/25 passed`
- `quantum: 12/12 passed`
- `software: 13/13 passed`

其中，严格未见量子子集的任务集合由以下文件固定：

- [quantum_generalization_holdout_v1.txt](/Users/daxu/software/quantum-gpt/evals/benchmarks/quantum_generalization_holdout_v1.txt)
- [manifest.json](/Users/daxu/software/quantum-gpt/evals/runs/omnicoder-quantum-generalization-holdout-v1-clean/manifest.json)

因此，项目当前已经具备一条从“严格未见 benchmark 定义”到“远端干净运行结果”的完整证据链。

### 3. 监督微调信号

语义版本 2-NPU 训练记录在：

- [omnicoder9b_semantic_v4_2npu_20260329.md](/Users/daxu/software/quantum-gpt/reports/omnicoder9b_semantic_v4_2npu_20260329.md)

可直接核验的训练信号：

- `final_eval.loss = 0.3727`
- `final_eval.perplexity = 1.4517`

这说明 OmniCoder 路线不仅在评测端有结果，也已经在监督训练信号上表现出清晰收敛。

## 四、强化学习与下一轮放大

GRPO 迭代记录在：

- [grpo_v2_iteration_2026-03-31.md](/Users/daxu/software/quantum-gpt/reports/grpo_v2_iteration_2026-03-31.md)

当前可直接汇报的状态为：

- GRPO 训练器已经完成真实实现并跑通运行路径
- 训练迭代记录、参数收敛和后续放大计划均已落到可追溯文件
- 8-NPU pipeline 已完成排队与命令准备

相关运行规划与命令资产在：

- [timeboxed-8npu-scaleup-command-sheet.txt](/Users/daxu/software/quantum-gpt/artifacts/timeboxed-8npu-scaleup-command-sheet.txt)
- [timeboxed_8npu_watch_and_launch.sh](/Users/daxu/software/quantum-gpt/scripts/timeboxed_8npu_watch_and_launch.sh)

## 五、工程化能力

### 1. Codex on ai2

本地辅助脚本在：

- [install_codex_standalone.sh](/Users/daxu/software/quantum-gpt/scripts/install_codex_standalone.sh)
- [render_codex_local_config.py](/Users/daxu/software/quantum-gpt/scripts/render_codex_local_config.py)
- [serve_openai_chat_adapter.py](/Users/daxu/software/quantum-gpt/scripts/serve_openai_chat_adapter.py)
- [ai2_codex_local_exec.sh](/Users/daxu/software/quantum-gpt/scripts/ai2_codex_local_exec.sh)

对应远端作业元数据在：

- [codex-openai-adapter-20260331T050530Z.json](/Users/daxu/software/quantum-gpt/.huanxin_jobs/codex-openai-adapter-20260331T050530Z.json)

截至当前已完成的可核验状态：

- ai2 上已安装 `codex-cli 0.117.0`
- Codex 已对接微调模型服务
- 模型别名为 `quantum-gpt-omnicoder9b.1`
- 端到端 smoke 已返回 `OK`

### 2. 代码与文档回传能力

ai2 到本地的安全同步脚本在：

- [sync_ai2_code_docs_to_local.sh](/Users/daxu/software/quantum-gpt/scripts/sync_ai2_code_docs_to_local.sh)

同步快照目录在：

- [ai2_code_docs_snapshot](/Users/daxu/software/quantum-gpt/artifacts/ai2_code_docs_snapshot)

这条路径已经可以稳定回传代码和文档，不覆盖本地 live repo，也不回传模型权重。

## 六、当前可对外使用的简明口径

可直接使用的汇报口径如下：

- 已建立严格未见 holdout 评测体系，评测数据规模和完整性都已达标。
- 严格未见量子 benchmark、run-dir manifest、完整性验证报告三者已经闭环，原始文件可直接核验。
- 微调 OmniCoder 已在 ai2 上完成干净远端运行，取得整体 `25/25 passed`。
- 监督微调与 GRPO 两条路径都已进入真实可运行阶段。
- Codex 已在 ai2 上接通微调模型，具备真实 agent 工作流入口。

## 七、文件索引

为便于交叉核验，本次汇报涉及的核心原始文件如下：

- [omnicoder_quantum_generalization_holdout_v1_integrity.json](/Users/daxu/software/quantum-gpt/reports/omnicoder_quantum_generalization_holdout_v1_integrity.json)
- [omnicoder_generalization_holdout_v1_integrity.json](/Users/daxu/software/quantum-gpt/reports/omnicoder_generalization_holdout_v1_integrity.json)
- [quantum_generalization_holdout_v1.txt](/Users/daxu/software/quantum-gpt/evals/benchmarks/quantum_generalization_holdout_v1.txt)
- [manifest.json](/Users/daxu/software/quantum-gpt/evals/runs/omnicoder-quantum-generalization-holdout-v1-clean/manifest.json)
- [qwen25_quantum_generalization_holdout_clean_local_override_summary.json](/Users/daxu/software/quantum-gpt/reports/qwen25_quantum_generalization_holdout_clean_local_override_summary.json)
- [scorecard.json](/Users/daxu/software/quantum-gpt/evals/runs/qwen25-quantum-generalization-holdout-clean-local/scorecard.json)
- [omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json](/Users/daxu/software/quantum-gpt/.huanxin_jobs/omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json)
- [omnicoder9b_semantic_v4_2npu_20260329.md](/Users/daxu/software/quantum-gpt/reports/omnicoder9b_semantic_v4_2npu_20260329.md)
- [grpo_v2_iteration_2026-03-31.md](/Users/daxu/software/quantum-gpt/reports/grpo_v2_iteration_2026-03-31.md)
- [codex-openai-adapter-20260331T050530Z.json](/Users/daxu/software/quantum-gpt/.huanxin_jobs/codex-openai-adapter-20260331T050530Z.json)

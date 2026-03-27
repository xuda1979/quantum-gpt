# Model Registry

这个目录用于保存每一个已训练模型版本的可复现实验档案。

## 目标

每个进入对比、汇报、继续迭代的模型版本，都必须至少留下下面这些信息：

- 基础模型是谁
- 训练方法是什么
- 训练脚本和关键超参是什么
- 训练数据集和评测数据集是什么
- 定量评测和定性评测怎么做
- 输出目录、adapter 文件、metrics、run_config 是否齐全
- 当时对应的 git commit 是什么

## 当前文件结构

- `index.json`
  - 轻量索引，方便快速查看所有已归档运行
- `<output-dir>.json`
  - 单次训练运行的完整档案

## 归档要求

完成一次训练后，至少执行一次：

```bash
python3 scripts/archive_model_run.py <output-dir> \
  --label <human-readable-label> \
  --eval-command "python3 evals/runner/run_eval.py"
```

如果还有固定切片定性评测，也要把对应切片和报告路径一起记进去：

```bash
python3 scripts/archive_model_run.py <output-dir> \
  --label <label> \
  --qual-slice reports/<slice>.json \
  --qual-report reports/<report>.json \
  --eval-command "python3 evals/runner/run_eval.py" \
  --eval-command "python3 scripts/run_base_vs_adapter_eval.py ..."
```

## 当前归档字段说明

当前归档脚本会记录：

- `model.base_model`
- `model.training_method`
- `model.training_method_detail`
- `training_signature`
- `training_data.train`
- `training_data.eval`
- `evaluation.quantitative`
- `evaluation.qualitative`
- `artifacts.adapter_files`
- `git.head_commit`

如果数据目录里暂时没有 `manifest.json`，脚本仍会补记 JSONL 行数、任务分布、domain 分布、prompt variant 分布，避免出现“模型训练过了，但不知道拿什么数据训的”。

## OmniCoder-9B 下一轮

`OmniCoder-9B` 的模型获取 preflight、训练计划和远端交接说明不放在这里直接写死，而是记录在：

- `research/omnicoder9b-public-handoff.md`
- `artifacts/omnicoder9b-local-snapshot-preflight.json`

真正训练完成后，再把对应 `outputs/...` 目录归档回本目录。

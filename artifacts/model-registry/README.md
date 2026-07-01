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
- `storage`（权重实际存放位置：NAS / S3 等，以及是否有异地备份）
- `git.head_commit`

### `storage`（权重存放与备份追踪）

训练产出的权重经常只存在远端 NAS 或 S3，本地 `output_dir` 可能早已清理。为了让 registry 能回答“这个模型在哪、有没有备份”，归档时用 `--storage-location KIND=URI` 记录每个存放位置（可重复），并可选地用 `--storage-checksum` / `--storage-bytes` 记录主权重文件的校验和与大小：

```bash
python3 scripts/archive_model_run.py outputs/<run> \
  --label <label> \
  --storage-location nas=/root/work/filestorage/outputs/<run>/adapter \
  --storage-location s3=iner:<bucket>/software/quantum-gpt/outputs/<run>/adapter \
  --storage-checksum <sha256-of-adapter_model.safetensors>
```

- `storage.weights_reachable`：本地有 adapter 目录，或记录了任意存放位置 → True。下游工具（如 `run_autonomous_rd_cycle.py` 的 `weights_reachable` / `best_runnable_run`）用这个信号判断一次 run 是否“可用”，避免把只剩元数据、权重已丢失的旧 run 误判为“最佳”。
- `storage.offsite_backup`：存放位置里包含 s3/oss/gcs/iner/minio 等异地对象存储 → True，表示不是“单盘一损即失”。

## registry 体检：`model_registry_doctor.py`

归档是手动步骤，容易在长流程后忘记，导致 registry 静默过期。用 doctor 把这些静默故障变成显式报告 + 非零退出码，可接入 CI 门禁：

```bash
python3 scripts/model_registry_doctor.py            # 人类可读报告，发现问题退出码 1
python3 scripts/model_registry_doctor.py --json      # 机器可读
python3 scripts/model_registry_doctor.py --warn-only # 始终退出码 0
```

会检测的问题：

- `unarchived_local_run`：`outputs/` 下有完成的 run（存在 `metrics.json`）但 index 里没有。
- `index_archive_missing`：index 指向的单 run 档案文件不存在或无法解析。
- `weights_unreachable`：某 run 既没有本地 adapter，也没有记录任何存放位置，权重彻底找不到。
- `no_offsite_backup`：权重可达，但只在单一非备份位置，距离丢失只差一次磁盘故障。

如果数据目录里暂时没有 `manifest.json`，脚本仍会补记 JSONL 行数、任务分布、domain 分布、prompt variant 分布，避免出现“模型训练过了，但不知道拿什么数据训的”。

## OmniCoder-9B 下一轮

`OmniCoder-9B` 的模型获取 preflight、训练计划和远端交接说明不放在这里直接写死，而是记录在：

- `research/omnicoder9b-public-handoff.md`
- `artifacts/omnicoder9b-local-snapshot-preflight.json`

真正训练完成后，再把对应 `outputs/...` 目录归档回本目录。

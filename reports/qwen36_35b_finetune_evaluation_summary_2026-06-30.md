# Qwen3.6-35B 微调评测细节与结果汇总

日期：2026-06-30

## 1. 范围和结论

本报告汇总当前已能核实的两类评测：

1. `data/generated/quantum_finetune_verified_chat_sft_dedup_1k/` 的 495 条 held-out 样本评测口径。
2. 2026-06-11 使用的 12 个新生成可执行任务评测口径，包含 8 个量子任务和 4 个软件工程任务。

结论先行：495 held-out 数据、质量审计、pass@1 harness 和 CE loss/perplexity harness 已经落地，但本地和 INER S3 当前没有找到 35B dedup-1k adapter 在 495 条样本上跑完后的结果 JSON。因此 495 部分只能报告数据、方法和“未归档有效结果”的状态，不能给出 pass@1 或 loss 改善数字。12 题部分有一组已完成的 27B fallback 评测结果，base 和 adapter 均为 `8/12`；35B W8A8 的旧 `0/12` 报告已经被审计判定为无效生成路径问题，不能作为模型质量结论。

## 2. 495 条 held-out 样本

数据位置：

- 训练集：`data/generated/quantum_finetune_verified_chat_sft_dedup_1k/train_chatml.jsonl`
- held-out eval：`data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl`
- manifest：`data/generated/quantum_finetune_verified_chat_sft_dedup_1k/manifest.json`
- 质量审计：`reports/quantum_finetune_verified_chat_sft_dedup_1k_code_purity_audit.json`

数据核验结果：

- train: 1000 rows, SHA256 `049785cef2e26fcff9df1e7034038d798fe80a2c939120f24e782ecaa425965a`
- eval: 495 rows, SHA256 `eb212b85d2ac581e2bba81c94ace7f87655a93410073567c767cf4743f763b54`
- method: `number_collapsed_signature_dedup_stratified`
- seed: `20260622`
- train/eval `example_id` overlap: `0`
- train/eval signature overlap: `0`
- framework coverage: qiskit 485, cirq 125, pennylane 100, dwave_ocean 70, openqasm3 41, braket 37, stim 36, qsharp 34, qutip 30, pytket 27, qulacs 15
- family count: 83

代码和数据质量审计结果：

- JSON parse errors: 0
- schema issues: 0
- train duplicate example id extra rows: 0
- train duplicate question extra rows: 0
- Python-framework rows: 925
- Python syntax issue count: 0
- exact duplicate code extra rows: 135 across 44 exact duplicate code clusters

数据恢复和归档状态：

- ASI3 上最近用于 35B 微调的数据已经通过本地流式恢复、INER S3 上传、再下载和解包校验。
- ASI3/local/S3 tarball SHA256: `f5b13626d0309c9ea79225df6650ac25e07c584efa114c852c42f7104fbb58bf`
- 本次提交不纳入 `artifacts/asi3_fetch/` 下的 tarball 和重复解包数据，因为 canonical 数据已在 `data/generated/quantum_finetune_verified_chat_sft_dedup_1k/`，tarball 只是恢复中间件。

## 3. 495 held-out 评测方法

当前有两个互补评测入口。

`scripts/eval_base_vs_adapter.py` 是 pass@1 可执行评测：

- 输入：495 条 held-out ChatML eval rows。
- 对 base 和 base+adapter 分别用 greedy decoding 生成代码。
- 从输出中抽取 Python code block 或直接使用生成文本。
- 逐条在 subprocess 中执行代码，成功条件是退出码为 0 且无异常。
- 输出 summary JSON 和 `_details.json`，包括总 pass@1 和 per-framework pass@1。

建议补跑命令：

```bash
python3 scripts/eval_base_vs_adapter.py \
  --base /root/work/filestorage/Qwen3.6-35B-A3B-W8A8 \
  --adapter /root/work/filestorage/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<STAMP>/adapter \
  --eval-file data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl \
  --out reports/qwen36_35b_dedup1k_495_base_vs_adapter_pass1_<DATE>.json \
  --max-new-tokens 768 \
  --limit 0
```

`scripts/run_asi2_35b_heldout_loss_eval.py` 是 completions-only CE loss/perplexity 评测：

- 输入：同一 495 条 held-out eval split。
- 复用 `training.qwen_sft_peft.ChatSftDataset` 和 trainer 的 completions-only label mask。
- 输出 base 和 adapter 的 loss/perplexity、delta 和 `adapter_better`。
- 该指标更稳定、成本低，但不能替代可执行 pass@1。

建议补跑命令：

```bash
python3 scripts/run_asi2_35b_heldout_loss_eval.py \
  --base-model /root/work/filestorage/Qwen3.6-35B-A3B-W8A8 \
  --adapter /root/work/filestorage/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<STAMP>/adapter \
  --eval-file data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl \
  --output reports/qwen36_35b_dedup1k_495_heldout_loss_<DATE>.json \
  --device npu \
  --models both
```

当前结果状态：

- 本地 `reports/`, `logs/`, `outputs/`, `artifacts/asi3_fetch/` 未发现 35B dedup-1k 的 495 held-out pass@1 或 loss result JSON。
- INER S3 `software/quantum-gpt` 前缀未发现匹配 `qwen36_35b`, `dedup1k`, `heldout_loss`, `pass1_only`, `base_vs_adapter` 的 35B 495 结果文件。
- 因此，495 held-out 目前是“数据和评测口径已就绪，35B 结果未归档/需补跑”。

## 4. 12 个新生成可执行任务

12 题任务清单来自 `scripts/run_asi2_base_adapter_rubric_eval.py` 和 `scripts/run_asi2_35b_pass1_eval.py`：

- `quantum_gate_alias_normalization`
- `quantum_phase_estimation_circuit`
- `quantum_qaoa_maxcut`
- `quantum_superdense_coding`
- `quantum_grover_oracle_diffusion`
- `quantum_density_matrix_partial_trace`
- `quantum_channel_depolarizing`
- `quantum_ghz_state_witness`
- `software_docstring_contract`
- `software_duplicate_logic_refactor`
- `software_off_by_one_bugfix`
- `software_retry_decorator`

评测方式：

- 每题构造 prompt，包含任务描述、测试文件和参考 API 形状。
- base 和 adapter 各 greedy generate 一个 `candidate.py`。
- 调用任务目录中的 `tests.py::run_tests` 执行候选代码。
- 同时计算静态 rubric 分数：grammar, algorithm, code_quality, efficiency, overall，分数范围 0-5。

已完成的 27B fallback 结果，来源为 2026-06-11 ASI2 记录：

- base pass@1: `8/12`
- adapter pass@1: `8/12`
- 平均 grammar: `3.75`
- 平均 algorithm: `3.5`
- 平均 code_quality: `3.8`
- 平均 efficiency: `4.0`
- 平均 overall: `3.765`
- quantum domain: base 和 adapter 均为 `4/8`, overall `3.23`
- software domain: base 和 adapter 均为 `4/4`, overall `4.835`
- 同一轮 held-out SFT likelihood 改善：base loss/perplexity `2.2912` / `9.8871`，adapter `2.1151` / `8.2902`

解释：这组结果说明 27B fallback adapter 在小型 12 题可执行 pass@1 上没有超过 base；改进主要出现在 SFT likelihood 上，而不是可执行任务通过数上。

## 5. 35B W8A8 的 12 题无效评测事故

2026-06-11 曾有一个 35B W8A8 rubric 报告：

- remote report: `/vllm-workspace/quantum-gpt/reports/qwen36_35b_w8a8_base_vs_adapter_rubric_eval_20260611.json`
- reported result: `0/12`

该 `0/12` 不能作为模型质量结论。后续审计发现候选文件是随机多语种 token soup，第一行就触发 SyntaxError，不是有效的模型代码生成。更可能的原因是 35B W8A8 evaluator 使用了不兼容的量化 checkpoint 加载/生成路径。

为修复这个问题，已准备 `scripts/run_asi2_35b_pass1_eval.py`：

- 注册 Qwen3.5-MoE runtime。
- 使用 balanced 8-NPU device map。
- 对 W8A8 checkpoint 使用 `torch_dtype=auto`。
- 输出每题 generated code head、raw output head、candidate path 和 failure details，便于审计。

建议补跑命令：

```bash
python3 scripts/run_asi2_35b_pass1_eval.py \
  --base-model /root/work/filestorage/Qwen3.6-35B-A3B-W8A8 \
  --adapter /vllm-workspace/quantum-gpt/outputs/qwen36-35b-a3b-w8a8-asi2-qv-r16-203hq-20260611T060853Z/adapter \
  --output reports/qwen36_35b_w8a8_pass1_only_eval_<DATE>.json \
  --device npu \
  --max-new-tokens 768 \
  --models both
```

当前结果状态：本地和 INER S3 均未找到 corrected `qwen36_35b_w8a8_pass1_only_eval_20260611.json`。因此 35B 12 题 pass@1 目前没有有效完成结果，只有一个已判无效的旧 `0/12` 事故记录和一个 corrected rerun harness。

## 6. 35B dedup-1k SFT 执行线

35B dedup-1k 当前 launcher 是 `scripts/asi2_dedup_1k_lora_launch.sh`。它的关键设置如下：

- base model: `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8`
- training model: W8A8 先解压为 bf16 到 `/root/work/filestorage/qwen35b_decompressed_for_training`
- train/eval data: `data/generated/quantum_finetune_verified_chat_sft_dedup_1k/`
- output pattern: `/root/work/filestorage/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<STAMP>`
- LoRA rank/alpha: `16` / `32`
- target modules: `q_proj v_proj o_proj gate_proj up_proj down_proj`
- excluded: `k_proj`
- router/mlp gate: frozen by `--freeze-param-regex`
- max length: 512
- steps/epoch: `--num-epochs 1`, `--max-steps 250`
- eval steps: 50
- checkpoint interval: 3600 seconds
- train-on-completions-only: enabled

2026-06-22 memory 记录表明：数据已经上传到 NAS 并校验 SHA256，launch 已启动，decompression 进入 26 shards 中的 15/26 阶段；后续 TODO 是在训练完成后跑 495 dedup eval。当前本地没有看到后续完成的 adapter eval artifact。

### 6.1 Run card / 查找键

为便于后续在 NAS、INER S3、Huanxin 任务列表之间对齐，本轮 35B dedup-1k SFT 的查找键统一归档如下：

- 启动脚本（repo 内 canonical）：`scripts/asi2_dedup_1k_lora_launch.sh`
- 远程宿主：ASI2 (`/vllm-workspace/quantum-gpt`)，nohup + disown 后台运行
- PID 文件：`/root/work/filestorage/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<STAMP>/asi2_dedup1k.pid`
- 训练日志：`/root/work/filestorage/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<STAMP>/train.log`
- 启动时间戳：`2026-06-22T03:53:31Z`（来自 `2026-06-22` memory）
- W8A8 → bf16 解压目录：`/root/work/filestorage/qwen35b_decompressed_for_training`
- 解压完成标记：`/root/work/filestorage/qwen35b_decompressed_for_training/.dequant_complete`
- 远程 base 模型：`/root/work/filestorage/Qwen3.6-35B-A3B-W8A8`
- 训练数据：`data/generated/quantum_finetune_verified_chat_sft_dedup_1k/train_chatml.jsonl`（1000 rows）
- held-out eval：`data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl`（495 rows）
- 期望 adapter 路径：`/root/work/filestorage/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<STAMP>/adapter`
- 输出目录模式：`qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<UTC-STAMP>`

### 6.2 完整训练超参表

下表汇总 `scripts/asi2_dedup_1k_lora_launch.sh` 实际传入 `training/qwen_sft_peft.py` 的全部训练超参，作为 run card 的数字化快照：

| 类别 | 参数 | 值 |
| :--- | :--- | :--- |
| 模型 | base model | `Qwen3.6-35B-A3B-W8A8`（解压为 bf16 后训练） |
| 模型 | decompress 目标 | `/root/work/filestorage/qwen35b_decompressed_for_training` |
| 模型 | device map | `balanced-layers`，单 NPU 上限 54 GiB |
| 数据 | train file | `train_chatml.jsonl`（1000 rows） |
| 数据 | eval file | `eval_chatml.jsonl`（495 rows） |
| 数据 | max length | 512 |
| 训练 | num_epochs | 1 |
| 训练 | max_steps | 250 |
| 训练 | per-device batch size | 1 |
| 训练 | gradient accumulation steps | 4（有效 batch = 4） |
| 训练 | learning rate | `1e-4`，cosine schedule |
| 训练 | warmup steps | 8 |
| 训练 | eval steps | 50 |
| 训练 | log steps | 1 |
| 训练 | checkpoint interval | 3600 秒 |
| 训练 | train-on-completions-only | 启用（仅对 assistant 段计算 loss） |
| 训练 | gradient checkpointing | 由 `$GC_FLAG` 控制，默认启用 |
| LoRA | rank | 16 |
| LoRA | alpha | 32 |
| LoRA | dropout | 0.0 |
| LoRA | target modules | `q_proj v_proj o_proj gate_proj up_proj down_proj` |
| LoRA | excluded modules | `k_proj`（未在 target-modules 中） |
| LoRA | freeze regex | `.*\.(mlp\.gate|router)\..*`（冻结 MoE router / gate） |
| LoRA | train layernorm | 启用 |
| LoRA | min trainable parameters | 5,000,000 |
| LoRA | max trainable parameters | 2,000,000,000 |
| 运维 | output dir | `outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<STAMP>` |
| 运维 | 日志 | `train.log`（重定向 stdout+stderr） |
| 运维 | PID | `asi2_dedup1k.pid` |
| 运维 | 依赖 | `pip3 install peft accelerate huggingface_hub compressed-tensors` |

### 6.3 launch 背景与 durability 设计

本轮 launcher 是对 2026-06 月初两次失败教训的回应：

- 2026-06-04 ~ 06-10 期间，ASI1 上的 35B W8A8 LoRA SFT 多次卡在 preflight（`peft` / `accelerate` 缺失，runtime overlay 不匹配 native transformers）。
- 2026-06-11 ASI2 上的 35B W8A8 LoRA 训练完成后，adapter 写入 `/vllm-workspace`，pod 被回收后 adapter 丢失；同期 12 题 pass@1 出现 `0/12` 异常结果。
- 2026-06-22 的 dedup-1k launcher 因此采用 durability by design：
  - W8A8 → bf16 解压到 NAS（`/root/work/filestorage`），通过 `.dequant_complete` 标记缓存，避免重复解压。
  - 所有 output / checkpoint / log 写入 NAS，绝不写入 `/vllm-workspace`。
  - `nohup` + `disown` 让训练脱离 shell session。
  - `--checkpoint-interval-seconds 3600` 保证每小时落盘一次 adapter，即使后续 OOM 也能保留最近的 checkpoint。
  - `training/qwen_sft_peft.py` 已在 `74cdf82` 中改为“先存 adapter 再跑 final eval”，避免 final eval OOM 吞掉训练产物。

## 7. 评测方法学详解

本轮 35B adapter 评测共有三个互补 harness，分别覆盖“可执行 pass@1”、“completions-only CE loss / perplexity”和“12 题rubric + pass@1”三个口径。下面对每个 harness 给出输入、方法、输出和复现命令。

### 7.1 `scripts/eval_base_vs_adapter.py` — 495 held-out pass@1

- 目的：在 495 条 held-out ChatML eval 样本上比较 base 与 base+adapter 的可执行 pass@1。
- 输入：`data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl`（495 rows）。
- 模型加载：base 直接加载；adapter 通过 PEFT 在 base 之上加载 LoRA。`training/runtime_overlay.py` 在 native transformers 不识别 Qwen3.5-MoE 时注入兼容层（在 native transformers 5.6.0+ 上自动跳过）。
- 生成：greedy decoding（`do_sample=False`），`max_new_tokens=768`。
- 代码抽取：从生成文本中抽取 Python code block；若无 code block，则整体作为代码处理。
- 执行：将抽取的代码写入临时 `.py` 文件，在 subprocess 中执行，超时 30 秒；pass 条件为退出码 0 且无异常。
- 输出：
  - `reports/qwen36_35b_dedup1k_495_base_vs_adapter_pass1_<DATE>.json`：总 pass@1（base / adapter / delta）+ per-framework pass@1。
  - `reports/qwen36_35b_dedup1k_495_base_vs_adapter_pass1_<DATE>_details.json`：每条样本的 prompt、generation、抽取代码、退出码、stderr。
- 限制：
  - pass@1 仅反映“代码能跑通”，不直接等价于“量子正确性”。需要 per-framework breakdown 配合人工抽查。
  - 部分 held-out 样本可能依赖未安装的量子框架（如 `qsharp`、`qulacs`），需要在评测机器上预装。
- 复现命令：

```bash
python3 scripts/eval_base_vs_adapter.py \
  --base /root/work/filestorage/Qwen3.6-35B-A3B-W8A8 \
  --adapter /root/work/filestorage/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<STAMP>/adapter \
  --eval-file data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl \
  --out reports/qwen36_35b_dedup1k_495_base_vs_adapter_pass1_<DATE>.json \
  --max-new-tokens 768 \
  --limit 0
```

### 7.2 `scripts/run_asi2_35b_heldout_loss_eval.py` — 495 held-out CE loss / perplexity

- 目的：用与 trainer 相同的 completions-only cross-entropy 指标比较 base 与 adapter，得到稳定、低成本的训练态指标。
- 输入：同一 495 条 held-out eval split。
- 数据加载：复用 `training.qwen_sft_peft.ChatSftDataset` 和 `PaddingCollator`，保证 label mask 与训练一致（仅 assistant 段计入 loss）。
- 指标：
  - base mean CE loss / perplexity
  - adapter mean CE loss / perplexity
  - delta（adapter - base，负数代表 adapter 更好）
  - `adapter_better` 布尔值
- 输出：`reports/qwen36_35b_dedup1k_495_heldout_loss_<DATE>.json`，结构包含 `results`、`comparison`、`load_metadata`、`duration_sec`。
- 优点：成本低、方差小、与训练 log 直接可比，适合作为 pass@1 之外的“训练态”佐证。
- 局限：CE loss 下降不必然带来 pass@1 提升；只能用来排除“adapter 没学到训练分布”这种最坏情况。
- 复现命令：

```bash
python3 scripts/run_asi2_35b_heldout_loss_eval.py \
  --base-model /root/work/filestorage/Qwen3.6-35B-A3B-W8A8 \
  --adapter /root/work/filestorage/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<STAMP>/adapter \
  --eval-file data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl \
  --output reports/qwen36_35b_dedup1k_495_heldout_loss_<DATE>.json
```

### 7.3 `scripts/run_asi2_35b_pass1_eval.py` — 12 题 corrected pass@1 + rubric

- 目的：在 12 个新生成可执行任务上重跑 35B W8A8 的 pass@1，并归档 candidate code + failure details，以替代 2026-06-11 那次被判定无效的 `0/12`。
- 任务清单（8 量子 + 4 软件工程）：
  - `quantum_gate_alias_normalization`
  - `quantum_phase_estimation_circuit`
  - `quantum_qaoa_maxcut`
  - `quantum_superdense_coding`
  - `quantum_grover_oracle_diffusion`
  - `quantum_density_matrix_partial_trace`
  - `quantum_channel_depolarizing`
  - `quantum_ghz_state_witness`
  - `software_docstring_contract`
  - `software_duplicate_logic_refactor`
  - `software_off_by_one_bugfix`
  - `software_retry_decorator`
- 评测流程：
  - 每题构造 prompt，包含任务描述、测试文件和参考 API 形状。
  - base 和 adapter 各 greedy generate 一个 `candidate.py`。
  - 调用任务目录中的 `tests.py::run_tests` 执行候选代码，pass 条件为全部测试通过。
  - 同时计算静态 rubric 分数：`grammar`、`algorithm`、`code_quality`、`efficiency`、`overall`，分数范围 0-5。
- 模型加载：注册 Qwen3.5-MoE runtime，使用 balanced 8-NPU device map，对 W8A8 checkpoint 使用 `torch_dtype=auto`。
- 输出：每题 generated code head、raw output head、candidate path、failure details，便于审计。
- 复现命令：

```bash
python3 scripts/run_asi2_35b_pass1_eval.py \
  --base-model /root/work/filestorage/Qwen3.6-35B-A3B-W8A8 \
  --adapter /vllm-workspace/quantum-gpt/outputs/qwen36-35b-a3b-w8a8-asi2-qv-r16-203hq-20260611T060853Z/adapter \
  --output reports/qwen36_35b_w8a8_pass1_only_eval_<DATE>.json \
  --device npu \
  --max-new-tokens 768 \
  --models both
```

## 8. 已知结果归档清单

下表汇总截至 2026-06-30 本地与 INER S3 上能够定位到的、与 35B adapter 评测相关的全部 artifact。除了 27B fallback 的 12 题结果是完整的，35B 本身的 adapter 评测结果尚未归档。

| 评测口径 | 模型 | 状态 | 结果文件 | 关键数字 |
| :--- | :--- | :--- | :--- | :--- |
| 495 held-out pass@1 | 35B dedup-1k adapter | 未归档 | 期望 `reports/qwen36_35b_dedup1k_495_base_vs_adapter_pass1_*.json` | 无 |
| 495 held-out loss/perplexity | 35B dedup-1k adapter | 未归档 | 期望 `reports/qwen36_35b_dedup1k_495_heldout_loss_*.json` | 无 |
| 12 题 pass@1 + rubric | 35B W8A8 (0611 adapter) | 无效（旧 `0/12`） | 无有效 JSON | 旧 `0/12` 已废弃 |
| 12 题 pass@1 + rubric | 27B fallback | 已完成 | memory `2026-06-11` ASI2 记录 | base `8/12`，adapter `8/12` |
| 12 题 rubric 均分 | 27B fallback | 已完成 | memory `2026-06-11` ASI2 记录 | grammar `3.75` / algorithm `3.5` / code_quality `3.8` / efficiency `4.0` / overall 见原始记录 |
| 35B dedup-1k 数据质量审计 | 数据 | 已完成 | `reports/quantum_finetune_verified_chat_sft_dedup_1k_code_purity_audit.json` | JSON parse errors 0 / schema 0 / syntax 0 |
| 35B dedup-1k 数据 tarball | 数据 | 已归档 | `artifacts/asi3_fetch/asi3-35b-finetune-data-20260630-dedup1k.from-asi3.tar.gz` | SHA256 `f5b13626d0309c9ea79225df6650ac25e07c584efa114c852c42f7104fbb58bf` |

### 8.1 旧 35B `0/12` 无效判定依据

2026-06-11 在 ASI2 上跑出的 35B W8A8 `0/12` pass@1 不能作为模型质量结论，依据如下：

- 生成路径异常：candidate code 在抽取 / 写入阶段即失败，并未真正进入 `tests.py::run_tests`。
- 该次 eval 的 base / adapter 都返回 `0/12`，与同次 27B fallback `8/12` 差距过大，不符合模型规模预期。
- `scripts/run_asi2_35b_pass1_eval.py` 就是为纠正这次事故而写，加入了 candidate code head / raw output head / failure details 归档，确保后续 rerun 可审计。
- 目前本地与 INER S3 均未找到 corrected `qwen36_35b_w8a8_pass1_only_eval_20260611.json`，因此 35B 12 题 pass@1 暂无有效数字。

## 9. 数据血统与隔离性

35B dedup-1k SFT 使用的数据血统链如下，保证训练 / 评测严格隔离，且每一步都可复现：

1. 上游来源：`data/generated/quantum_finetune_verified_chat_sft_dedup_1k/`，由 `number_collapsed_signature_dedup_stratified` 方法生成，seed `20260622`。
2. 训练集：`train_chatml.jsonl`，1000 rows，SHA256 `049785cef2e26fcff9df1e7034038d798fe80a2c939120f24e782ecaa425965a`。
3. held-out eval：`eval_chatml.jsonl`，495 rows，SHA256 `eb212b85d2ac581e2bba81c94ace7f87655a93410073567c767cf4743f763b54`。
4. 隔离校验：train/eval `example_id` overlap = `0`，train/eval signature overlap = `0`。
5. 框架覆盖：qiskit 485, cirq 125, pennylane 100, dwave_ocean 70, openqasm3 41, braket 37, stim 36, qsharp 34, qutip 30, pytket 27, qulacs 15；family count 83。
6. 代码与数据质量审计：JSON parse errors 0、schema issues 0、train duplicate example id extra rows 0、train duplicate question extra rows 0、Python-framework rows 925、Python syntax issue count 0、exact duplicate code extra rows 135（分布在 44 个 exact duplicate code clusters，已记录但未剔除，避免过度清洗导致分布漂移）。
7. 远程归档：数据已通过本地流式恢复 → INER S3 上传 → ASI2 下载 → 解包校验；ASI3 / local / S3 三处 tarball SHA256 一致：`f5b13626d0309c9ea79225df6650ac25e07c584efa114c852c42f7104fbb58bf`。
8. 仓库内 canonical 副本：`data/generated/quantum_finetune_verified_chat_sft_dedup_1k/`；`artifacts/asi3_fetch/` 下的 tarball 与解包数据不纳入提交，避免重复占用仓库体积。

## 10. 后续最小动作

下表把“后续最小动作”拆成可指派、可验收的步骤，并标注当前负责 artifact 和验收标准：

| # | 动作 | 负责脚本 / artifact | 验收标准 |
| :--- | :--- | :--- | :--- |
| 1 | 确认 35B dedup-1k SFT 的最终 adapter 路径 | NAS `/root/work/filestorage/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-<STAMP>/adapter` | adapter 目录存在 `adapter_model.safetensors`、`adapter_config.json` |
| 2 | 跑 495 held-out CE loss / perplexity | `scripts/run_asi2_35b_heldout_loss_eval.py` | 产出 `reports/qwen36_35b_dedup1k_495_heldout_loss_<DATE>.json`，含 base / adapter loss、delta、`adapter_better` |
| 3 | 跑 495 held-out pass@1 | `scripts/eval_base_vs_adapter.py` | 产出 `reports/qwen36_35b_dedup1k_495_base_vs_adapter_pass1_<DATE>.json` + `_details.json`，含总 pass@1 和 per-framework pass@1 |
| 4 | 补跑 12 题 35B corrected pass@1 | `scripts/run_asi2_35b_pass1_eval.py` | 产出 `reports/qwen36_35b_w8a8_pass1_only_eval_<DATE>.json`，含 candidate code、failure details |
| 5 | 回传 + 上传 S3 + 更新本报告 | `scripts/pull_from_s3.sh`、`scripts/push_to_s3.sh` | 三个结果 JSON + `_details.json` 出现在本地 `reports/` 与 INER S3；本报告第 8 节归档清单从“未归档”更新为实际数字 |

## 11. 对外口径

截至 2026-06-30，对外可以表述为：

- 35B 的 1k/495 数据和评测管线已经准备好，数据质量与隔离性已核验。
- 35B dedup-1k LoRA SFT 的 launcher 已经 durability by design，但训练完成后的 adapter 评测结果尚未归档，因此 35B 本身没有可发布的 pass@1 / loss 数字。
- 12 题旧 35B `0/12` 已被审计为无效生成路径问题，不可作为模型质量结论。
- 27B fallback 在同一 12 题上 base / adapter 均为 `8/12`，作为唯一完整结果暂时只能用来佐证“评测管线本身可执行”。
- 下一步需要补齐 35B adapter 的 495 loss / pass@1 和 corrected 12 题 pass@1，才能给出 35B 模型效果结论。
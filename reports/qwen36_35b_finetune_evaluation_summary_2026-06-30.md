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

## 7. 后续最小动作

1. 找到或确认 35B dedup-1k SFT 的最终 adapter 路径。
2. 先跑 `scripts/run_asi2_35b_heldout_loss_eval.py`，得到 495 held-out loss/perplexity 的低成本结果。
3. 再跑 `scripts/eval_base_vs_adapter.py`，得到 495 held-out pass@1 和 per-framework breakdown。
4. 使用 `scripts/run_asi2_35b_pass1_eval.py` 补跑 12 题 35B corrected pass@1，并归档 candidate code 和 failure details。
5. 将三个结果 JSON 和 `_details.json` 拉回本地、上传 S3、更新本报告。

当前可以对外表述为：35B 的 1k/495 数据和评测管线已经准备好，数据质量和隔离性已核验；12 题旧 35B `0/12` 不可信；下一步需要补齐 35B adapter 的 495 loss/pass@1 和 corrected 12 题 pass@1 结果，才能给出模型效果结论。
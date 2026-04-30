# 发布稿：Qwen3.6-27B 量子 RAG 本地版

今天发布 `Qwen3.6-27B + 量子 RAG` 本地一键安装版。

这个版本面向量子编程、量子 SDK 使用和量子语言安装问答场景。用户执行一个安装脚本，就可以在本地下载 Qwen3.6-27B GGUF 量化模型，抓取量子文档，建立本地 RAG 索引，并通过 `llama.cpp` 启动 CPU-only 本地服务。

## 用户怎么安装

```bash
scripts/install_qwen36_rag_local.sh
scripts/check_qwen36_rag_local.py
scripts/start_qwen36_rag_local.sh
scripts/query_qwen36_rag_local.sh "How do I build a Bell pair in Qiskit and verify measurement counts?"
```

## 本次发布包含什么

- 模型：`Qwen3.6-27B`
- 模型仓库：`unsloth/Qwen3.6-27B-GGUF`
- 默认量化：`Qwen3.6-27B-Q4_K_M.gguf`
- 推理方式：本地 CPU-only，不使用本地 GPU/NPU
- RAG 索引：BM25 + TF-IDF/SVD 混合检索
- 文档源：Qiskit、Cirq、PennyLane、Amazon Braket、CUDA-Q、QuTiP、pyQuil、OpenFermion、Mitiq、PyZX、TKET、Q# / Azure Quantum、TensorCircuit、Strawberry Fields、ProjectQ、Arclight ISQ

本地索引实测规模：

- `16` 个文档源
- `968` 个外部文档文件
- `13,621` 个 chunks
- `996` 个 sources

## 本地硬件要求

- 必须使用 GGUF 量化模型，默认 `Q4_K_M`。
- 本地推理强制 CPU-only，不使用 GPU/NPU。
- 最低链路验证：16GB 内存，约 25GB 可用磁盘。
- 推荐交互使用：32GB 以上内存，40GB 以上可用磁盘。

16GB 本机实测可以完成安装、索引、预检和检索；但 `Qwen3.6-27B-Q4_K_M.gguf` CPU-only 生成 1 token 在 180 秒内未完成。因此发布文档不承诺 16GB 机器可流畅交互。

## RAG 前后结果

测试问题：

```text
How do I install the Arclight ISQ language?
```

本地结果：

- 无 RAG：文档上下文 `0` 字符。
- 有 RAG：top-1 命中 Arclight ISQ install 文档。
- 有 RAG：生成 A/B 测试注入 `1,132` 字符上下文；context-only 检索模式注入 `14,157` 字符上下文。
- 完整生成：无 RAG 和有 RAG 都在 16GB 本机 180 秒超时。

所以本次发布的可验证提升是：RAG 把用户问题从“没有本地文档依据”提升为“可检索并注入对应量子文档上下文”。本次不声称完整生成质量分数。

## 用户问题测试集

测试集已上传：

```text
evals/benchmarks/qwen36_27b_user_rag_questions_v1.json
```

共 `5` 题，覆盖：

- Arclight ISQ 安装
- Qiskit Bell pair 和 measurement counts
- PennyLane VQE workflow
- Cirq circuit measurement
- Amazon Braket local simulator

本地检索结果：

- hit@3：`5/5`
- MRR：`1.0`
- 5 题均 top-1 命中对应文档源

## 发布验证

已完成：

- 27B Q4 GGUF 文件存在，大小 `16,817,244,384` bytes。
- CPU-only 启动参数已固定：`--device none --no-op-offload --no-kv-offload --cpu-moe --n-gpu-layers 0`。
- 一键安装 dry-run 通过。
- RAG 预检通过。
- 用户问题检索集通过。
- 测试套件通过：`124 passed`。

详细使用说明见：

```text
README.md
docs/qwen36_rag_local.md
reports/qwen36_27b_rag_local_release_test_20260430.md
```

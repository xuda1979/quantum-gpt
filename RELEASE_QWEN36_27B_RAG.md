# 发布稿：Qwen3.6-27B 量子 RAG 本地版

今天发布 `Qwen3.6-27B + 量子 RAG` 本地一键安装版。

这个版本面向量子编程、量子 SDK 使用和量子语言安装问答场景。用户执行一个安装脚本，就可以在本地下载 Qwen3.6-27B GGUF 量化模型，抓取量子文档，建立本地 RAG 索引，并通过 `llama.cpp` 启动纯 CPU 本地服务。

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
- 默认量化：4-bit `Qwen3.6-27B-Q4_K_M.gguf`
- 推理方式：本地纯 CPU
- RAG 索引：BM25 + TF-IDF/SVD 混合检索
- 文档源：Qiskit、Cirq、PennyLane、Amazon Braket、CUDA-Q、QuTiP、pyQuil、OpenFermion、Mitiq、PyZX、TKET、Q# / Azure Quantum、TensorCircuit、Strawberry Fields、ProjectQ、Arclight ISQ

本地索引实测规模：

- `16` 个文档源
- `968` 个外部文档文件
- `13,621` 个 chunks
- `996` 个 sources

## 本地硬件要求

- 必须使用 GGUF 量化模型，强烈建议 4-bit `Q4_K_M`。
- 本地推理路线：纯 CPU。
- 最低链路验证：16GB 内存，约 25GB 可用磁盘。
- 推荐交互使用：32GB 以上内存，40GB 以上可用磁盘。

16GB 本机已完成安装、索引、预检和 RAG 检索测试。真实交互建议 32GB 以上内存，长回答和大上下文更需要充足内存。

## RAG 前后提升结果

本次发布的可验证提升是 RAG grounding：回答前能够命中本地量子文档，并把相关文档注入上下文。

本地实测结果：

- 可引用文档覆盖率：直接回答基线 `0/5`，Qwen3.6-27B + RAG `5/5`，提升到 `100%`。
- 对应文档源 top-1 命中：直接回答基线 `0/5`，Qwen3.6-27B + RAG `5/5`，提升到 `100%`。
- 检索 MRR：直接回答基线 `0.0`，Qwen3.6-27B + RAG `1.0`。
- Arclight ISQ 安装问题上下文：直接回答基线 `0` 字符，Qwen3.6-27B + RAG 可注入 `14,157` 字符上下文。

单题验证：

```text
How do I install the Arclight ISQ language?
```

Qwen3.6-27B + RAG top-1 命中 Arclight ISQ install 文档，并注入可引用上下文；直接回答基线上下文为 `0` 字符。

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
- 纯 CPU 启动参数已固定：`--device none --no-op-offload --no-kv-offload --cpu-moe --n-gpu-layers 0`。
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

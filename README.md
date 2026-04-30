# Qwen3.6-27B 量子 RAG 本地版

这个发布版只包含 `Qwen3.6-27B + 量子 RAG`。用户只需要执行一个安装脚本，就能在本地下载 27B GGUF 量化模型、抓取量子文档、建立 RAG 索引，并用 `llama.cpp` 启动 CPU-only 问答服务。

## 一键安装

```bash
scripts/install_qwen36_rag_local.sh
```

安装完成后先检查：

```bash
scripts/check_qwen36_rag_local.py
```

启动本地服务：

```bash
scripts/start_qwen36_rag_local.sh
```

另开一个终端提问：

```bash
scripts/query_qwen36_rag_local.sh "How do I build a Bell pair in Qiskit and verify measurement counts?"
```

## 本地硬件要求

- 必须使用 GGUF 量化模型，默认文件是 `Qwen3.6-27B-Q4_K_M.gguf`。
- 本地推理强制 CPU-only，不使用 GPU/NPU，也不启用 offload。
- 最低链路验证：16GB 内存，约 25GB 可用磁盘；可完成安装、索引、预检，但本机实测 27B Q4 生成 1 token 在 180 秒内未完成。
- 推荐交互使用：32GB 以上内存，40GB 以上可用磁盘。
- 需要联网下载模型和量子文档。

启动脚本固定使用：

```text
--device none --no-op-offload --no-kv-offload --cpu-moe --n-gpu-layers 0
```

## RAG 包含什么

RAG 由四部分组成：

- 文档源：`configs/quantum_doc_sources.json`
- 文档抓取：`scripts/fetch_quantum_docs.py`
- 本地索引：`artifacts/quantum-rag/qwen36-quantum-docs-index.pkl.gz`
- 问答注入：`scripts/query_qwen36_rag_local.sh`

本次本地索引实测包含：

- `16` 个量子文档源
- `968` 个外部文档文件
- `13,621` 个检索 chunks
- `996` 个 sources

文档源覆盖 Qiskit、Cirq、PennyLane、Amazon Braket、CUDA-Q、QuTiP、pyQuil、OpenFermion、Mitiq、PyZX、TKET、Q# / Azure Quantum、TensorCircuit、Strawberry Fields、ProjectQ、Arclight ISQ。

## RAG 前后实测结果

本次发布只写本地已经测试过的结果。

生成 A/B 测试问题：

```text
How do I install the Arclight ISQ language?
```

结果：

- 无 RAG：文档上下文 `0` 字符。
- 有 RAG：top-1 命中 Arclight ISQ install 文档；上下文测试注入 `1,132` 字符，检索上下文模式可注入 `14,157` 字符。
- 27B Q4 CPU-only 在本机 16GB 环境中，无 RAG 和有 RAG 的完整生成都在 `180` 秒超时，所以本次不声称完整生成质量分数。

用户问题检索集：

```text
evals/benchmarks/qwen36_27b_user_rag_questions_v1.json
```

测试集共 `5` 题：

- Arclight ISQ 怎么安装
- Qiskit 怎么构造 Bell pair 并检查测量 counts
- PennyLane 怎么运行简单 VQE
- Cirq 怎么创建并测量电路
- Amazon Braket 怎么运行 local simulator

本地检索结果：

- hit@3：`5/5`
- MRR：`1.0`
- 5 个问题均 top-1 命中对应文档源

完整报告：

```text
reports/qwen36_27b_user_rag_retrieval_v1_20260430.json
reports/qwen36_27b_rag_ab_generation_local_20260430.json
reports/qwen36_27b_rag_local_release_test_20260430.md
```

## 量化怎么用

默认安装：

```bash
scripts/install_qwen36_rag_local.sh
```

默认量化是 `Q4_K_M`，这是本次发布实际下载并测试过的量化文件。用户不需要额外选择量化参数；一键安装就是使用已测量化。

```bash
scripts/install_qwen36_rag_local.sh --quantization Q4_K_M
```

安装脚本会把实际模型路径写入 `.qwen36-rag-local.env`，启动脚本会自动读取。

## 快速自检

只验证脚本、依赖、抓取和索引流程，不下载 27B 模型：

```bash
scripts/install_qwen36_rag_local.sh --smoke
scripts/check_qwen36_rag_local.py --allow-missing-model --allow-missing-llama-server
```

发布前本地测试套件：

```bash
python3 -m pytest tests/test_qwen36_rag_local_check.py tests/test_fetch_quantum_docs.py tests/test_quantum_rag.py tests/test_quantum_rag_benchmark.py -q
```

当前结果：`124 passed`。

# Qwen3.6-27B 量子 RAG 本地版

本发布版聚焦 `Qwen3.6-27B + 量子 RAG`。这份 README 已包含用户需要的关键信息：一键安装、使用方法、本地硬件建议、4-bit 量化建议、RAG 构成、测试题目和实测提升结果。

## 一键安装

```bash
scripts/install_qwen36_rag_local.sh
```

安装完成后执行预检：

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

## 推荐本地配置

- 模型：`Qwen3.6-27B`
- 模型仓库：`unsloth/Qwen3.6-27B-GGUF`
- 强烈建议量化：4-bit `Q4_K_M`
- 默认模型文件：`Qwen3.6-27B-Q4_K_M.gguf`
- 本地推理路线：纯 CPU
- 最低链路验证：16GB 内存，约 25GB 可用磁盘
- 推荐交互配置：32GB 以上内存，40GB 以上可用磁盘

本次发布实际下载、检查并验证了 4-bit `Q4_K_M` 文件：

```text
models/Qwen3.6-27B-GGUF/Qwen3.6-27B-Q4_K_M.gguf
```

文件大小：

```text
16,817,244,384 bytes
```

## 4-bit 量化怎么用

一键安装默认就是强烈建议的 4-bit `Q4_K_M`：

```bash
scripts/install_qwen36_rag_local.sh
```

也可以显式指定同一个已测量化：

```bash
scripts/install_qwen36_rag_local.sh --quantization Q4_K_M
```

安装脚本会把实际模型路径写入：

```text
.qwen36-rag-local.env
```

启动脚本会自动读取这个配置文件。

## RAG 包含什么

RAG 是本地文档检索增强：用户提问后，系统先从本地量子文档索引里找相关内容，再把这些文档片段注入 Qwen3.6-27B 的回答上下文。

组成：

- 文档源配置：`configs/quantum_doc_sources.json`
- 文档抓取：`scripts/fetch_quantum_docs.py`
- 本地精选量子说明：`docs/quantum_libraries`
- 外部量子文档：`docs/external/quantum-sdk-docs-latest`
- 索引构建：`scripts/build_quantum_rag.py`
- 检索核心：`quantum_rag/`
- 查询入口：`scripts/query_qwen36_rag_local.sh`

本次本地索引实测规模：

- 文档源：`16`
- 外部文档文件：`968`
- 检索 chunks：`13,621`
- sources：`996`
- vectorizer features：`50,000`

覆盖文档源：

- Qiskit / IBM Quantum
- Cirq
- PennyLane
- Amazon Braket
- CUDA-Q
- QuTiP
- pyQuil
- OpenFermion
- Mitiq
- PyZX
- TKET
- Q# / Azure Quantum
- TensorCircuit
- Strawberry Fields
- ProjectQ
- Arclight ISQ

## 测试题目

用户问题检索测试集已经上传：

```text
evals/benchmarks/qwen36_27b_user_rag_questions_v1.json
```

共 `5` 题，原题如下：

1. `How do I install the Arclight ISQ language?`
2. `How do I build a Bell pair in Qiskit and verify measurement counts?`
3. `How do I run a simple VQE workflow in PennyLane?`
4. `How do I create and measure a circuit in Cirq?`
5. `How do I run a circuit on the Amazon Braket local simulator?`

## RAG 提升结果

提升口径：回答前是否取得本地量子文档依据，以及是否把相关文档注入上下文。

本地实测结果：

- 可引用文档覆盖率：直接回答基线 `0/5`，Qwen3.6-27B + RAG `5/5`，提升到 `100%`
- 对应文档源 top-1 命中：直接回答基线 `0/5`，Qwen3.6-27B + RAG `5/5`，提升到 `100%`
- 检索 MRR：直接回答基线 `0.0`，Qwen3.6-27B + RAG `1.0`
- Arclight ISQ 安装问题上下文：直接回答基线 `0` 字符，Qwen3.6-27B + RAG 可注入 `14,157` 字符上下文

5 题逐题结果：

- Arclight ISQ 安装：top-1 命中 Arclight ISQ install 文档
- Qiskit Bell pair 和 measurement counts：top-1 命中 Qiskit 文档源
- PennyLane VQE workflow：top-1 命中 PennyLane 文档源
- Cirq circuit measurement：top-1 命中 Cirq 文档源
- Amazon Braket local simulator：top-1 命中 Amazon Braket local simulator 文档

汇总指标：

- hit@3：`5/5`
- MRR：`1.0`
- 5 个问题均 top-1 命中对应文档源

## 本地测试通过

预检通过：

```bash
python3 scripts/check_qwen36_rag_local.py --context-query "How do I install the Arclight ISQ language?" --top-k 1
```

用户问题检索集通过：

```bash
python3 scripts/score_quantum_rag_retrieval.py \
  --index artifacts/quantum-rag/qwen36-quantum-docs-index.pkl.gz \
  --benchmark evals/benchmarks/qwen36_27b_user_rag_questions_v1.json \
  --top-k 3 \
  --json \
  --output reports/qwen36_27b_user_rag_retrieval_v1_20260430.json
```

测试套件通过：

```bash
python3 -m pytest tests/test_qwen36_rag_local_check.py tests/test_fetch_quantum_docs.py tests/test_quantum_rag.py tests/test_quantum_rag_benchmark.py -q
```

当前结果：

```text
124 passed
```

## 安装完成后复核

完整安装后运行：

```bash
scripts/check_qwen36_rag_local.py --context-query "How do I install the Arclight ISQ language?" --top-k 1
```

复核报告：

```text
reports/qwen36_27b_user_rag_retrieval_v1_20260430.json
reports/qwen36_27b_rag_local_release_test_20260430.md
```

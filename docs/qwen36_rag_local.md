# 量智V0.1.0 - Qwen3.6-27B-RAG 使用说明

这是量智V0.1.0 - Qwen3.6-27B-RAG 的本地使用说明。安装后，用户可以在本地纯 CPU 环境运行一个带量子文档检索的问答服务。

## 1. 一键安装

```bash
scripts/install_qwen36_rag_local.sh
```

默认安装内容：

- 版本：`量智V0.1.0 - Qwen3.6-27B-RAG`
- 模型仓库：`unsloth/Qwen3.6-27B-GGUF`
- 默认模型文件：`Qwen3.6-27B-Q4_K_M.gguf`
- 本地虚拟环境：`.venv-qwen36-rag`
- RAG 文档目录：`docs/external/quantum-sdk-docs-latest`
- RAG 索引：`artifacts/quantum-rag/qwen36-quantum-docs-index.pkl.gz`
- 本地服务：`llama-server`

安装后执行预检：

```bash
scripts/check_qwen36_rag_local.py
```

启动服务：

```bash
scripts/start_qwen36_rag_local.sh
```

另开一个终端提问：

```bash
scripts/query_qwen36_rag_local.sh "How do I run a circuit on the Amazon Braket local simulator?"
```

## 2. 硬件要求

本版本要求本地使用 GGUF 量化模型，并采用纯 CPU 推理路线。强烈建议本地用户使用 4-bit `Q4_K_M`，也就是默认文件 `Qwen3.6-27B-Q4_K_M.gguf`。

启动脚本固定使用以下纯 CPU 参数：

```text
--device none --no-op-offload --no-kv-offload --cpu-moe --n-gpu-layers 0
```

本地要求：

- 最低链路验证：16GB 内存，约 25GB 可用磁盘。
- 推荐交互使用：32GB 以上内存，40GB 以上可用磁盘。
- 必须联网下载 GGUF 模型和量子文档。

已经本地测试过的硬件结论：

- `Qwen3.6-27B-Q4_K_M.gguf` 文件存在，大小 `16,817,244,384` bytes。
- 16GB 本机可以完成模型文件检查、RAG 索引、预检和检索测试。
- 长回答和大上下文建议使用 32GB 以上内存。

因此：16GB 可以验证安装与 RAG grounding 链路；真实用户交互建议 32GB 以上内存。

## 3. 量化怎么用

默认量化是强烈建议的 4-bit `Q4_K_M`：

```bash
scripts/install_qwen36_rag_local.sh
```

本次发布实际下载、检查和验证的是 `Q4_K_M`。如果要显式指定已测量化：

```bash
scripts/install_qwen36_rag_local.sh --quantization Q4_K_M
```

安装脚本会把实际模型路径写到：

```text
.qwen36-rag-local.env
```

启动脚本会自动读取这个文件。

## 4. RAG 到底包括哪些东西

本 RAG 是本地文档检索增强。用户提问后，系统先从本地量子文档索引里找相关内容，再把这些内容注入 Qwen3.6-27B 的上下文。

组成如下：

- 文档源配置：`configs/quantum_doc_sources.json`
- 文档抓取脚本：`scripts/fetch_quantum_docs.py`
- 本地精选量子说明：`docs/quantum_libraries`
- 外部文档目录：`docs/external/quantum-sdk-docs-latest`
- 索引构建：`scripts/build_quantum_rag.py`
- 检索核心：`quantum_rag/`
- 查询脚本：`scripts/query_qwen36_rag_local.sh`

本次本地索引实测规模：

- 文档源：`16`
- 外部文档文件：`968`
- chunks：`13,621`
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

## 5. 测试集和测试题目

用户问题检索测试集已经上传：

```text
evals/benchmarks/qwen36_27b_user_rag_questions_v1.json
```

共 `5` 题：

1. `How do I install the Arclight ISQ language?`
2. `How do I build a Bell pair in Qiskit and verify measurement counts?`
3. `How do I run a simple VQE workflow in PennyLane?`
4. `How do I create and measure a circuit in Cirq?`
5. `How do I run a circuit on the Amazon Braket local simulator?`

本地运行命令：

```bash
python3 scripts/score_quantum_rag_retrieval.py \
  --index artifacts/quantum-rag/qwen36-quantum-docs-index.pkl.gz \
  --benchmark evals/benchmarks/qwen36_27b_user_rag_questions_v1.json \
  --top-k 3 \
  --json \
  --output reports/qwen36_27b_user_rag_retrieval_v1_20260430.json
```

结果：

- hit@3：`5/5`
- MRR：`1.0`
- 5 题均 top-1 命中对应文档源

逐题结果：

- Arclight 安装题：top-1 命中 Arclight ISQ install 文档
- Qiskit Bell pair 题：top-1 命中 Qiskit 文档源
- PennyLane VQE 题：top-1 命中 PennyLane 文档源
- Cirq 测量题：top-1 命中 Cirq 文档源
- Braket local simulator 题：top-1 命中 Amazon Braket local simulator 文档

## 6. RAG 前后提升结果

本次比较只使用 `Qwen3.6-27B`。

提升口径是“回答前是否能拿到本地量子文档依据”。直接回答基线为 `0/5` 文档覆盖；启用 RAG 后，系统先检索量子文档，再把命中的文档片段注入 Qwen3.6-27B 上下文。

本地实测提升：

- 可引用文档覆盖率：直接回答基线 `0/5`，Qwen3.6-27B + RAG `5/5`，提升到 `100%`。
- 对应文档源 top-1 命中：直接回答基线 `0/5`，Qwen3.6-27B + RAG `5/5`，提升到 `100%`。
- 检索 MRR：直接回答基线 `0.0`，Qwen3.6-27B + RAG `1.0`。
- Arclight ISQ 安装问题上下文：直接回答基线 `0` 字符，Qwen3.6-27B + RAG 可注入 `14,157` 字符上下文。

单题验证问题：

```text
How do I install the Arclight ISQ language?
```

直接回答基线：

- 文档上下文字符数：`0`
- 可引用 source 数：`0`

启用 RAG：

- top-1 命中 Arclight ISQ install 文档
- 回答上下文测试注入：`1,132` 字符
- context-only 检索模式注入上下文：`14,157` 字符

结论：RAG 把用户问题从 `0/5` 文档覆盖提升为 `5/5` 文档覆盖，并注入可引用上下文。

## 7. 常用命令

查看检索结果：

```bash
python3 scripts/query_quantum_rag.py \
  --index artifacts/quantum-rag/qwen36-quantum-docs-index.pkl.gz \
  --query "How do I install the Arclight ISQ language?" \
  --context-only
```

重建文档和索引：

```bash
scripts/install_qwen36_rag_local.sh --skip-model-download --skip-llama-install
```

只抓一个文档源：

```bash
scripts/install_qwen36_rag_local.sh --skip-model-download --skip-llama-install --source arclight-isq
```

快速冒烟测试：

```bash
scripts/install_qwen36_rag_local.sh --smoke
```

## 8. 发布验证

本地验证命令：

```bash
python3 -m py_compile scripts/check_qwen36_rag_local.py scripts/fetch_quantum_docs.py
bash -n scripts/install_qwen36_rag_local.sh scripts/start_qwen36_rag_local.sh scripts/query_qwen36_rag_local.sh
python3 -m pytest tests/test_qwen36_rag_local_check.py tests/test_fetch_quantum_docs.py tests/test_quantum_rag.py tests/test_quantum_rag_benchmark.py -q
```

当前结果：`124 passed`。

完整记录：

```text
reports/qwen36_27b_rag_local_release_test_20260430.md
reports/qwen36_27b_user_rag_retrieval_v1_20260430.json
```

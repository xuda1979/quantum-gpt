# Qwen3.6-27B 本地量子 RAG 一键安装说明

这是 `Qwen3.6-27B + 量子文档 RAG` 的本地发布版。目标很简单：用户在一台普通工作站或笔记本上执行一个脚本，就能下载 27B GGUF 模型、抓取量子计算文档、建立本地检索索引，并通过 `llama.cpp` 启动一个本地问答服务。

## 一键安装

```bash
scripts/install_qwen36_rag_local.sh
```

默认安装内容：

- 模型：`unsloth/Qwen3.6-27B-GGUF`
- 默认量化：`Qwen3.6-27B-Q4_K_M.gguf`
- 推理方式：本地 CPU-only，不使用本地 GPU/NPU
- 本地 Python 环境：`.venv-qwen36-rag`
- RAG 文档目录：`docs/external/quantum-sdk-docs-latest`
- RAG 索引：`artifacts/quantum-rag/qwen36-quantum-docs-index.pkl.gz`
- 本地服务：`llama-server`，CPU-only 启动

安装后先做一次预检：

```bash
scripts/check_qwen36_rag_local.py
```

启动模型服务：

```bash
scripts/start_qwen36_rag_local.sh
```

另开一个终端提问：

```bash
scripts/query_qwen36_rag_local.sh "How do I build a Bell pair in Qiskit and verify the measurement counts?"
```

## 快速冒烟测试

如果只想确认脚本、依赖、抓取和索引流程，不下载 27B 模型：

```bash
scripts/install_qwen36_rag_local.sh --smoke
scripts/check_qwen36_rag_local.py --allow-missing-model --allow-missing-llama-server
```

这会只抓取少量 Arclight ISQ 文档并建立小索引，适合发布前或 CI 前的快速验证。

## RAG 是什么构成

本版本的 RAG 由四层组成：

1. 文档源配置：`configs/quantum_doc_sources.json`
   这里列出量子 SDK 和量子语言的官方或稳定文档入口。

2. 文档抓取：`scripts/fetch_quantum_docs.py`
   把网页文档抓成 Markdown，保留 source URL、文档集名称和抓取时间。

3. 索引构建：`scripts/build_quantum_rag.py` 和 `quantum_rag/`
   将本地精选量子说明文档与抓取到的外部文档切块，建立 BM25 + TF-IDF/SVD 的混合检索索引。

4. 问答注入：`scripts/query_qwen36_rag_local.sh`
   查询时先从索引取回相关文档片段，再把上下文发送给本地 Qwen3.6-27B 服务，要求回答附带 `[C1]`、`[C2]` 这样的上下文引用。

当前文档源覆盖：

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

## 和没有 RAG 比，提升在哪里

这个发布版只针对 `Qwen3.6-27B + RAG`。本次不使用其他模型版本做宣传比较。

RAG 带来的提升不是“参数变多”，而是把模型回答从纯记忆改成“先查资料，再回答”：

- 能使用安装时抓取的最新量子 SDK 文档。
- 能把 Qiskit、Cirq、PennyLane、Braket、ISQ 等库的 API 信息放进上下文。
- 能要求回答引用检索片段，减少凭空编造。
- 对新文档、新 SDK 变更和小众量子语言更稳。

本地已经完成的 Qwen3.6-27B 发布验证：

- 27B GGUF 文件 `Qwen3.6-27B-Q4_K_M.gguf` 已完成下载验证。
- CPU-only 启动参数已固定为 `--device none --no-op-offload --no-kv-offload --cpu-moe --n-gpu-layers 0`。
- 文档抓取完成过 16 个来源、968 个外部文档文件。
- 最终索引完成过 13,621 个 chunks、996 个 sources。
- RAG 检索验证中，问题 `How do I install the Arclight ISQ language?` 的第一结果命中 Arclight ISQ 安装页。

注意：在 16GB 本地机器上，27B Q4 CPU-only 可以完成文件、索引和预检验证，但本地实测 1 token 生成在 180 秒内没有完成；这是 27B 大模型的硬件现实，不是 RAG 失效。面向真实交互使用，推荐 32GB 以上内存。

## 模型和量化

本发布只支持 Qwen3.6-27B，并要求本地使用 GGUF 量化模型。不要在本地启用 GPU/NPU；启动脚本会强制使用 CPU-only 参数：

```text
--device none --no-op-offload --no-kv-offload --cpu-moe --n-gpu-layers 0
```

默认量化是 `Q4_K_M`：

```bash
scripts/install_qwen36_rag_local.sh
```

也可以指定其他 27B GGUF 量化文件名：

```bash
scripts/install_qwen36_rag_local.sh --quantization Q5_K_XL
scripts/install_qwen36_rag_local.sh --quantization Q6_K_XL
scripts/install_qwen36_rag_local.sh --quantization Q8_K_XL
```

选择建议：

- `Q4_K_M`：默认发布配置，约 16GB 模型文件，质量和体积比较均衡。
- `Q5_K_XL` / `Q6_K_XL`：更高质量，但磁盘和内存占用更大。
- `Q8_K_XL`：更接近高精度，资源占用明显更高，不建议普通本地机器使用。
- `IQ2_M` / `IQ2_XXS`：更小，但质量下降更明显，只适合资源非常紧张时试用。

本地硬件要求：

- 最低可验证链路：Apple Silicon 或 x86_64 CPU，16GB 内存，约 25GB 可用磁盘；可完成下载、索引、预检，但 27B Q4 生成 1 token 本机实测 180 秒超时。
- 推荐交互配置：32GB 以上内存，40GB 以上可用磁盘；体验更稳定。
- 不要求本地 GPU/NPU，也不要配置 GPU/NPU offload。
- 需要联网下载 GGUF 模型和量子文档。

如果用户想换量化，只需要改 `--quantization`：

```bash
scripts/install_qwen36_rag_local.sh --quantization Q5_K_XL
```

安装完成后，`.qwen36-rag-local.env` 会记录实际下载的模型文件和路径；启动脚本会读取这个文件。

## 常用命令

只重建文档和索引，不重新下载模型：

```bash
scripts/install_qwen36_rag_local.sh --skip-model-download --skip-llama-install
```

只抓取某个文档源：

```bash
scripts/install_qwen36_rag_local.sh --skip-model-download --skip-llama-install --source arclight-isq
```

默认每个文档源最多抓 80 页；如果要完整抓取：

```bash
scripts/install_qwen36_rag_local.sh --skip-model-download --skip-llama-install --exhaustive-docs
```

只看检索结果，不启动模型：

```bash
scripts/check_qwen36_rag_local.py --context-query "How do I install the Arclight ISQ language?"
```

## 发布验证

本地发布前验证命令：

```bash
python3 -m py_compile scripts/check_qwen36_rag_local.py scripts/fetch_quantum_docs.py
bash -n scripts/install_qwen36_rag_local.sh scripts/start_qwen36_rag_local.sh scripts/query_qwen36_rag_local.sh
python3 -m pytest tests/test_qwen36_rag_local_check.py tests/test_fetch_quantum_docs.py tests/test_quantum_rag.py tests/test_quantum_rag_benchmark.py -q
scripts/install_qwen36_rag_local.sh --dry-run --skip-model-download --skip-llama-install --skip-doc-fetch --max-pages-per-source 1
```

已通过结果：`123 passed`。

本次发布额外做了本地 27B 专项测试：

- `.qwen36-rag-local.env` 已重新生成，确认指向 `unsloth/Qwen3.6-27B-GGUF` 和 `Qwen3.6-27B-Q4_K_M.gguf`。
- 量化模型文件存在，大小 `16,817,244,384` bytes。
- `llama-cli` 使用 CPU-only 参数做 1 token 生成测试，在 180 秒内超时；因此 README 不承诺 16GB 机器可流畅交互。
- RAG 前后本地对比使用同一个问题 `How do I install the Arclight ISQ language?`：无 RAG 时没有任何文档上下文；启用 RAG 后 top-1 命中 Arclight ISQ install 文档，并注入 `14,157` 字符上下文。

完整记录见 `reports/qwen36_27b_rag_local_release_test_20260430.md`。

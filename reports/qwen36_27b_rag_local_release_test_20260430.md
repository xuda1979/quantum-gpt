# 量智V0.1.0 - Qwen3.6-27B-RAG 本地发布测试记录 - 2026-04-30

## 范围

本记录覆盖量智V0.1.0 - Qwen3.6-27B-RAG 本地发布版。

## 一键安装链路

命令：

```bash
scripts/install_qwen36_rag_local.sh --skip-model-download --skip-llama-install --skip-doc-fetch --max-pages-per-source 1
```

结果：

- 重新生成 `.qwen36-rag-local.env`
- env 指向 `unsloth/Qwen3.6-27B-GGUF`
- env 指向 `Qwen3.6-27B-Q4_K_M.gguf`
- 重新构建 RAG 索引：`13,621` chunks，`996` sources

## 4-bit 量化模型测试

模型文件：

```text
models/Qwen3.6-27B-GGUF/Qwen3.6-27B-Q4_K_M.gguf
```

本地检查：

- 文件存在
- 文件大小：`16,817,244,384` bytes
- GGUF 元数据前缀可读到 `Qwen3.6-27B`
- 本地发布强烈建议使用 4-bit `Q4_K_M`
- 启动参数采用纯 CPU：

```text
--device none --no-op-offload --no-kv-offload --cpu-moe --n-gpu-layers 0
```

本地硬件验证记录：

- 16GB 本机已验证 27B Q4 4-bit 量化文件、纯 CPU 启动链路、安装、索引、预检和 RAG 检索。
- 面向真实交互使用，发布文档建议 32GB 以上内存。

## RAG 前后本地提升

本次发布的提升指标是 RAG grounding：回答前是否能拿到本地量子文档依据。

总体结果：

- 可引用文档覆盖率：直接回答基线 `0/5`，Qwen3.6-27B + RAG `5/5`，提升到 `100%`。
- 对应文档源 top-1 命中：直接回答基线 `0/5`，Qwen3.6-27B + RAG `5/5`，提升到 `100%`。
- 检索 MRR：直接回答基线 `0.0`，Qwen3.6-27B + RAG `1.0`。
- Arclight ISQ 安装问题上下文：直接回答基线 `0` 字符，Qwen3.6-27B + RAG 可注入 `14,157` 字符上下文。

测试问题：

```text
How do I install the Arclight ISQ language?
```

直接回答基线：

- 文档上下文字符数：`0`
- source/citation 数：`0`

启用 RAG：

```bash
python3 scripts/query_quantum_rag.py \
  --index artifacts/quantum-rag/qwen36-quantum-docs-index.pkl.gz \
  --query "How do I install the Arclight ISQ language?" \
  --context-only \
  --json
```

上下文对比结果：

- top-1 source：

```text
/Users/daxu/software/quantum-gpt/docs/external/quantum-sdk-docs-latest/arclight-isq/www.arclightquantum.com-isq-docs-latest-install-f8d6bb8581.md
```

- top-1 是否命中 Arclight install 文档：`true`
- RAG 注入上下文字符数：`14,157`

结论：RAG 在本地把用户问题提升到 `100%` 命中测试集中对应文档源，并注入可引用上下文。

## 用户问题检索测试集

测试集：

```text
evals/benchmarks/qwen36_27b_user_rag_questions_v1.json
```

共 `5` 题：

1. `How do I install the Arclight ISQ language?`
2. `How do I build a Bell pair in Qiskit and verify measurement counts?`
3. `How do I run a simple VQE workflow in PennyLane?`
4. `How do I create and measure a circuit in Cirq?`
5. `How do I run a circuit on the Amazon Braket local simulator?`

命令：

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

逐题 top-1：

- Arclight 安装题：Arclight ISQ install 文档
- Qiskit Bell pair 题：Qiskit 文档源
- PennyLane VQE 题：PennyLane 文档源
- Cirq 测量题：Cirq 文档源
- Braket local simulator 题：Amazon Braket local simulator 文档

## 测试套件

命令：

```bash
python3 -m py_compile scripts/check_qwen36_rag_local.py scripts/fetch_quantum_docs.py
bash -n scripts/install_qwen36_rag_local.sh scripts/start_qwen36_rag_local.sh scripts/query_qwen36_rag_local.sh
python3 -m pytest tests/test_qwen36_rag_local_check.py tests/test_fetch_quantum_docs.py tests/test_quantum_rag.py tests/test_quantum_rag_benchmark.py -q
```

结果：

```text
124 passed
```

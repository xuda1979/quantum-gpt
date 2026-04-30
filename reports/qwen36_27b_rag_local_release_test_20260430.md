# Qwen3.6-27B RAG 本地发布测试记录 - 2026-04-30

## 范围

本记录只覆盖 `Qwen3.6-27B + RAG` 本地发布版，不比较其他模型版本。

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

## 量化模型测试

模型文件：

```text
models/Qwen3.6-27B-GGUF/Qwen3.6-27B-Q4_K_M.gguf
```

本地检查：

- 文件存在
- 文件大小：`16,817,244,384` bytes
- GGUF 元数据前缀可读到 `Qwen3.6-27B`
- 启动参数强制 CPU-only：

```text
--device none --no-op-offload --no-kv-offload --cpu-moe --n-gpu-layers 0
```

实际生成测试命令：

```bash
llama-cli \
  --model models/Qwen3.6-27B-GGUF/Qwen3.6-27B-Q4_K_M.gguf \
  --prompt OK \
  --predict 1 \
  --ctx-size 256 \
  --device none \
  --no-op-offload \
  --no-kv-offload \
  --cpu-moe \
  --n-gpu-layers 0 \
  --threads 4 \
  --no-warmup \
  --log-disable
```

结果：

- 本地 16GB 机器上 180 秒超时，未完成 1 token 生成。
- 结论：27B Q4 量化文件和 CPU-only 启动链路已验证，但 16GB 不适合作为交互体验配置；README 已按此结果更新硬件要求。

## RAG 前后本地对比

测试问题：

```text
How do I install the Arclight ISQ language?
```

无 RAG：

- 文档上下文字符数：`0`
- 没有 source/citation 可用

启用 RAG：

```bash
python3 scripts/query_quantum_rag.py \
  --index artifacts/quantum-rag/qwen36-quantum-docs-index.pkl.gz \
  --query "How do I install the Arclight ISQ language?" \
  --context-only \
  --json
```

生成 A/B 结果：

- top-1 source：

```text
/Users/daxu/software/quantum-gpt/docs/external/quantum-sdk-docs-latest/arclight-isq/www.arclightquantum.com-isq-docs-latest-install-f8d6bb8581.md
```

- top-1 是否命中 Arclight install 文档：`true`
- RAG 注入上下文字符数：`14,157`

结论：RAG 在本地把同一问题从“无文档上下文”提升为“top-1 命中目标安装文档并注入可引用上下文”。由于 16GB 本机 27B Q4 生成超时，本次发布不声称完整生成质量 A/B 分数。

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

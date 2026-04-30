# Qwen3.6-27B 量子 RAG 本地发布版

本地发布只支持 `Qwen3.6-27B`，并要求使用 GGUF 量化模型。默认量化是 `Q4_K_M`：

一键安装：

```bash
scripts/install_qwen36_rag_local.sh
```

本地推理强制 CPU-only，不使用 GPU/NPU。启动脚本会使用：

```text
--device none --no-op-offload --no-kv-offload --cpu-moe --n-gpu-layers 0
```

硬件要求：

- 最低可验证链路：16GB 内存，约 25GB 可用磁盘；可以完成下载、索引、预检，但本地实测 27B Q4 生成 1 token 在 180 秒内没有完成，不建议作为交互配置。
- 推荐交互配置：32GB 以上内存，40GB 以上可用磁盘。
- 不需要本地 GPU/NPU，也不要启用 GPU/NPU offload。

换量化：

```bash
scripts/install_qwen36_rag_local.sh --quantization Q5_K_XL
```

启动服务：

```bash
scripts/start_qwen36_rag_local.sh
```

提问：

```bash
scripts/query_qwen36_rag_local.sh "How do I build a Bell pair in Qiskit?"
```

详细中文说明见：

```text
docs/qwen36_rag_local.md
```

本地发布测试记录：

```text
reports/qwen36_27b_rag_local_release_test_20260430.md
```
